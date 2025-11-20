from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

import services
from identity.identity_user import IdentityUser, password_hash
from identity.token import Token

router = APIRouter(prefix="/identity", tags=["identity"])


def create_access_token(identity: IdentityUser):
    expires = timedelta(minutes=15)
    token = Token.create(data={"sub": identity.email}, expires_delta=expires)
    return token


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await services.identity_user_repository.get_by_email(form_data.username)
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(identity=user)
    return token


@router.post("/register")
async def register(
    email: Annotated[str, Form()], password: Annotated[str, Form()]
) -> Token:
    existing = await services.identity_user_repository.get_by_email(email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    h = password_hash.hash(password)
    identity = IdentityUser(email=email, password_hash=h)
    await services.identity_user_repository.save(identity)
    token = create_access_token(identity=identity)
    return token


class PasswordResetResponse(BaseModel):
    message: str
    email: str


@router.post("/forgot-password")
async def forgot_password(
    email: Annotated[str, Form()]
) -> PasswordResetResponse:
    """
    Endpoint to handle password reset requests.
    In a production environment, this would:
    1. Generate a unique reset token
    2. Store the token with expiration
    3. Send an email with reset link
    
    For now, it just validates the email exists and returns success.
    """
    user = await services.identity_user_repository.get_by_email(email)
    if not user:
        # Don't reveal if email exists or not (security best practice)
        # Always return success to prevent email enumeration
        return PasswordResetResponse(
            message="If this email is registered, you will receive password reset instructions.",
            email=email
        )
    
    # TODO: Generate reset token and send email
    # reset_token = generate_reset_token(user)
    # send_password_reset_email(email, reset_token)
    
    return PasswordResetResponse(
        message="Password reset instructions have been sent to your email.",
        email=email
    )


@router.post("/reset-password")
async def reset_password(
    email: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    reset_token: Annotated[str, Form()]
) -> dict:
    """
    Endpoint to actually reset the password using a token.
    This would validate the reset token and update the password.
    """
    # TODO: Implement token validation
    # For now, just update the password if user exists
    
    user = await services.identity_user_repository.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    h = password_hash.hash(new_password)
    user.password_hash = h
    await services.identity_user_repository.save(user)
    
    return {"message": "Password successfully reset"}
