"""
API dependencies for authentication and authorization.
"""

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import security
from app.db.database import get_db
from app.models.user import User
from app.services.user_service import UserService


# Security scheme
security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify access token
    payload = security.verify_token(credentials.credentials, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_service = UserService(db)
    user = user_service.get_user_by_id(uuid.UUID(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is locked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_superadmin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current superadmin user."""
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return current_user


def require_permission(permission: str):
    """Dependency factory for permission-based access control."""
    def permission_dependency(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return permission_dependency


def require_role(allowed_roles: list[str]):
    """Dependency factory for role-based access control."""
    def role_dependency(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role must be one of: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_dependency


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None
    
    try:
        # Verify access token
        payload = security.verify_token(credentials.credentials, "access")
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Get user from database
        user_service = UserService(db)
        user = user_service.get_user_by_id(uuid.UUID(user_id))
        
        if not user or not user.is_active or user.is_locked:
            return None
        
        return user
    except Exception:
        return None


def get_request_info(request: Request) -> dict:
    """Get request information for logging."""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers)
    }


class PermissionChecker:
    """Permission checker class for complex permission logic."""
    
    def __init__(self, user: User):
        self.user = user
    
    def can_manage_user(self, target_user: User) -> bool:
        """Check if user can manage target user."""
        # Superadmin can manage all users except other superadmins
        if self.user.is_superadmin:
            return target_user.role != "superadmin" or target_user.id == self.user.id
        
        # Admin users can only manage regular users
        if self.user.is_admin:
            return target_user.role == "user"
        
        # Regular users can only manage themselves
        return target_user.id == self.user.id
    
    def can_view_user(self, target_user: User) -> bool:
        """Check if user can view target user."""
        # Superadmin can view all users
        if self.user.is_superadmin:
            return True
        
        # Admin users can view regular users and themselves
        if self.user.is_admin:
            return target_user.role == "user" or target_user.id == self.user.id
        
        # Regular users can only view themselves
        return target_user.id == self.user.id
    
    def can_assign_role(self, target_role: str) -> bool:
        """Check if user can assign specific role."""
        # Only superadmin can assign admin roles
        if target_role in ["superadmin", "admin1", "admin2", "admin3"]:
            return self.user.is_superadmin
        
        # Admin users can assign user role
        if target_role == "user":
            return self.user.is_admin
        
        return False
    
    def can_access_audit_logs(self) -> bool:
        """Check if user can access audit logs."""
        return self.user.has_permission("view_audit_logs")
    
    def can_view_analytics(self) -> bool:
        """Check if user can view analytics."""
        return self.user.has_permission("view_analytics")


def get_permission_checker(
    current_user: User = Depends(get_current_user)
) -> PermissionChecker:
    """Get permission checker for current user."""
    return PermissionChecker(current_user)

