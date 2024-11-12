from enum import Enum as PyEnum

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {k: self.__dict__[k] for k in self.__dict__ if "_sa_" != k[:4]}

    def __repr__(self):
        return f"""<{self.__class__.__name__}({[', '.join('%s=%s' % (k, self.__dict__[k])
                                             for k in self.__dict__ if '_sa_' != k[:4])]}"""


class SSOProvider(Base):
    __tablename__ = "sso_providers"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)

    users = relationship("User", back_populates="sso_provider")


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    sso_type = Column(BigInteger, ForeignKey("sso_providers.id"), nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    avatar = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False)
    is_enabled = Column(Boolean, nullable=False)

    sso_provider = relationship("SSOProvider", back_populates="users")
    courses = relationship("Course", secondary="user_courses", back_populates="users")
    messages = relationship("Message", back_populates="user")


class Course(Base):
    __tablename__ = "courses"

    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    default_prompt = Column(String, nullable=False)

    users = relationship("User", secondary="user_courses", back_populates="courses")
    messages = relationship("Message", back_populates="course")


class UserCourses(Base):
    __tablename__ = "user_courses"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
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
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="messages")
    materials = relationship("Material", back_populates="message")
    tests = relationship("Test", back_populates="message")
    course = relationship("Course", back_populates="messages")


class Material(Base):
    __tablename__ = "materials"

    id = Column(BigInteger, primary_key=True)
    url = Column(String, nullable=False)
    message_id = Column(BigInteger, ForeignKey("messages.id"), nullable=False)

    message = relationship("Message", back_populates="materials")


class Test(Base):
    __tablename__ = "tests"

    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False)
    message_id = Column(BigInteger, ForeignKey("messages.id"), nullable=False)

    message = relationship("Message", back_populates="tests")
    questions = relationship("Question", back_populates="test")


class Question(Base):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    test_id = Column(BigInteger, ForeignKey("tests.id"), nullable=False)

    test = relationship("Test", back_populates="questions")
