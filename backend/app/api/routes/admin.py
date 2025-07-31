"""
Admin API routes for SuperAdmin functionality.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.dependencies import (
    get_current_superadmin_user, get_request_info
)
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserUpdate, User as UserResponse, UserList,
    UserSearchParams, PaginatedResponse, UserStats, MessageResponse,
    AuditLogEntry
)
from app.services.user_service import UserService


router = APIRouter(prefix="/admin", tags=["Admin Management"])


@router.get("/admins", response_model=List[UserResponse])
async def list_admin_users(
    current_user: User = Depends(get_current_superadmin_user),
    db: Session = Depends(get_db)
):
    """List all admin users (SuperAdmin only)."""
    user_service = UserService(db)
    
    # Search for admin users
    search_params = UserSearchParams(
        page=1,
        size=100,  # Get all admins
        sort_by="created_at",
        sort_order="asc"
    )
    
    # Get all admin users
    admin_roles = ["admin1", "admin2", "admin3"]
    all_admins = []
    
    for role in admin_roles:
        search_params.role = role
        admins, _ = user_service.search_users(search_params)
        all_admins.extend(admins)
    
    return [UserResponse.from_orm(admin) for admin in all_admins]


@router.post("/admins", response_model=UserResponse)
async def create_admin_user(
    user_create: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_superadmin_user),
    db: Session = Depends(get_db)
):
    """Create a new admin user (SuperAdmin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    # Validate admin role
    if user_create.role not in ["admin1", "admin2", "admin3"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be one of: admin1, admin2, admin3"
        )
    
    try:
        admin_user = user_service.create_user(
            user_create,
            created_by=current_user
        )
        return admin_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/admins/{admin_id}", response_model=UserResponse)
async def get_admin_user(
    admin_id: str,
    current_user: User = Depends(get_current_superadmin_user),
    db: Session = Depends(get_db)
):
    """Get admin user by ID (SuperAdmin only)."""
    user_service = UserService(db)
    
    try:
        admin_uuid = uuid.UUID(admin_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid admin ID"
        )
    
    admin_user = user_service.get_user_by_id(admin_uuid)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Verify it's an admin user
    if admin_user.role not in ["admin1", "admin2", "admin3"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    return admin_user


@router.put("/admins/{admin_id}", response_model=UserResponse)
async def update_admin_user(
    admin_id: str,
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_superadmin_user),
    db: Session = Depends(get_db)
):
    """Update admin user by ID (SuperAdmin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    try:
        admin_uuid = uuid.UUID(admin_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid admin ID"
        )
    
    # Get target admin user
    admin_user = user_service.get_user_by_id(admin_uuid)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Verify it's an admin user
    if admin_user.role not in ["admin1", "admin2", "admin3"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Validate role change if provided
    if user_update.role and user_update.role not in ["admin1", "admin2", "admin3"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin role must be one of: admin1, admin2, admin3"
        )
    
    try:
        updated_admin = user_service.update_user(
            admin_uuid,
            user_update,
            updated_by=current_user
        )
        
        if not updated_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin user not found"
            )
        
        return updated_admin
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/admins/{admin_id}", response_model=MessageResponse)
async def delete_admin_user(
    admin_id: str,
    request: Request,
    current_user: User = Depends(get_current_superadmin_user),
    db: Session = Depends(get_db)
):
    """Delete admin user by ID (SuperAdmin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    try:
        admin_uuid = uuid.UUID(admin_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid admin ID"
        )
    
    # Get target admin user
    admin_user = user_service.get_user_by_id(admin_uuid)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Verify it's an admin user
    if admin_user.role not in ["admin1", "admin2", "admin3"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent self-deletion
    if admin_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = user_service.delete_user(admin_uuid, deleted_by=current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    return MessageResponse(message="Admin user deleted successfully")


@router.post("/admins/{admin_id}/lock", response_model=MessageResponse)
async def lock_admin_user(
    admin_id: str,
    request: Request,
    current_user: User = Depends(get_current_superadmin_user),
    db: Session = Depends(get_db)
):
    """Lock admin user account (SuperAdmin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    try:
        admin_uuid = uuid.UUID(admin_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid admin ID"
        )
    
    # Get target admin user
    admin_user = user_service.get_user_by_id(admin_uuid)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Verify it's an admin user
    if admin_user.role not in ["admin1", "admin2", "admin3"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent self-locking
    if admin_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot lock your own account"
        )
    
    success = user_service.lock_user(admin_uuid, locked_by=current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    return MessageResponse(message="Admin user locked successfully")


@router.post("/admins/{admin_id}/unlock", response_model=MessageResponse)
async def unlock_admin_user(
    admin_id: str,
    request: Request,
    current_user: User = Depends(get_current_superadmin_user),
    db: Session = Depends(get_db)
):
    """Unlock admin user account (SuperAdmin only)."""
    user_service = UserService(db)
    request_info = get_request_info(request)
    
    try:
        admin_uuid = uuid.UUID(admin_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid admin ID"
        )
    
    # Get target admin user
    admin_user = user_service.get_user_by_id(admin_uuid)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Verify it's an admin user
    if admin_user.role not in ["admin1", "admin2", "admin3"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    success = user_service.unlock_user(admin_uuid, unlocked_by=current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    return MessageResponse(message="Admin user unlocked successfully")


@router.get("/system/stats")
async def get_system_stats(
    current_user: User = Depends(get_current_superadmin_user),
    db: Session = Depends(get_db)
):
    """Get system statistics (SuperAdmin only)."""
    user_service = UserService(db)
    
    # Get user stats
    user_stats = user_service.get_user_stats()
    
    # Get admin-specific stats
    admin_stats = {}
    for role in ["admin1", "admin2", "admin3"]:
        search_params = UserSearchParams(role=role, page=1, size=1)
        _, count = user_service.search_users(search_params)
        admin_stats[role] = count
    
    return {
        "user_stats": user_stats,
        "admin_stats": admin_stats,
        "system_info": {
            "total_admins": sum(admin_stats.values()),
            "active_admins": sum(
                user_service.search_users(UserSearchParams(role=role, is_active=True, page=1, size=1))[1]
                for role in ["admin1", "admin2", "admin3"]
            )
        }
    }


@router.get("/audit-logs")
async def get_system_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    action: str = Query(None),
    resource: str = Query(None),
    current_user: User = Depends(get_current_superadmin_user),
    db: Session = Depends(get_db)
):
    """Get system audit logs (SuperAdmin only)."""
    user_service = UserService(db)
    
    audit_logs, total = user_service.get_audit_logs(
        action=action,
        resource=resource,
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


@router.get("/roles")
async def get_available_roles(
    current_user: User = Depends(get_current_superadmin_user)
):
    """Get available roles for admin management (SuperAdmin only)."""
    return {
        "admin_roles": [
            {
                "value": "admin1",
                "label": "Admin 1",
                "description": "Administrator with user management permissions"
            },
            {
                "value": "admin2", 
                "label": "Admin 2",
                "description": "Administrator with user management permissions"
            },
            {
                "value": "admin3",
                "label": "Admin 3", 
                "description": "Administrator with user management permissions"
            }
        ],
        "user_roles": [
            {
                "value": "user",
                "label": "User",
                "description": "Regular user with basic permissions"
            }
        ]
    }

