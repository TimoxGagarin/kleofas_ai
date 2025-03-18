from copy import deepcopy
from typing import Annotated

from fastapi import Depends, Query

from api.src.controllers.base import BaseRouter
from api.src.controllers.users import get_current_superuser
from api.src.dao.messages import MessagesDAO
from api.src.dao.tests import TestsDAO
from api.src.dao.user_courses import UserCoursesDAO
from api.src.dao.users import UsersDAO
from api.src.exceptions import CourseIsntAvaliable, UserDoesntExists
from api.src.schemas.tests import DisplayTest, SearchTest
from api.src.utils.utils import remove_none_values


class TestRouter(BaseRouter):
    def entity__get_all(self, summary):
        @self.get("", summary=summary)
        async def get_tests(
            data: self.search_entity = Query(),
            *,
            admin: Annotated[dict, Depends(get_current_superuser)],
        ) -> list[self.display_entity]:
            params = remove_none_values(data.model_dump())

            if data.user_id:
                user = await UsersDAO.find_by_id(data.user_id)
                if not user:
                    raise UserDoesntExists
            if data.course_id:
                data = deepcopy(params)
                data.pop("limit")
                data.pop("offset")
                course = await UserCoursesDAO.find_one_or_none(**data)
                if not course:
                    raise CourseIsntAvaliable

            messages = await MessagesDAO.find_all(**params)
            result = []
            [result.append(msg.test) for msg in messages if msg.test]
            return result


router = TestRouter(
    entity_name="Test",
    entity_dao=TestsDAO,
    display_entity=DisplayTest,
    search_entity=SearchTest,
    prefix="/tests",
    tags=["tests"],
)
