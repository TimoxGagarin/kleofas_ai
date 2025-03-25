from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import RedisStrategy

from api.src.auth.manager import get_user_manager
from api.src.auth.oauth import enabled_providers
from api.src.auth.transport import auth_backend, get_redis_strategy
from api.src.dao.courses import CoursesDAO
from api.src.dao.messages import MessagesDAO
from api.src.dao.user_courses import UserCoursesDAO
from api.src.dao.users import UsersDAO
from api.src.db.models import Users
from api.src.db.s3 import file_storage
from api.src.exceptions import (
    CourseAlreadyExists,
    CourseDoesntExists,
    CourseIsntAvaliable,
)
from api.src.schemas.courses import DisplayCourse
from api.src.schemas.materials import DisplayMaterial
from api.src.schemas.tests import DisplayTest
from api.src.schemas.users import CreateUser, DisplayUser, UpdateUser
from api.src.settings import settings
from api.src.utils.utils import remove_none_values

router = APIRouter(prefix="/users", tags=["users"])


fastapi_users = FastAPIUsers[Users, UUID](
    get_user_manager,
    [auth_backend],
)
get_current_active_user = fastapi_users.authenticator.current_user(
    active=True, verified=True
)
get_current_superuser = fastapi_users.authenticator.current_user(
    active=True, verified=True, superuser=True
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True)
)

router.include_router(fastapi_users.get_register_router(DisplayUser, CreateUser))

router.include_router(fastapi_users.get_verify_router(DisplayUser))

router.include_router(fastapi_users.get_reset_password_router())

for provider in enabled_providers:
    router.include_router(
        fastapi_users.get_oauth_router(
            provider,
            auth_backend,
            settings.SESSION_SECRET,
            associate_by_email=True,
            is_verified_by_default=True,
        ),
        prefix=f"/{provider.name}",
    )


@router.get("/me")
async def get_me(user: dict = Depends(get_current_active_user)) -> DisplayUser:
    return user


@router.patch("/me")
async def update_me(
    username: str | None = Form(None),
    avatar: UploadFile | None = File(None),
    password: str | None = Form(None),
    user: DisplayUser = Depends(get_current_active_user),
) -> DisplayUser:
    avatar_id = None
    if avatar:
        avatar_id = file_storage.write(avatar.file, avatar.filename)
    data = remove_none_values(
        UpdateUser(
            username=username, avatar_id=avatar_id, password=password
        ).model_dump()
    )
    if password:
        async for manager in get_user_manager():
            data["hashed_password"] = manager.password_helper.hash(password)
            data.pop("password")
    return await UsersDAO.update(user.id, **data)


@router.get("/me/courses")
async def get_my_courses(
    user: DisplayUser = Depends(get_current_active_user),
) -> list[DisplayCourse]:
    return await UsersDAO.find_user_courses(user_id=user.id)


@router.get("/me/tests")
async def get_tests(
    user: Annotated[DisplayUser, Depends(get_current_active_user)],
) -> list[DisplayTest]:
    messages = await MessagesDAO.find_all(user_id=user.id)
    result = []
    [result.extend(msg.tests) for msg in messages]
    return result


@router.get("/me/materials")
async def get_materials(
    user: Annotated[DisplayUser, Depends(get_current_active_user)],
) -> list[DisplayMaterial]:
    messages = await MessagesDAO.find_all(user_id=user.id)
    result = []
    [result.extend(msg.materials) for msg in messages]
    return result


@router.post("/me/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_to_my_courses(
    course_id: int, user: DisplayUser = Depends(get_current_active_user)
):
    course = await UserCoursesDAO.find_one_or_none(course_id=course_id, user_id=user.id)
    if course:
        raise CourseAlreadyExists
    course = await CoursesDAO.find_by_id(course_id)
    if not course:
        raise CourseDoesntExists
    await UserCoursesDAO.add(user_id=user.id, course_id=course_id)


@router.get("/me/courses/{course_id}/messages")
async def get_my_course_messages(
    course_id: int,
    offset: int | None = None,
    limit: int | None = None,
    *,
    user: DisplayUser = Depends(get_current_active_user),
):
    course = await UserCoursesDAO.find_one_or_none(course_id=course_id, user_id=user.id)
    if not course:
        raise CourseIsntAvaliable
    messages = await MessagesDAO.find_all(
        course_id=course_id, user_id=user.id, offset=offset, limit=limit
    )
    return messages


@router.get("/me/ws_token")
async def get_ws_token(
    redis: RedisStrategy = Depends(get_redis_strategy),
    user: DisplayUser = Depends(get_current_active_user),
):
    return {"token": await redis.write_token(user)}
