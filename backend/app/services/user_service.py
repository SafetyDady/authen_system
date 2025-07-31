"""
User service layer for business logic.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.core.config import settings
from app.core.security import security
from app.db.database import get_db
from app.models.user import User, UserSession, AuditLog, PasswordReset
from app.schemas.user import (
    UserCreate, UserUpdate, UserUpdateProfile, PasswordChange,
    PasswordReset as PasswordResetSchema, UserSearchParams, UserStats
)


class UserService:
    """User service for managing user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(
        self, 
        user_create: UserCreate, 
        created_by: Optional[User] = None
    ) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = self.get_user_by_email(user_create.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Validate password strength
        password_validation = security.validate_password_strength(user_create.password)
        if not password_validation["is_valid"]:
            raise ValueError(f"Password validation failed: {', '.join(password_validation['errors'])}")
        
        # Create user
        user = User(
            email=user_create.email.lower(),
            password_hash=security.get_password_hash(user_create.password),
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            role=user_create.role,
            is_active=user_create.is_active,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Log user creation
        self.log_audit_action(
            action="user_created",
            resource="user",
            resource_id=str(user.id),
            user=created_by,
            new_values=json.dumps({
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
            })
        )
        
        return user
    
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email.lower()).first()
    
    def update_user(
        self, 
        user_id: uuid.UUID, 
        user_update: UserUpdate, 
        updated_by: Optional[User] = None
    ) -> Optional[User]:
        """Update user information."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Store old values for audit log
        old_values = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_active": user.is_active,
        }
        
        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        # Log user update
        new_values = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_active": user.is_active,
        }
        
        self.log_audit_action(
            action="user_updated",
            resource="user",
            resource_id=str(user.id),
            user=updated_by,
            old_values=json.dumps(old_values),
            new_values=json.dumps(new_values)
        )
        
        return user
    
    def update_user_profile(
        self, 
        user_id: uuid.UUID, 
        profile_update: UserUpdateProfile
    ) -> Optional[User]:
        """Update user's own profile."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Store old values for audit log
        old_values = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_url": user.avatar_url,
        }
        
        # Update fields
        update_data = profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        # Log profile update
        new_values = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_url": user.avatar_url,
        }
        
        self.log_audit_action(
            action="profile_updated",
            resource="user",
            resource_id=str(user.id),
            user=user,
            old_values=json.dumps(old_values),
            new_values=json.dumps(new_values)
        )
        
        return user
    
    def change_password(
        self, 
        user_id: uuid.UUID, 
        password_change: PasswordChange
    ) -> bool:
        """Change user password."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not security.verify_password(password_change.current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Validate new password strength
        password_validation = security.validate_password_strength(password_change.new_password)
        if not password_validation["is_valid"]:
            raise ValueError(f"Password validation failed: {', '.join(password_validation['errors'])}")
        
        # Update password
        user.password_hash = security.get_password_hash(password_change.new_password)
        user.password_changed_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        # Invalidate all user sessions except current one
        self.db.query(UserSession).filter(
            UserSession.user_id == user_id
        ).update({"is_active": False})
        
        self.db.commit()
        
        # Log password change
        self.log_audit_action(
            action="password_changed",
            resource="user",
            resource_id=str(user.id),
            user=user
        )
        
        return True
    
    def delete_user(self, user_id: uuid.UUID, deleted_by: Optional[User] = None) -> bool:
        """Delete user (soft delete by deactivating)."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Soft delete by deactivating
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        # Invalidate all user sessions
        self.db.query(UserSession).filter(
            UserSession.user_id == user_id
        ).update({"is_active": False})
        
        self.db.commit()
        
        # Log user deletion
        self.log_audit_action(
            action="user_deleted",
            resource="user",
            resource_id=str(user.id),
            user=deleted_by
        )
        
        return True
    
    def search_users(self, search_params: UserSearchParams) -> Tuple[List[User], int]:
        """Search users with pagination and filters."""
        query = self.db.query(User)
        
        # Apply filters
        if search_params.search:
            search_term = f"%{search_params.search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
                )
            )
        
        if search_params.role:
            query = query.filter(User.role == search_params.role)
        
        if search_params.is_active is not None:
            query = query.filter(User.is_active == search_params.is_active)
        
        if search_params.is_verified is not None:
            query = query.filter(User.is_verified == search_params.is_verified)
        
        if search_params.is_locked is not None:
            query = query.filter(User.is_locked == search_params.is_locked)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if search_params.sort_by == "email":
            order_column = User.email
        elif search_params.sort_by == "first_name":
            order_column = User.first_name
        elif search_params.sort_by == "last_name":
            order_column = User.last_name
        elif search_params.sort_by == "role":
            order_column = User.role
        elif search_params.sort_by == "last_login":
            order_column = User.last_login
        else:
            order_column = User.created_at
        
        if search_params.sort_order == "desc":
            order_column = desc(order_column)
        
        query = query.order_by(order_column)
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.size
        users = query.offset(offset).limit(search_params.size).all()
        
        return users, total
    
    def get_user_stats(self) -> UserStats:
        """Get user statistics."""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        verified_users = self.db.query(User).filter(User.is_verified == True).count()
        locked_users = self.db.query(User).filter(User.is_locked == True).count()
        
        # Users by role
        role_counts = self.db.query(
            User.role, func.count(User.id)
        ).group_by(User.role).all()
        users_by_role = {role: count for role, count in role_counts}
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = self.db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        # Recent logins (last 30 days)
        recent_logins = self.db.query(User).filter(
            and_(
                User.last_login >= thirty_days_ago,
                User.last_login.isnot(None)
            )
        ).count()
        
        return UserStats(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            locked_users=locked_users,
            users_by_role=users_by_role,
            recent_registrations=recent_registrations,
            recent_logins=recent_logins
        )
    
    def lock_user(self, user_id: uuid.UUID, locked_by: Optional[User] = None) -> bool:
        """Lock user account."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_locked = True
        user.locked_until = None  # Permanent lock until manually unlocked
        user.updated_at = datetime.utcnow()
        
        # Invalidate all user sessions
        self.db.query(UserSession).filter(
            UserSession.user_id == user_id
        ).update({"is_active": False})
        
        self.db.commit()
        
        # Log user lock
        self.log_audit_action(
            action="user_locked",
            resource="user",
            resource_id=str(user.id),
            user=locked_by
        )
        
        return True
    
    def unlock_user(self, user_id: uuid.UUID, unlocked_by: Optional[User] = None) -> bool:
        """Unlock user account."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_locked = False
        user.locked_until = None
        user.failed_login_attempts = 0
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Log user unlock
        self.log_audit_action(
            action="user_unlocked",
            resource="user",
            resource_id=str(user.id),
            user=unlocked_by
        )
        
        return True
    
    def log_audit_action(
        self,
        action: str,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        user: Optional[User] = None,
        old_values: Optional[str] = None,
        new_values: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log audit action."""
        audit_log = AuditLog(
            user_id=user.id if user else None,
            action=action,
            resource=resource,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        self.db.commit()
    
    def get_audit_logs(
        self, 
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[AuditLog], int]:
        """Get audit logs with pagination and filters."""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource:
            query = query.filter(AuditLog.resource == resource)
        
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * size
        audit_logs = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(size).all()
        
        return audit_logs, total


def get_user_service(db: Session = next(get_db())) -> UserService:
    """Get user service instance."""
    return UserService(db)

