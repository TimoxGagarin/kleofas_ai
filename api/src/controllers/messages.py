from collections import defaultdict
from typing import Annotated, Any

from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect, status

from api.src.controllers.base import BaseRouter
from api.src.controllers.users import get_current_active_user
from api.src.dao.materials import MaterialsDAO
from api.src.dao.messages import MessagesDAO
from api.src.dao.questions import QuestionsDAO
from api.src.dao.tests import TestsDAO
from api.src.dao.user_courses import UserCoursesDAO
from api.src.dao.users import UsersDAO
from api.src.db.models import TypeEnum
from api.src.db.redis import redis
from api.src.exceptions import CourseDoesntExists
from api.src.schemas.messages import (
    CreateMessage,
    DisplayMessage,
    SearchMessage,
)
from api.src.schemas.questions import DisplayQuestion
from api.src.schemas.tests import DisplayTest
from api.src.schemas.users import DisplayUser


class MessageRouter(BaseRouter):
    def entity__create(self, summary):
        @self.post("", status_code=status.HTTP_201_CREATED, summary=summary)
        async def create_message(
            message: CreateMessage,
            user: Annotated[DisplayUser, Depends(get_current_active_user)],
        ) -> DisplayMessage:
            new_message = await MessagesDAO.add(
                user_id=user.id,
                text=message.text,
                type=message.type,
                course_id=message.course_id,
            )

            new_materials = None
            if message.materials:
                new_materials = await MaterialsDAO.add_all(
                    new_message.id, [m.model_dump() for m in message.materials]
                )

            new_test = None
            display_test = None
            new_questions = []
            if message.test:
                new_test = await TestsDAO.add(
                    message_id=new_message.id, title=message.test.title
                )
                if message.test.questions:
                    new_questions = await QuestionsDAO.add_all(
                        new_test.id, [q.model_dump() for q in message.test.questions]
                    )
                display_questions = [
                    DisplayQuestion(**question.to_dict()) for question in new_questions
                ]
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


router = MessageRouter(
    entity_name="Message",
    entity_dao=MessagesDAO,
    create_entity=CreateMessage,
    display_entity=DisplayMessage,
    search_entity=SearchMessage,
    prefix="/messages",
    tags=["messages"],
)

connected_clients = defaultdict(list)


@router.websocket("/chat/{course_id}")
async def user_course_chat(websocket: WebSocket, course_id: int):
    try:
        await websocket.accept()
        token = await websocket.receive_text()
        user_id = await redis.get(f"fastapi_users_token:{token}")
        user = await UsersDAO.find_by_id(user_id)
        users_course = await UserCoursesDAO.find_one_or_none(
            course_id=course_id, user_id=user_id
        )
        if not users_course:
            raise CourseDoesntExists
        connected_clients[course_id].append(websocket)

        offset = 0
        PAGE_SIZE = 20

        async def prepare_message_data(message: Any, user_data: Any = None) -> dict:
            return {
                "user": DisplayUser.model_validate(
                    user_data or message.user
                ).model_dump(mode="json"),
                "message": DisplayMessage.model_validate(message).model_dump(
                    mode="json"
                ),
                "type": message.type.value,
            }

        async def send_messages_to_clients(
            clients: list, message_type: str, messages_data: list
        ):
            for client in clients:
                await client.send_json({"type": message_type, "results": messages_data})

        try:
            while True:
                data = await websocket.receive_text()

                if data in ("load_init", "load_prev"):
                    if data == "load_prev":
                        offset += PAGE_SIZE

                    messages = await MessagesDAO.find_all_with_user(
                        offset=offset, limit=PAGE_SIZE, course_id=course_id
                    )
                    ready_messages = [
                        await prepare_message_data(msg) for msg in messages
                    ]
                    await send_messages_to_clients([websocket], data, ready_messages)

                else:
                    message_text = data[5:]
                    user_message = await MessagesDAO.add(
                        text=message_text,
                        type=TypeEnum.user,
                        course_id=course_id,
                        materials=[],
                        test=None,
                        user_id=user_id,
                    )

                    user_message_data = await prepare_message_data(user_message, user)
                    await send_messages_to_clients(
                        connected_clients[course_id], "new_message", [user_message_data]
                    )

                    ai_message = await MessagesDAO.add(
                        text="Hello kek!!!",
                        type=TypeEnum.ai,
                        course_id=course_id,
                        materials=[],
                        test=None,
                        user_id=user_id,
                    )
                    ai_message_data = await prepare_message_data(ai_message, user)
                    await send_messages_to_clients(
                        connected_clients[course_id], "new_message", [ai_message_data]
                    )

        except WebSocketDisconnect:
            connected_clients[course_id].remove(websocket)
            if not connected_clients[course_id]:
                del connected_clients[course_id]

    except HTTPException as e:
        await websocket.close(code=e.status_code, reason=e.detail)
