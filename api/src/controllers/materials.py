from copy import deepcopy
from typing import Annotated

from fastapi import Depends, Query

from api.src.controllers.base import BaseRouter
from api.src.controllers.users import get_current_superuser
from api.src.dao.materials import MaterialsDAO
from api.src.dao.messages import MessagesDAO
from api.src.dao.user_courses import UserCoursesDAO
from api.src.dao.users import UsersDAO
from api.src.exceptions import CourseIsntAvaliable, UserDoesntExists
from api.src.schemas.materials import DisplayMaterial, SearchMaterial
from api.src.utils.utils import remove_none_values


class MaterialRouter(BaseRouter):
    def entity__get_all(self, summary):
        @self.get("")
        async def get_materials(
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
            [result.extend(msg.materials) for msg in messages]
            return result


router = MaterialRouter(
    entity_name="Material",
    entity_dao=MaterialsDAO,
    display_entity=DisplayMaterial,
    search_entity=SearchMaterial,
    prefix="/materials",
    tags=["materials"],
)
