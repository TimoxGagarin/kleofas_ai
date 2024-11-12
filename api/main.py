from fastapi import FastAPI

from api.src.controllers.courses import router as course_router
from api.src.controllers.materials import router as material_router
from api.src.controllers.messages import router as message_router
from api.src.controllers.sso import router as sso_router
from api.src.controllers.tests import router as test_router
from api.src.controllers.users import router as user_router

app = FastAPI()

app.include_router(sso_router)
app.include_router(message_router)
app.include_router(course_router)
app.include_router(user_router)
app.include_router(test_router)
app.include_router(material_router)
