from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

    id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {k: self.__dict__[k] for k in self.__dict__ if "_sa_" != k[:4]}

    def __repr__(self):
        return f"""<{self.__class__.__name__}({[', '.join('%s=%s' % (k, self.__dict__[k])
                                             for k in self.__dict__ if '_sa_' != k[:4])]}"""


class SSOProvider(Base):
    __tablename__ = "sso_providers"

    name = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, nullable=False)
    sso_type = Column(BigInteger, ForeignKey("sso_providers.id"), nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    avatar = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False)
    is_enabled = Column(Boolean, nullable=False)
