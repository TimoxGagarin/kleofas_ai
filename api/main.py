from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette_admin.contrib.sqla import Admin

from api.src.admin.auth import UsernameAndPasswordProvider
from api.src.admin.views import (
    CourseView,
    FlowerView,
    MaterialView,
    MessageView,
    OAuthAccountView,
    TestView,
    UserView,
)
from api.src.controllers.courses import router as course_router
from api.src.controllers.materials import router as material_router
from api.src.controllers.messages import router as message_router
from api.src.controllers.tests import router as test_router
from api.src.controllers.users import router as user_router
from api.src.db.config import async_engine
from api.src.db.models import Course, Material, Message, OAuthAccount, Test, Users

app = FastAPI()

app.mount("/files", StaticFiles(directory="files"), name="files")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(message_router)
app.include_router(course_router)
app.include_router(user_router)
app.include_router(test_router)
app.include_router(material_router)

admin = Admin(
    async_engine,
    auth_provider=UsernameAndPasswordProvider(),
    templates_dir="api/templates/starlette_admin",
)

admin.add_view(UserView(Users))
admin.add_view(OAuthAccountView(OAuthAccount))
admin.add_view(MessageView(Message))
admin.add_view(CourseView(Course))
admin.add_view(TestView(Test))
admin.add_view(MaterialView(Material))
admin.add_view(
    FlowerView(
        label="Flower",
        icon="fa-solid fa-seedling",
        path="/flower",
        template_path="flower.html",
    )
)

admin.mount_to(app)
