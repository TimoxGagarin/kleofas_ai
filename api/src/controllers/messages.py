from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.src.dao.materials import MaterialsDAO
from api.src.dao.messages import MessagesDAO
from api.src.dao.questions import QuestionsDAO
from api.src.dao.tests import TestsDAO
from api.src.exceptions import MessageDoesntExists
from api.src.schemas.messages import CreateMessage, DisplayMessage
from api.src.schemas.questions import DisplayQuestion
from api.src.schemas.tests import DisplayTest
from api.src.utils.sessions import admin_required, get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_message(message: CreateMessage, user: Annotated[dict, Depends(get_current_user)]) -> DisplayMessage:
    new_message = await MessagesDAO.add(user_id=user["id"], text=message.text, type=message.type, course_id=message.course_id)

    new_materials = None
    if message.materials:
        new_materials = await MaterialsDAO.add_all(new_message.id, [m.model_dump() for m in message.materials])

    new_test = None
    display_test = None
    new_questions = []
    if message.test:
        new_test = await TestsDAO.add(message_id=new_message.id, title=message.test.title)
        if message.test.questions:
            new_questions = await QuestionsDAO.add_all(new_test.id, [q.model_dump() for q in message.test.questions])
        display_questions = [DisplayQuestion(**question.to_dict()) for question in new_questions]
        display_test = DisplayTest(
            id=new_test.id,
            title=new_test.title,
            message_id=new_message.id,
            questions=display_questions,
            created_at=new_test.created_at,
        )

    return DisplayMessage(
        id=new_message.id,
        type=new_message.type,
        course_id=new_message.course_id,
        text=new_message.text,
        user_id=new_message.user_id,
        materials=new_materials,
        test=display_test,
        created_at=new_message.created_at,
    )


@router.get("")
async def get_messages(
    course_id: int,
    user_id: int,
    offset: int | None = None,
    limit: int | None = None,
    *,
    admin: Annotated[dict, Depends(admin_required)]
):
    return await MessagesDAO.find_all(course_id=course_id, user_id=user_id, offset=offset, limit=limit)


@router.get("/{message_id}")
async def get_message(message_id: int, user: Annotated[dict, Depends(admin_required)]):
    message = await MessagesDAO.find_by_id(message_id)
    if not message:
        raise MessageDoesntExists
    return message
