"""
Authentication API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.api.dependencies import get_current_user, get_request_info
from app.models.user import User
from app.schemas.user import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    LogoutRequest, PasswordReset, PasswordResetConfirm, UserProfile,
    MessageResponse, SuccessResponse
)
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """User login endpoint."""
    auth_service = AuthService(db)
    request_info = get_request_info(request)
    
    # Authenticate user
    user, error = auth_service.authenticate_user(
        login_request,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"]
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    # Create user session
    access_token, refresh_token = auth_service.create_user_session(
        user,
        remember_me=login_request.remember_me,
        device_info=request_info["user_agent"],
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"]
    )
    
    # Prepare user profile
    user_profile = UserProfile(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_profile
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token endpoint."""
    auth_service = AuthService(db)
    request_info = get_request_info(request)
    
    # Refresh access token
    access_token, error = auth_service.refresh_access_token(
        refresh_request.refresh_token,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"]
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    return RefreshTokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    logout_request: LogoutRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User logout endpoint."""
    auth_service = AuthService(db)
    request_info = get_request_info(request)
    
    # Logout user
    auth_service.logout_user(
        current_user,
        refresh_token=logout_request.refresh_token,
        logout_all_devices=logout_request.logout_all_devices,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"]
    )
    
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/password-reset", response_model=MessageResponse)
async def request_password_reset(
    password_reset_request: PasswordReset,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request password reset endpoint."""
    auth_service = AuthService(db)
    request_info = get_request_info(request)
    
    # Request password reset
    auth_service.request_password_reset(
        password_reset_request,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"]
    )
    
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """Confirm password reset endpoint."""
    auth_service = AuthService(db)
    request_info = get_request_info(request)
    
    # Reset password
    success, error = auth_service.reset_password(
        reset_confirm.token,
        reset_confirm.new_password,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"]
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return MessageResponse(message="Password has been reset successfully")


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active sessions."""
    auth_service = AuthService(db)
    sessions = auth_service.get_user_sessions(current_user.id)
    
    return {
        "sessions": [
            {
                "id": str(session.id),
                "device_info": session.device_info,
                "ip_address": session.ip_address,
                "created_at": session.created_at,
                "last_used_at": session.last_used_at,
                "expires_at": session.expires_at,
                "is_current": False  # TODO: Determine current session
            }
            for session in sessions
        ]
    }


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke specific user session."""
    auth_service = AuthService(db)
    request_info = get_request_info(request)
    
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID"
        )
    
    success = auth_service.revoke_session(
        current_user,
        session_uuid,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"]
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return MessageResponse(message="Session revoked successfully")


@router.post("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """Verify if current token is valid."""
    return {
        "valid": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role,
            "is_active": current_user.is_active
        }
    }

