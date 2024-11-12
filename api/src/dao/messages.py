from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.src.dao.base import BaseDAO
from api.src.db.config import async_session
from api.src.db.models import Message, Test


class MessagesDAO(BaseDAO):

    model = Message

    @classmethod
    async def find_all(cls, offset: int | None = None, limit: int | None = None, **filter_by):
        async with async_session() as session:
            query = (
                select(cls.model)
                .options(
                    selectinload(cls.model.materials),
                    selectinload(cls.model.tests).options(selectinload(Test.questions)),
                )
                .filter_by(**filter_by)
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(query)
            return result.scalars().all()
