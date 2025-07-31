"""
Users API routes.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.dependencies import (
    get_current_user, get_current_admin_user, get_current_superadmin_user,
    get_permission_checker, PermissionChecker, get_request_info
)
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserUpdate, UserUpdateProfile, PasswordChange,
    User as UserResponse, UserList, UserProfile, UserSearchParams,
    PaginatedResponse, UserStats, MessageResponse, SuccessResponse,
    AuditLogEntry
)
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    permission_checker: PermissionChecker = Depends(get_permission_checker),
    db: Session = Depends(get_db)
):
    """Create a new user (Admin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    # Check if current user can assign the requested role
    if not permission_checker.can_assign_role(user_create.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot assign role '{user_create.role}'"
        )
    
    try:
        user = user_service.create_user(
            user_create,
            created_by=current_user
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    search_params: UserSearchParams = Depends(),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List users with pagination and filters (Admin only)."""
    user_service = UserService(db)
    
    # Filter users based on current user's permissions
    if not current_user.is_superadmin:
        # Non-superadmin users can only see regular users
        search_params.role = "user"
    
    users, total = user_service.search_users(search_params)
    
    # Calculate pagination info
    pages = (total + search_params.size - 1) // search_params.size
    has_next = search_params.page < pages
    has_prev = search_params.page > 1
    
    return PaginatedResponse(
        items=[UserList.from_orm(user) for user in users],
        total=total,
        page=search_params.page,
        size=search_params.size,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user statistics (Admin only)."""
    user_service = UserService(db)
    return user_service.get_user_stats()


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile."""
    return UserProfile.from_orm(current_user)


@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    profile_update: UserUpdateProfile,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    updated_user = user_service.update_user_profile(
        current_user.id,
        profile_update
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile.from_orm(updated_user)


@router.post("/me/change-password", response_model=MessageResponse)
async def change_my_password(
    password_change: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    try:
        success = user_service.change_password(current_user.id, password_change)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return MessageResponse(message="Password changed successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    permission_checker: PermissionChecker = Depends(get_permission_checker),
    db: Session = Depends(get_db)
):
    """Get user by ID (Admin only)."""
    user_service = UserService(db)
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    user = user_service.get_user_by_id(user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user can view this user
    if not permission_checker.can_view_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    permission_checker: PermissionChecker = Depends(get_permission_checker),
    db: Session = Depends(get_db)
):
    """Update user by ID (Admin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    # Get target user
    target_user = user_service.get_user_by_id(user_uuid)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user can manage this user
    if not permission_checker.can_manage_user(target_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )
    
    # Check role assignment permissions
    if user_update.role and not permission_checker.can_assign_role(user_update.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot assign role '{user_update.role}'"
        )
    
    try:
        updated_user = user_service.update_user(
            user_uuid,
            user_update,
            updated_by=current_user
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    permission_checker: PermissionChecker = Depends(get_permission_checker),
    db: Session = Depends(get_db)
):
    """Delete user by ID (Admin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    # Get target user
    target_user = user_service.get_user_by_id(user_uuid)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user can manage this user
    if not permission_checker.can_manage_user(target_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this user"
        )
    
    # Prevent self-deletion
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = user_service.delete_user(user_uuid, deleted_by=current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return MessageResponse(message="User deleted successfully")


@router.post("/{user_id}/lock", response_model=MessageResponse)
async def lock_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    permission_checker: PermissionChecker = Depends(get_permission_checker),
    db: Session = Depends(get_db)
):
    """Lock user account (Admin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    # Get target user
    target_user = user_service.get_user_by_id(user_uuid)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user can manage this user
    if not permission_checker.can_manage_user(target_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to lock this user"
        )
    
    # Prevent self-locking
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot lock your own account"
        )
    
    success = user_service.lock_user(user_uuid, locked_by=current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return MessageResponse(message="User locked successfully")


@router.post("/{user_id}/unlock", response_model=MessageResponse)
async def unlock_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    permission_checker: PermissionChecker = Depends(get_permission_checker),
    db: Session = Depends(get_db)
):
    """Unlock user account (Admin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    # Get target user
    target_user = user_service.get_user_by_id(user_uuid)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user can manage this user
    if not permission_checker.can_manage_user(target_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to unlock this user"
        )
    
    success = user_service.unlock_user(user_uuid, unlocked_by=current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return MessageResponse(message="User unlocked successfully")


@router.get("/{user_id}/audit-logs")
async def get_user_audit_logs(
    user_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    action: str = Query(None),
    current_user: User = Depends(get_current_admin_user),
    permission_checker: PermissionChecker = Depends(get_permission_checker),
    db: Session = Depends(get_db)
):
    """Get user audit logs (Admin only)."""
    user_service = UserService(db)
    
    # Check if current user can access audit logs
    if not permission_checker.can_access_audit_logs():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view audit logs"
        )
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    # Get target user
    target_user = user_service.get_user_by_id(user_uuid)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user can view this user's audit logs
    if not permission_checker.can_view_user(target_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user's audit logs"
        )
    
    audit_logs, total = user_service.get_audit_logs(
        user_id=user_uuid,
        action=action,
        page=page,
        size=size
    )
    
    # Calculate pagination info
    pages = (total + size - 1) // size
    has_next = page < pages
    has_prev = page > 1
    
    return {
        "items": [AuditLogEntry.from_orm(log) for log in audit_logs],
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "has_next": has_next,
        "has_prev": has_prev
    }

