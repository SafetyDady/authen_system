"""
Security utilities for authentication and authorization.
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Optional, Union

import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityUtils:
    """Security utility functions."""
    
    @staticmethod
    def create_access_token(
        subject: Union[str, Any], 
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[dict] = None
    ) -> str:
        """Create JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "access",
            "iat": datetime.utcnow(),
        }
        
        if additional_claims:
            to_encode.update(additional_claims)
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        subject: Union[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh",
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),  # JWT ID for token revocation
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            # Check expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                return None
            
            return payload
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_password_reset_token(email: str) -> str:
        """Generate password reset token."""
        delta = timedelta(hours=1)  # Reset token expires in 1 hour
        now = datetime.utcnow()
        expires = now + delta
        
        to_encode = {
            "exp": expires,
            "sub": email,
            "type": "password_reset",
            "iat": now,
        }
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[str]:
        """Verify password reset token and return email."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            if payload.get("type") != "password_reset":
                return None
            
            email = payload.get("sub")
            return email
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def generate_email_verification_token(email: str) -> str:
        """Generate email verification token."""
        delta = timedelta(days=7)  # Verification token expires in 7 days
        now = datetime.utcnow()
        expires = now + delta
        
        to_encode = {
            "exp": expires,
            "sub": email,
            "type": "email_verification",
            "iat": now,
        }
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def verify_email_verification_token(token: str) -> Optional[str]:
        """Verify email verification token and return email."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            if payload.get("type") != "email_verification":
                return None
            
            email = payload.get("sub")
            return email
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def generate_secure_random_string(length: int = 32) -> str:
        """Generate cryptographically secure random string."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """Validate password against security policy."""
        errors = []
        
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long")
        
        if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if settings.PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if settings.PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength_score": max(0, 100 - len(errors) * 20)
        }


# Create global security instance
security = SecurityUtils()

