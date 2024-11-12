import json
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from api.src.constants import avaliable_sso
from api.src.dao.sso import SSODAO
from api.src.dao.users import UsersDAO
from api.src.db.models import User
from api.src.exceptions import UnknownSSOProvider
from api.src.schemas.sso import CreateSSO, UpdateSSO
from api.src.schemas.users import DisplayUser
from api.src.settings import settings
from api.src.utils.sessions import admin_required, create_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/add", status_code=status.HTTP_204_NO_CONTENT)
async def add_provider(provider: CreateSSO, admin: Annotated[dict, Depends(admin_required)]):
    if provider.name not in avaliable_sso:
        raise UnknownSSOProvider
    provider = await SSODAO.add(**provider.model_dump())
    if not provider:
        raise UnknownSSOProvider


@router.patch("/patch", status_code=status.HTTP_204_NO_CONTENT)
async def update_provider(provider: UpdateSSO, admin: Annotated[dict, Depends(admin_required)]):
    if provider.name not in avaliable_sso:
        raise UnknownSSOProvider
    provider = await SSODAO.update(**provider.model_dump())
    if not provider:
        raise UnknownSSOProvider


@router.get("/{sso_provider}/login")
async def sso_login(sso_provider: str):
    provider_model = await SSODAO.find_one_or_none(name=sso_provider)
    if not provider_model or sso_provider not in avaliable_sso:
        raise UnknownSSOProvider
    provider = avaliable_sso[sso_provider](
        client_id=provider_model.client_id,
        client_secret=provider_model.client_secret,
        redirect_uri=f"http://{settings.BASE_URL}/auth/{sso_provider}/callback",
    )
    return await provider.get_login_redirect()


@router.get("/{sso_provider}/callback")
async def sso_callback(response: Response, request: Request, sso_provider: str) -> DisplayUser:
    provider_model = await SSODAO.find_one_or_none(name=sso_provider)
    if not provider_model or sso_provider not in avaliable_sso:
        raise UnknownSSOProvider
    provider = avaliable_sso[sso_provider](
        client_id=provider_model.client_id,
        client_secret=provider_model.client_secret,
        redirect_uri=f"http://{settings.BASE_URL}/auth/{sso_provider}/callback",
    )
    user = await provider.verify_and_process(request)

    user_model = await UsersDAO.find_one_or_none(user_id=int(user.id), sso_type=provider_model.id)
    user_schema = {
        "user_id": int(user.id),
        "sso_type": provider_model.id,
        "username": user.display_name,
        "avatar": user.picture,
        "email": user.email,
    }

    if not user_model:
        user: User = await UsersDAO.add(is_admin=False, is_enabled=True, **user_schema)
    else:
        user = await UsersDAO.update(**user_schema)

    def default_converter(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    session_id = await create_session(json.dumps(user.to_dict(), default=default_converter))
    response.set_cookie(key=settings.SESSION_COOKIE_NAME, value=session_id, httponly=True)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response):
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if session_id:
        await settings.redis.delete(session_id)
        response.delete_cookie(settings.SESSION_COOKIE_NAME)
