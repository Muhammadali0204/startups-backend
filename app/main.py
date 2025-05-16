from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from tortoise.contrib.fastapi import register_tortoise

from app.routers.main import router
from app.core.config import DATABASE_CONFIG, settings


app = FastAPI(openapi_version="3.1.0")

app.mount(
    "/uploads",
    StaticFiles(directory=f"{settings.BASE_DIR}/{settings.UPLOAD_DIR}"),
    name="uploads",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(app, config=DATABASE_CONFIG, generate_schemas=True)

app.include_router(router)
