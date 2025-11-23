from os import minor
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel

from billiken_blueprint import config, identity
from billiken_blueprint.dependencies import AuthToken, IdentityUserRepo, StudentRepo
from billiken_blueprint.domain.student import Student


router = APIRouter(prefix="/user_info", tags=["user_info"])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class UserInfoBody(BaseModel):
    name: str
    graduation_year: int
    degree_ids: list[int]
    completed_course_ids: list[int]
    major_code: str
    degree_type: str
    college: str


@router.post("")
async def set_user_info(
    token: AuthToken,
    user_info: UserInfoBody,
    identity_user_repo: IdentityUserRepo,
    student_repo: StudentRepo,
):
    try:
        payload = jwt.decode(token, config.JWT_PUBLIC_KEY, algorithms=["EdDSA"])
        identity_id = payload.get("sub")
        if not identity_id:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    identity = await identity_user_repo.get_by_id(int(identity_id))
    if not identity:
        raise credentials_exception
    student = Student(
        id=None,
        name=user_info.name,
        degree_ids=user_info.degree_ids,
        completed_course_ids=user_info.completed_course_ids,
        graduation_year=user_info.graduation_year,
        major_code=user_info.major_code,
        degree_type=user_info.degree_type,
        college=user_info.college,
    )
    student = await student_repo.save(student)

    identity.student_id = student.id
    await identity_user_repo.save(identity)


@router.get("")
async def get_user_info(
    token: AuthToken,
    identity_repo: IdentityUserRepo,
    student_repo: StudentRepo,
):
    try:
        payload = jwt.decode(token, config.JWT_PUBLIC_KEY, algorithms=["EdDSA"])
        identity_id = payload.get("sub")
        if not identity_id:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    identity = await identity_repo.get_by_id(int(identity_id))
    if not identity:
        raise credentials_exception
    if not identity.student_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student information not found for this user",
        )

    student = await student_repo.get_by_id(identity.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student information not found",
        )

    return dict(
        email=identity.email,
        name=student.name,
        degreeIds=student.degree_ids,
        completedCourseIds=student.completed_course_ids,
        graduation_year=student.graduation_year,
        major_code=student.major_code,
        degree_type=student.degree_type,
        college=student.college,
    )
