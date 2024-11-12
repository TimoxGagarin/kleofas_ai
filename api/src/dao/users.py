from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from api.src.dao.base import BaseDAO
from api.src.db.config import async_session
from api.src.db.models import User


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def update(cls, **data):
        async with async_session() as session:
            query = (
                update(cls.model)
                .filter_by(user_id=data["user_id"], sso_type=data["sso_type"])
                .values(**data)
                .returning(cls.model)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(query)
            await session.commit()

            updated_instance = result.scalar_one_or_none()
            if updated_instance:
                await session.refresh(updated_instance)
            return updated_instance

    @classmethod
    async def find_user_courses(cls, user_id):
        async with async_session() as session:
            result = await session.execute(
                select(cls.model).filter(cls.model.id == user_id).options(selectinload(cls.model.courses))
            )
            user = result.scalar_one_or_none()
            if user:
                return user.courses
            return None
