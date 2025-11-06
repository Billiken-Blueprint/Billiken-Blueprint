from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from billiken_blueprint.dependencies import IdentityUserRepo
from billiken_blueprint.identity.identity_user import IdentityUser
from billiken_blueprint.identity.token import Token


router = APIRouter(prefix="/identity", tags=["identity"])


def create_access_token(user: IdentityUser):
    expires = timedelta(hours=1)
    data = {"sub": str(user.id), "email": user.email}
    token = Token.create(data=data, expires_delta=expires)
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
