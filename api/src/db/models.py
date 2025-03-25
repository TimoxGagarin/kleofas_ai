from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID, uuid4

from faker import Faker
from fastapi import Depends, Request
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import UUID as GUID
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from api.src.db.config import get_async_session


class Base(DeclarativeBase):
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"""<{self.__class__.__name__}({
            [
                ", ".join(
                    "%s=%s" % (k, self.__dict__[k])
                    for k in self.__dict__
                    if "_sa_" != k[:4]
                )
            ]
        }"""


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False
    )

    user: Mapped["Users"] = relationship("Users", back_populates="oauth_accounts")

    async def __admin_repr__(self, request: Request):
        return f"{self.user_id} {self.oauth_name} Oauth Account"


class Users(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(
        String(length=320), index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    avatar_id: Mapped[str | None] = mapped_column(
        String(length=320), default="files/templates/profile.png", nullable=False
    )
    hashed_password: Mapped[str | None] = mapped_column(
        String(length=1024), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = Column(
        DateTime, server_default=func.now(), nullable=False
    )

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    courses = relationship("Course", secondary="user_courses", back_populates="users")
    messages = relationship("Message", back_populates="user")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.username:
            fake = Faker()
            self.username = f"{fake.first_name()} {fake.last_name()}"

    async def __admin_repr__(self, request: Request):
        return self.username


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, Users, OAuthAccount)


class Course(Base):
    __tablename__ = "courses"

    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    default_prompt = Column(String, nullable=False)

    users = relationship("Users", secondary="user_courses", back_populates="courses")
    messages = relationship("Message", back_populates="course")

    async def __admin_repr__(self, request: Request):
        return self.title


class UserCourses(Base):
    __tablename__ = "user_courses"

    user_id = Column(GUID, ForeignKey("user.id"), primary_key=True)
    course_id = Column(BigInteger, ForeignKey("courses.id"), primary_key=True)


class TypeEnum(PyEnum):
    ai = "ai"
    user = "user"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            return cls(value.lower())
        return super()._missing_(value)


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    text = Column(String, nullable=False)
    type = Column(Enum(TypeEnum), nullable=False)
    course_id = Column(BigInteger, ForeignKey("courses.id"), nullable=False)
    user_id = Column(GUID, ForeignKey("user.id"), nullable=False)

    user = relationship("Users", back_populates="messages")
    materials = relationship(
        "Material", back_populates="message", cascade="all, delete", lazy="joined"
    )
    test = relationship(
        "Test",
        back_populates="message",
        uselist=False,
        cascade="all, delete",
        lazy="joined",
    )
    course = relationship("Course", back_populates="messages")

    async def __admin_repr__(self, request: Request):
        return f"Message: {self.text[:20]}.."


class Material(Base):
    __tablename__ = "materials"

    id = Column(BigInteger, primary_key=True)
    url = Column(String, nullable=False)
    message_id = Column(
        BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )

    message = relationship("Message", back_populates="materials")

    async def __admin_repr__(self, request: Request):
        return f"Material: {self.url[:20]}.."


class Test(Base):
    __tablename__ = "tests"

    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False)
    message_id = Column(
        BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )

    message = relationship("Message", back_populates="test")
    questions = relationship(
        "Question", back_populates="test", cascade="all, delete", lazy="joined"
    )

    async def __admin_repr__(self, request: Request):
        return f"Test: {self.title}"


class Question(Base):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    test_id = Column(
        BigInteger, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False
    )

    test = relationship("Test", back_populates="questions")

    async def __admin_repr__(self, request: Request):
        return f"Question: {self.text}"
