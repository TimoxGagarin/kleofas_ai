from api.src.dao.base import BaseDAO
from api.src.db.models import Test


class TestsDAO(BaseDAO):

    model = Test
