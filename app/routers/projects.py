import os
import random
import uuid
from typing import List
from tortoise.expressions import Q
from tortoise.functions import Count
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Body, status, Query

from app.core.project import fuzzy_multiword_search, shorter
from app.core.deps import CurrentUserDep, OptionalUserDep
from app.schemas.project import CreateProjectData, ShortProjectOut
from app.models.models import Project, ProjectLike, ProjectShare, ProjectView
from app.core.config import settings


router = APIRouter()


@router.post(path="/project", status_code=status.HTTP_201_CREATED)
async def create_project(
    user: CurrentUserDep,
    project: CreateProjectData = Body(...),
):
    blocks = project.blocks
    if len(blocks) < 2:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Blocks length too small"
        )

    if not (
        blocks[0].type == "header"
        and blocks[0].data.get("level", 0) == 3
        and len(blocks[0].data.get("text", "")) > 5
        and len(blocks[0].data.get("text", "")) < 50
        and blocks[1].type == "header"
        and blocks[1].data.get("level", 0) == 5
        and len(blocks[1].data.get("text", "")) > 10
        and len(blocks[1].data.get("text", "")) < 500
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Invalid blocks"
        )

    project_title = blocks[0].data.get("text")
    project_subtitle = shorter(blocks[1].data.get("text"))

    project_image_url = None
    for block in blocks:
        file_data = block.data.get("file", None)
        if file_data:
            project_image_url = file_data.get("url")[0]
            break

    serialized_blocks = [block.model_dump() for block in blocks]
    await Project.create(
        user=user,
        data=serialized_blocks,
        title=project_title,
        subtitle=project_subtitle,
        image_url=project_image_url,
        required_funds=project.requiredFunds,
    )

    return JSONResponse(content="Project created")


@router.get(path="/my-projects", status_code=200, response_model=List[ShortProjectOut])
async def get_my_projects(
    user: CurrentUserDep,
):
    projects = await Project.filter(user=user).prefetch_related("user").all()

    return projects


@router.get(path="/project/{id}", status_code=status.HTTP_200_OK)
async def get_project(id: uuid.UUID, user: OptionalUserDep):
    project = await Project.filter(id=id).prefetch_related("user").first()
    if project:
        if user:
            await ProjectView.get_or_create(user=user, project=project)
        liked = False
        if user:
            liked = await ProjectLike.filter(user=user, project=project).exists()

        likes_count = await ProjectLike.filter(project=project).count()
        shares_count = await ProjectShare.filter(project=project).count()
        views_count = await ProjectView.filter(project=project).count()

        project_out_data = {
            "id": project.id,
            "user": {
                "id": project.user.id,
                "telegram_id": project.user.telegram_id,
                "username": project.user.username,
                "first_name": project.user.first_name,
                "last_name": project.user.last_name,
            },
            "data": project.data,
            "views_count": views_count,
            "likes_count": likes_count,
            "shares_count": shares_count,
            "created_time": project.created_time,
            "liked": liked,
            "required_funds": project.required_funds,
        }

        return project_out_data
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content="Project not found",
    )


@router.delete(path="/project/{id}", status_code=status.HTTP_200_OK)
async def delete_project(user: CurrentUserDep, id: uuid.UUID):
    project = await Project.filter(id=id).first()
    if project:
        for item in project.data:
            if item['type'] == "image":
                urls = item['data']['file']['url']
                for url in urls:
                    relative_path = url.split("/api/")[1]
                    try:
                        os.remove(os.path.join(settings.BASE_DIR, relative_path))
                    except:
                        pass
        await project.delete()
        return {"message": "Deleted"}
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content="Project not found",
    )


@router.put(path="/project/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_project(
    user: CurrentUserDep, id: uuid.UUID, project: CreateProjectData = Body(...)
):
    project_in_base = await Project.filter(id=id).prefetch_related("user").first()
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="Project not found"
        )
    if project_in_base.user != user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content="Project is not yours"
        )
    blocks = project.blocks
    if len(blocks) < 2:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Blocks length too small"
        )

    if not (
        blocks[0].type == "header"
        and blocks[0].data.get("level", 0) == 3
        and len(blocks[0].data.get("text", "")) > 5
        and len(blocks[0].data.get("text", "")) < 50
        and blocks[1].type == "header"
        and blocks[1].data.get("level", 0) == 5
        and len(blocks[1].data.get("text", "")) > 10
        and len(blocks[1].data.get("text", "")) < 500
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Invalid blocks"
        )

    project_title = blocks[0].data.get("text")
    project_subtitle = shorter(blocks[1].data.get("text"))

    project_image_url = None
    for block in blocks:
        file_data = block.data.get("file", None)
        if file_data:
            project_image_url = file_data.get("url")[0]

    serialized_blocks = [block.model_dump() for block in blocks]

    project_in_base.data = serialized_blocks
    project_in_base.title = project_title
    project_in_base.subtitle = project_subtitle
    project_in_base.image_url = project_image_url
    project_in_base.required_funds = project.requiredFunds
    await project_in_base.save()

    return JSONResponse(status_code=status.HTTP_200_OK, content="Project updated")


@router.get(path="/most-viewed", response_model=List[ShortProjectOut])
async def get_most_viewed_projects():
    projects = (
        await Project.annotate(views_count=Count("views"))
        .prefetch_related("user")
        .order_by("-views_count")
        .limit(5)
    )

    return projects


@router.get(path="/most-liked", response_model=List[ShortProjectOut])
async def get_most_liked_projects():
    projects = (
        await Project.annotate(likes_count=Count("likes"))
        .prefetch_related("user")
        .order_by("-likes_count")
        .limit(5)
    )

    return projects


@router.get(path="/search", response_model=List[ShortProjectOut])
async def search_project(q: str = Query(..., min_length=3, max_length=20)):
    projects = await fuzzy_multiword_search(q)
    if projects == []:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="No projects like that"
        )
    projects = [ShortProjectOut(**row) for row in projects]
    return projects
