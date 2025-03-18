from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.src.controllers.courses import router as course_router
from api.src.controllers.materials import router as material_router
from api.src.controllers.messages import router as message_router
from api.src.controllers.tests import router as test_router
from api.src.controllers.users import router as user_router

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
