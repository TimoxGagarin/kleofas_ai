from fastapi import Request, Response
from fastapi.templating import Jinja2Templates
from starlette_admin import CustomView, DateTimeField, EmailField
from starlette_admin.contrib.sqla import ModelView

from api.src.settings import settings


class UserView(ModelView):
    fields = [
        "id",
        "username",
        EmailField("email"),
        "is_active",
        "avatar_id",
        "is_superuser",
        "is_verified",
        DateTimeField("created_at"),
    ]
    row_actions = ["view", "edit"]
    label = "Users"
    exclude_fields_from_list = ["hashed_password", "oauth_accounts"]
    searchable_fields = ["id", "username", "email"]
    exclude_fields_from_detail = ["hashed_password"]
    exclude_fields_from_edit = ["hashed_password", "created_at", "avatar_id", "email"]

    def can_create(self, request: Request) -> bool:
        return False


class OAuthAccountView(ModelView):
    row_actions = ["view"]
    label = "OAuth accounts"
    exclude_fields_from_list = [
        "access_token",
        "expires_at",
        "refresh_token",
        "account_id",
    ]
    searchable_fields = ["id", "oauth_name", "account_email"]
    exclude_fields_from_detail = ["hashed_password"]
    exclude_fields_from_edit = ["hashed_password", "created_at", "avatar_id", "email"]

    def can_create(self, request: Request) -> bool:
        return False


class MessageView(ModelView):
    label = "Messages"


class CourseView(ModelView):
    label = "Courses"


class TestView(ModelView):
    label = "Tests"


class MaterialView(ModelView):
    label = "Materials"


class FlowerView(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            name=self.template_path,
            context={"request": request, "flower_url": settings.FLOWER_URL},
        )
