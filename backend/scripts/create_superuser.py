#!/usr/bin/env python3
"""
Script to create initial superuser.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import SessionLocal, create_tables
from app.services.user_service import UserService
from app.schemas.user import UserCreate


def create_superuser():
    """Create initial superuser."""
    print("Creating initial superuser...")
    
    # Create database tables if they don't exist
    create_tables()
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        user_service = UserService(db)
        
        # Check if superuser already exists
        existing_user = user_service.get_user_by_email(settings.FIRST_SUPERUSER_EMAIL)
        if existing_user:
            print(f"Superuser with email {settings.FIRST_SUPERUSER_EMAIL} already exists")
            return
        
        # Create superuser
        superuser_data = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            confirm_password=settings.FIRST_SUPERUSER_PASSWORD,
            first_name="Super",
            last_name="Admin",
            role="superadmin",
            is_active=True
        )
        
        superuser = user_service.create_user(superuser_data)
        
        # Mark as verified
        superuser.is_verified = True
        db.commit()
        
        print(f"Superuser created successfully:")
        print(f"  Email: {superuser.email}")
        print(f"  Name: {superuser.full_name}")
        print(f"  Role: {superuser.role}")
        print(f"  ID: {superuser.id}")
        
    except Exception as e:
        print(f"Error creating superuser: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_superuser()

