from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm

import services
from infrastructure.identity.identity_user import IdentityUser, password_hash
from infrastructure.identity.token import Token

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
