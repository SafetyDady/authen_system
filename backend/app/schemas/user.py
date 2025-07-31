"""
User schemas for API request/response validation.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, validator


class UserRole(str, Enum):
    """User role enumeration."""
    SUPERADMIN = "superadmin"
    ADMIN1 = "admin1"
    ADMIN2 = "admin2"
    ADMIN3 = "admin3"
    USER = "user"


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.USER
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('email')
    def email_must_be_valid(cls, v):
        # Additional email validation can be added here
        return v.lower()


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserUpdateProfile(BaseModel):
    """Schema for users updating their own profile."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr
    
    @validator('email')
    def email_must_be_valid(cls, v):
        return v.lower()


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# Response schemas
class User(UserBase):
    """User response schema."""
    id: uuid.UUID
    full_name: str
    is_verified: bool
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    failed_login_attempts: int
    
    class Config:
        from_attributes = True
        
    @validator('full_name', pre=True, always=True)
    def set_full_name(cls, v, values):
        if 'first_name' in values and 'last_name' in values:
            return f"{values['first_name']} {values['last_name']}".strip()
        return v


class UserProfile(BaseModel):
    """User profile response schema."""
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    avatar_url: Optional[str]
    role: UserRole
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserList(BaseModel):
    """User list response schema."""
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    is_locked: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserSession(BaseModel):
    """User session response schema."""
    id: uuid.UUID
    device_info: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    expires_at: datetime
    last_used_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics schema."""
    total_users: int
    active_users: int
    verified_users: int
    locked_users: int
    users_by_role: dict
    recent_registrations: int
    recent_logins: int


class AuditLogEntry(BaseModel):
    """Audit log entry schema."""
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    action: str
    resource: Optional[str]
    resource_id: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    user_email: Optional[str] = None
    
    class Config:
        from_attributes = True


# Authentication schemas
class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False
    
    @validator('email')
    def email_must_be_valid(cls, v):
        return v.lower()


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., min_length=1)


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutRequest(BaseModel):
    """Logout request schema."""
    refresh_token: Optional[str] = None
    logout_all_devices: bool = False


# Pagination schemas
class PaginationParams(BaseModel):
    """Pagination parameters schema."""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class UserSearchParams(PaginationParams):
    """User search parameters schema."""
    search: Optional[str] = Field(None, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_locked: Optional[bool] = None


class PaginatedResponse(BaseModel):
    """Paginated response schema."""
    items: List[UserList]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


# Error schemas
class ErrorDetail(BaseModel):
    """Error detail schema."""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    errors: Optional[List[ErrorDetail]] = None
    code: Optional[str] = None


# Success schemas
class SuccessResponse(BaseModel):
    """Success response schema."""
    message: str
    data: Optional[dict] = None


class MessageResponse(BaseModel):
    """Simple message response schema."""
    message: str