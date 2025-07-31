"""
Authentication service for login, logout, and token management.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.config import settings
from app.core.security import security
from app.db.database import get_db
from app.models.user import User, UserSession, PasswordReset
from app.schemas.user import LoginRequest, PasswordReset as PasswordResetSchema
from app.services.user_service import UserService


class AuthService:
    """Authentication service for managing user authentication."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
    
    def authenticate_user(
        self, 
        login_request: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate user with email and password.
        
        Returns:
            Tuple of (User, error_message)
        """
        user = self.user_service.get_user_by_email(login_request.email)
        
        if not user:
            return None, "Invalid email or password"
        
        # Check if account is locked
        if user.is_locked:
            if user.locked_until and datetime.utcnow() < user.locked_until:
                remaining_time = user.locked_until - datetime.utcnow()
                return None, f"Account is locked. Try again in {remaining_time.seconds // 60} minutes"
            elif user.locked_until is None:
                return None, "Account is permanently locked. Contact administrator"
        
        # Check if account is active
        if not user.is_active:
            return None, "Account is deactivated"
        
        # Verify password
        if not security.verify_password(login_request.password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account if max attempts reached
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.is_locked = True
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.LOCKOUT_DURATION_MINUTES
                )
                
                # Log account lockout
                self.user_service.log_audit_action(
                    action="account_locked_failed_attempts",
                    resource="user",
                    resource_id=str(user.id),
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            
            self.db.commit()
            
            # Log failed login attempt
            self.user_service.log_audit_action(
                action="login_failed",
                resource="user",
                resource_id=str(user.id),
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                new_values=json.dumps({"reason": "invalid_password"})
            )
            
            return None, "Invalid email or password"
        
        # Reset failed login attempts on successful authentication
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            
        # Unlock account if it was temporarily locked
        if user.is_locked and user.locked_until and datetime.utcnow() >= user.locked_until:
            user.is_locked = False
            user.locked_until = None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Log successful login
        self.user_service.log_audit_action(
            action="login_successful",
            resource="user",
            resource_id=str(user.id),
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return user, None
    
    def create_user_session(
        self,
        user: User,
        remember_me: bool = False,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Create user session and return access and refresh tokens.
        
        Returns:
            Tuple of (access_token, refresh_token)
        """
        # Create refresh token
        refresh_token_expires = timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS * (2 if remember_me else 1)
        )
        refresh_token = security.create_refresh_token(
            subject=str(user.id),
            expires_delta=refresh_token_expires
        )
        
        # Create user session
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + refresh_token_expires
        )
        
        self.db.add(session)
        self.db.commit()
        
        # Create access token with user info
        access_token = security.create_access_token(
            subject=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role,
                "session_id": str(session.id)
            }
        )
        
        return access_token, refresh_token
    
    def refresh_access_token(
        self, 
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Refresh access token using refresh token.
        
        Returns:
            Tuple of (access_token, error_message)
        """
        # Verify refresh token
        payload = security.verify_token(refresh_token, "refresh")
        if not payload:
            return None, "Invalid or expired refresh token"
        
        user_id = payload.get("sub")
        if not user_id:
            return None, "Invalid refresh token"
        
        # Get user session
        session = self.db.query(UserSession).filter(
            and_(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            )
        ).first()
        
        if not session or session.is_expired:
            return None, "Invalid or expired refresh token"
        
        # Get user
        user = self.user_service.get_user_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            return None, "User not found or inactive"
        
        # Update session last used
        session.refresh()
        self.db.commit()
        
        # Create new access token
        access_token = security.create_access_token(
            subject=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role,
                "session_id": str(session.id)
            }
        )
        
        # Log token refresh
        self.user_service.log_audit_action(
            action="token_refreshed",
            resource="user",
            resource_id=str(user.id),
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return access_token, None
    
    def logout_user(
        self,
        user: User,
        refresh_token: Optional[str] = None,
        logout_all_devices: bool = False,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Logout user by invalidating sessions."""
        if logout_all_devices:
            # Invalidate all user sessions
            self.db.query(UserSession).filter(
                UserSession.user_id == user.id
            ).update({"is_active": False})
            
            action = "logout_all_devices"
        else:
            # Invalidate specific session
            if refresh_token:
                self.db.query(UserSession).filter(
                    and_(
                        UserSession.user_id == user.id,
                        UserSession.refresh_token == refresh_token
                    )
                ).update({"is_active": False})
            else:
                # Invalidate all sessions if no specific token provided
                self.db.query(UserSession).filter(
                    UserSession.user_id == user.id
                ).update({"is_active": False})
            
            action = "logout"
        
        self.db.commit()
        
        # Log logout
        self.user_service.log_audit_action(
            action=action,
            resource="user",
            resource_id=str(user.id),
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return True
    
    def request_password_reset(
        self,
        password_reset_request: PasswordResetSchema,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Request password reset."""
        user = self.user_service.get_user_by_email(password_reset_request.email)
        if not user:
            # Don't reveal if email exists
            return True
        
        # Check if user is active
        if not user.is_active:
            return True
        
        # Generate reset token
        reset_token = security.generate_password_reset_token(user.email)
        
        # Create password reset record
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(password_reset)
        self.db.commit()
        
        # Log password reset request
        self.user_service.log_audit_action(
            action="password_reset_requested",
            resource="user",
            resource_id=str(user.id),
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # TODO: Send password reset email
        # email_service.send_password_reset_email(user.email, reset_token)
        
        return True
    
    def reset_password(
        self,
        token: str,
        new_password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Reset password using reset token."""
        # Verify reset token
        email = security.verify_password_reset_token(token)
        if not email:
            return False, "Invalid or expired reset token"
        
        # Get password reset record
        password_reset = self.db.query(PasswordReset).filter(
            and_(
                PasswordReset.token == token,
                PasswordReset.is_used == False
            )
        ).first()
        
        if not password_reset or not password_reset.is_valid:
            return False, "Invalid or expired reset token"
        
        # Get user
        user = self.user_service.get_user_by_email(email)
        if not user:
            return False, "User not found"
        
        # Validate new password strength
        password_validation = security.validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            return False, f"Password validation failed: {', '.join(password_validation['errors'])}"
        
        # Update password
        user.password_hash = security.get_password_hash(new_password)
        user.password_changed_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        # Mark reset token as used
        password_reset.is_used = True
        password_reset.used_at = datetime.utcnow()
        
        # Invalidate all user sessions
        self.db.query(UserSession).filter(
            UserSession.user_id == user.id
        ).update({"is_active": False})
        
        self.db.commit()
        
        # Log password reset
        self.user_service.log_audit_action(
            action="password_reset_completed",
            resource="user",
            resource_id=str(user.id),
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return True, None
    
    def get_user_sessions(self, user_id: uuid.UUID) -> list[UserSession]:
        """Get active user sessions."""
        return self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).order_by(UserSession.last_used_at.desc()).all()
    
    def revoke_session(
        self,
        user: User,
        session_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Revoke specific user session."""
        session = self.db.query(UserSession).filter(
            and_(
                UserSession.id == session_id,
                UserSession.user_id == user.id,
                UserSession.is_active == True
            )
        ).first()
        
        if not session:
            return False
        
        session.is_active = False
        self.db.commit()
        
        # Log session revocation
        self.user_service.log_audit_action(
            action="session_revoked",
            resource="session",
            resource_id=str(session.id),
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        expired_count = self.db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).update({"is_active": False})
        
        self.db.commit()
        return expired_count


def get_auth_service(db: Session = next(get_db())) -> AuthService:
    """Get authentication service instance."""
    return AuthService(db)

