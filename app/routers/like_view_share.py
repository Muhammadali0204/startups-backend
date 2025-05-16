from uuid import UUID
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from tortoise.exceptions import OperationalError

from app.core.deps import CurrentUserDep
from app.models.models import Project, ProjectLike, ProjectShare


router = APIRouter()


@router.post("/set-like/{project_id}")
async def toggle_like(user: CurrentUserDep, project_id: UUID):
    project = await Project.filter(id=project_id).first()
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Project not found"},
        )

    like = await ProjectLike.filter(user=user, project=project).first()
    if like:
        await like.delete()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Disliked"},
        )
    try:
        await ProjectLike.create(user=user, project=project)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"detail": "Liked"},
        )
    except OperationalError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Unexpected error"},
        )


@router.post("/set-share/{project_id}")
async def set_share(user: CurrentUserDep, project_id: str):
    project = await Project.filter(id=project_id).first()
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Project not found"},
        )

    exists = await ProjectShare.filter(user=user, project=project).exists()

    if not exists:
        try:
            await ProjectShare.create(user=user, project=project)
        except OperationalError:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": "Database error"},
            )
    else:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={"detail": "Already shared"},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Project shared"},
    )
