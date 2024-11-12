from sqlalchemy import update

from api.src.dao.base import BaseDAO
from api.src.db.config import async_session
from api.src.db.models import Course


class CoursesDAO(BaseDAO):

    model = Course

    @classmethod
    async def update(cls, id, **data):
        data = {key: value for key, value in data.items() if value is not None}

        async with async_session() as session:
            query = (
                update(cls.model)
                .filter_by(id=id)
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
