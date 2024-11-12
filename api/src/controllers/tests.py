from typing import Annotated

from fastapi import APIRouter, Depends

from api.src.dao.messages import MessagesDAO
from api.src.dao.user_courses import UserCoursesDAO
from api.src.dao.users import UsersDAO
from api.src.exceptions import CourseIsntAvaliable, UserDoesntExists
from api.src.schemas.tests import DisplayTest
from api.src.utils.sessions import admin_required

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("")
async def get_tests(
    course_id: int | None = None, user_id: int | None = None, *, admin: Annotated[dict, Depends(admin_required)]
) -> list[DisplayTest]:
    params = {k: v for k, v in {"course_id": course_id, "user_id": user_id}.items() if v}

    if user_id:
        user = await UsersDAO.find_by_id(user_id)
        if not user:
            raise UserDoesntExists
    if course_id:
        course = await UserCoursesDAO.find_one_or_none(**params)
        if not course:
            raise CourseIsntAvaliable

    messages = await MessagesDAO.find_all(**params)
    result = []
    [result.extend(msg.tests) for msg in messages]
    return result
