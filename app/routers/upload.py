import os
import shutil
from fastapi.responses import JSONResponse
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.deps import CurrentUserDep


router = APIRouter()


@router.post("/uploadImage")
async def upload_image(user: CurrentUserDep, file: UploadFile = File(...)):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="invalid image type")

    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="invalid image type")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="invalid image size")

    safe_filename = f"{os.urandom(8).hex()}.{file_ext}"
    file_location = f"{settings.BASE_DIR}/{settings.UPLOAD_DIR}/images/{safe_filename}"

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="error during saving")

    return JSONResponse(
        content={
            "success": 1,
            "file": {
                "url": (
                    f"https://{settings.ORIGIN}/api/{settings.UPLOAD_DIR}"
                    f"/images/{safe_filename}",
                )
            },
        }
    )


@router.post("/fetch")
async def fetch(url: str = Form(...)):
    return JSONResponse(content={"success": 1, "file": {"url": url}})
