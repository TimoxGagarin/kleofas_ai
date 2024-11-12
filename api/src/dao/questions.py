from api.src.dao.base import BaseDAO
from api.src.db.config import async_session
from api.src.db.models import Question


class QuestionsDAO(BaseDAO):

    model = Question

    @classmethod
    async def add_all(cls, test_id: int, rows: list[dict]):
        async with async_session() as session:
            instances = [cls.model(test_id=test_id, **row) for row in rows]
            session.add_all(instances)
            await session.commit()

            for instance in instances:
                await session.refresh(instance)
            return instances
