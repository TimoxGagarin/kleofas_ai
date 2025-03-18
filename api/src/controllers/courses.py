from api.src.controllers.base import BaseRouter
from api.src.dao.courses import CoursesDAO
from api.src.schemas.courses import (
    CreateCourse,
    DisplayCourse,
    SearchCourse,
    UpdateCourse,
)

router = BaseRouter(
    entity_name="Course",
    entity_dao=CoursesDAO,
    create_entity=CreateCourse,
    update_entity=UpdateCourse,
    display_entity=DisplayCourse,
    search_entity=SearchCourse,
    prefix="/courses",
    tags=["courses"],
)
