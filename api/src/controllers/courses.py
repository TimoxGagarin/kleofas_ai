from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.src.dao.courses import CoursesDAO
from api.src.exceptions import CourseAlreadyExists, CourseDoesntExists
from api.src.schemas.courses import CreateCourse, DisplayCourse, UpdateCourse
from api.src.utils.sessions import admin_required, get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_course(course: CreateCourse, admin: Annotated[dict, Depends(admin_required)]) -> DisplayCourse:
    existing_course = await CoursesDAO.find_one_or_none(title=course.title)
    if existing_course:
        raise CourseAlreadyExists
    return await CoursesDAO.add(**course.model_dump())


@router.patch("")
async def update_course(
    course_id: int, params: UpdateCourse, admin: Annotated[dict, Depends(admin_required)]
) -> DisplayCourse:
    existing_course = await CoursesDAO.find_by_id(course_id)
    if not existing_course:
        raise CourseDoesntExists
    return await CoursesDAO.update(course_id, **params.model_dump())


@router.get("")
async def get_courses(
    offset: int | None = None, limit: int | None = None, *, admin: Annotated[dict, Depends(get_current_user)]
) -> list[DisplayCourse]:
    return await CoursesDAO.find_all(offset=offset, limit=limit)


@router.get("/{course_id}")
async def get_course(course_id: int, admin: Annotated[dict, Depends(get_current_user)]) -> DisplayCourse:
    course = await CoursesDAO.find_by_id(course_id)
    if not course:
        raise CourseDoesntExists
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, admin: Annotated[dict, Depends(admin_required)]):
    await CoursesDAO.delete(id=course_id)
