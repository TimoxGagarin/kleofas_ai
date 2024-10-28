from fastapi import FastAPI

from api.src.controllers.sso import router as sso_router

app = FastAPI()

app.include_router(sso_router)
