import json
from uuid import uuid4

from fastapi import Depends, Request

from api.src.exceptions import AdminAccessRequired, SessionNotFound, Unauthorized
from api.src.settings import settings


async def get_session_data(session_id: str):
    session_data = await settings.redis.get(session_id)
    if session_data is None:
        raise SessionNotFound
    return json.loads(session_data)


async def create_session(data: dict):
    session_id = str(uuid4())
    await settings.redis.set(session_id, json.dumps(data))
    await settings.redis.expire(session_id, 3600)
    return session_id


async def get_current_user(request: Request):
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not session_id:
        raise Unauthorized
    return json.loads(await get_session_data(session_id))


async def admin_required(user_data: dict = Depends(get_current_user)):
    if not user_data.get("is_admin"):
        raise AdminAccessRequired
    return user_data
