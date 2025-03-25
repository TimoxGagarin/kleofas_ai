from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from api.src.controllers.users import get_current_active_user
from api.src.dao.user_courses import UserCoursesDAO
from api.src.exceptions import CourseDoesntExists
from api.src.schemas.users import DisplayUser
from api.src.settings import settings

router = APIRouter(tags=["debug"])


@router.get("/chat/{course_id}", response_class=HTMLResponse)
async def chat_interface(
    request: Request,
    course_id: int,
    user: DisplayUser = Depends(get_current_active_user),
):
    chat = await UserCoursesDAO.find_one_or_none(course_id=course_id, user_id=user.id)
    if not chat:
        raise CourseDoesntExists
    return settings.templates.TemplateResponse(
        "chat.html", {"request": request, "course_id": course_id}
    )
