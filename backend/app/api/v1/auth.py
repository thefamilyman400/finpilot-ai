"""
Authentication endpoints
Handles user registration, login, token refresh, password reset, and email verification
"""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
    create_password_reset_token,
    verify_password_reset_token,
    create_email_verification_token,
    verify_email_verification_token,
)
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    RefreshToken,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification,
    ResendVerificationEmail,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Register a new user
    
    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    - **full_name**: Optional full name
    - **phone_number**: Optional phone number
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        is_active=True,
        is_verified=False,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # TODO: Send verification email in background
    # verification_token = create_email_verification_token(new_user.email)
    # background_tasks.add_task(send_verification_email, new_user.email, verification_token)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Login with email and password (OAuth2 compatible)
    
    Returns access token and refresh token
    
    - **username**: User's email address
    - **password**: User's password
    """
    # Find user by email (username field contains email)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshToken,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Refresh access token using refresh token
    
    Returns new access token and refresh token
    """
    # Decode and verify refresh token
    payload = decode_token(token_data.refresh_token)
    verify_token_type(payload, "refresh")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Verify user still exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Logout current user
    
    Note: With JWT, actual logout is handled client-side by removing tokens.
    This endpoint is provided for consistency and can be extended with token blacklisting.
    """
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Request password reset
    
    Sends password reset email if user exists
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if user:
        reset_token = create_password_reset_token(user.email)
        # TODO: Send password reset email in background
        # background_tasks.add_task(send_password_reset_email, user.email, reset_token)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset-request")
async def password_reset_request(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Request password reset (alias for forgot-password)
    
    Sends password reset email if user exists
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if user:
        reset_token = create_password_reset_token(user.email)
        # TODO: Send password reset email in background
        # background_tasks.add_task(send_password_reset_email, user.email, reset_token)
    
    return {"message": "If the email exists, a password reset email sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Reset password using reset token
    """
    # Verify reset token
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    await db.commit()
    
    return {"message": "Password successfully reset"}


@router.get("/verify-email/{token}")
async def verify_email_get(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Verify user email using verification token (GET method for email links)
    """
    # Verify token
    email = verify_email_verification_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Mark as verified
    user.is_verified = True
    await db.commit()
    
    return {"message": "Email successfully verified"}


@router.post("/verify-email")
async def verify_email_post(
    verification: EmailVerification,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Verify user email using verification token (POST method for API)
    """
    # Verify token
    email = verify_email_verification_token(verification.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Mark as verified
    user.is_verified = True
    await db.commit()
    
    return {"message": "Email successfully verified"}


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationEmail,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Resend email verification link
    """
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if user and not user.is_verified:
        verification_token = create_email_verification_token(user.email)
        # TODO: Send verification email in background
        # background_tasks.add_task(send_verification_email, user.email, verification_token)
    
    return {"message": "If the email exists and is not verified, a verification link has been sent"}

# Made with Bob
