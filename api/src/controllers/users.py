from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.src.dao.courses import CoursesDAO
from api.src.dao.messages import MessagesDAO
from api.src.dao.user_courses import UserCoursesDAO
from api.src.dao.users import UsersDAO
from api.src.exceptions import CourseAlreadyExists, CourseDoesntExists, CourseIsntAvaliable
from api.src.schemas.courses import DisplayCourse
from api.src.schemas.materials import DisplayMaterial
from api.src.schemas.tests import DisplayTest
from api.src.schemas.users import DisplayUser
from api.src.utils.sessions import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)) -> DisplayUser:
    return user


@router.get("/me/courses")
async def get_my_courses(user: dict = Depends(get_current_user)) -> list[DisplayCourse]:
    return await UsersDAO.find_user_courses(user_id=user["id"])


@router.get("/me/tests")
async def get_tests(user: Annotated[dict, Depends(get_current_user)]) -> list[DisplayTest]:
    messages = await MessagesDAO.find_all(user_id=user["id"])
    result = []
    [result.extend(msg.tests) for msg in messages]
    return result


@router.get("/me/materials")
async def get_materials(user: Annotated[dict, Depends(get_current_user)]) -> list[DisplayMaterial]:
    messages = await MessagesDAO.find_all(user_id=user["id"])
    result = []
    [result.extend(msg.materials) for msg in messages]
    return result


@router.post("/me/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_to_my_courses(course_id: int, user: dict = Depends(get_current_user)):
    course = await UserCoursesDAO.find_one_or_none(course_id=course_id, user_id=user["id"])
    if course:
        raise CourseAlreadyExists
    course = await CoursesDAO.find_by_id(course_id)
    if not course:
        raise CourseDoesntExists
    await UserCoursesDAO.add(user_id=user["id"], course_id=course_id)


@router.get("/me/courses/{course_id}/messages")
async def get_my_course_messages(
    course_id: int, offset: int | None = None, limit: int | None = None, *, user: dict = Depends(get_current_user)
):
    course = await UserCoursesDAO.find_one_or_none(course_id=course_id, user_id=user["id"])
    if not course:
        raise CourseIsntAvaliable
    messages = await MessagesDAO.find_all(course_id=course_id, user_id=user["id"], offset=offset, limit=limit)
    return messages
