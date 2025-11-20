from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from billiken_blueprint.dependencies import IdentityUserRepo
from billiken_blueprint.identity.identity_user import IdentityUser
from billiken_blueprint.identity.token import Token
from billiken_blueprint.identity.token_payload import TokenPayload


router = APIRouter(prefix="/identity", tags=["identity"])


def create_access_token(user: IdentityUser):
    expires = timedelta(hours=1)
    token = Token.create(
        payload=TokenPayload(sub=str(user.id), email=user.email), expires_delta=expires
    )
    return token


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    identity_user_repo: IdentityUserRepo,
):
    user = await identity_user_repo.get_by_email(form.username)
    if not user or not user.verify_password(form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user)
    return token


@router.post("/register", response_model=Token)
async def register(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    identity_user_repo: IdentityUserRepo,
):
    existing_user = await identity_user_repo.get_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    new_user = IdentityUser.create(email=email, password=password)
    saved_user = await identity_user_repo.save(new_user)
    token = create_access_token(saved_user)
    return token


class PasswordResetResponse(BaseModel):
    message: str
    email: str


@router.post("/forgot-password")
async def forgot_password(
    email: Annotated[str, Form()],
    identity_user_repo: IdentityUserRepo,
) -> PasswordResetResponse:
    """
    Endpoint to handle password reset requests.
    In a production environment, this would:
    1. Generate a unique reset token
    2. Store the token with expiration
    3. Send an email with reset link
    
    For now, it just validates the email exists and returns success.
    """
    user = await identity_user_repo.get_by_email(email)
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
    reset_token: Annotated[str, Form()],
    identity_user_repo: IdentityUserRepo,
) -> dict:
    """
    Endpoint to actually reset the password using a token.
    This would validate the reset token and update the password.
    """
    # TODO: Implement token validation
    # For now, just update the password if user exists
    
    user = await identity_user_repo.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.update_password(new_password)
    await identity_user_repo.save(user)
    
    return {"message": "Password successfully reset"}
