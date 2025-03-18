from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.src.dao.base import BaseDAO
from api.src.db.config import async_session
from api.src.db.models import Users


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def find_user_courses(cls, user_id):
        async with async_session() as session:
            result = await session.execute(
                select(cls.model)
                .filter(cls.model.id == user_id)
                .options(selectinload(cls.model.courses))
            )
            user = result.unique().scalar_one_or_none()
            if user:
                return user.courses
            return None
