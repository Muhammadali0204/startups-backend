from fastapi import APIRouter

from app.routers import like_view_share

from . import auth
from . import upload
from . import projects

router = APIRouter()

router.include_router(upload.router, tags=["Upload"])
router.include_router(auth.router, prefix="/auth", tags=["User Auth"])
router.include_router(projects.router, prefix="/projects", tags=["Projects"])
router.include_router(
    like_view_share.router,
    prefix="/set-project",
    tags=["Set Project like,share,view count"],
)
