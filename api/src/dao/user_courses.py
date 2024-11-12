from api.src.dao.base import BaseDAO
from api.src.db.models import UserCourses


class UserCoursesDAO(BaseDAO):
    model = UserCourses
