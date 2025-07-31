"""
User model and related database tables.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile fields
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    
    # Role and permissions
    role = Column(
        Enum(
            "superadmin", 
            "admin1", 
            "admin2", 
            "admin3", 
            "user", 
            name="user_roles"
        ),
        default="user",
        nullable=False,
        index=True
    )
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Account lockout
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Email verification
    email_verification_token = Column(String(255), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role in ["superadmin", "admin1", "admin2", "admin3"]
    
    @property
    def is_superadmin(self) -> bool:
        """Check if user is superadmin."""
        return self.role == "superadmin"
    
    def can_manage_role(self, target_role: str) -> bool:
        """Check if user can manage users with target role."""
        if self.role == "superadmin":
            return target_role in ["admin1", "admin2", "admin3", "user"]
        elif self.role in ["admin1", "admin2", "admin3"]:
            return target_role == "user"
        return False
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        role_permissions = {
            "superadmin": [
                "manage_admins",
                "manage_users", 
                "view_audit_logs",
                "manage_system_settings",
                "view_analytics",
                "manage_roles"
            ],
            "admin1": [
                "manage_users",
                "view_audit_logs",
                "view_analytics"
            ],
            "admin2": [
                "manage_users",
                "view_audit_logs",
                "view_analytics"
            ],
            "admin3": [
                "manage_users",
                "view_audit_logs",
                "view_analytics"
            ],
            "user": [
                "view_profile",
                "update_profile"
            ]
        }
        
        return permission in role_permissions.get(self.role, [])


class UserSession(Base):
    """User session model for tracking active sessions."""
    
    __tablename__ = "user_sessions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session data
    refresh_token = Column(String(500), unique=True, nullable=False, index=True)
    device_info = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, ip={self.ip_address})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def refresh(self):
        """Update last used timestamp."""
        self.last_used_at = datetime.utcnow()


class AuditLog(Base):
    """Audit log model for tracking user actions."""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to user (nullable for system actions)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(100), nullable=True, index=True)
    resource_id = Column(String(100), nullable=True)
    
    # Change tracking
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    
    # Request details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationship
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"


class PasswordReset(Base):
    """Password reset request model."""
    
    __tablename__ = "password_resets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Reset token
    token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="password_resets")
    
    def __repr__(self):
        return f"<PasswordReset(id={self.id}, user_id={self.user_id}, is_used={self.is_used})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if reset token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if reset token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired

