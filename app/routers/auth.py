import time
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status

from app.models.models import User
from app.schemas.user import UserTelegramData
from app.core.auth import verify_telegram_hash, create_access_token


router = APIRouter()


@router.post("/telegram-login")
async def auth_user(user: UserTelegramData):
    user_dict = user.__dict__

    if not verify_telegram_hash(user_dict, user.hash):
        raise HTTPException(status_code=400, detail="Invalid hash")

    if time.time() - user.auth_date > 1800:  # 30 daqiqa
        raise HTTPException(status_code=400, detail="Login expired")

    user_in_base = await User.get_or_none(telegram_id=user.id)
    new = False

    telegram_id = user_dict.pop("id")

    if not user_in_base:
        user_in_base = await User.create(**user_dict, telegram_id=telegram_id)
        new = True
    else:
        user_in_base.update_from_dict(user_dict)
        await user_in_base.save()

    access_token, expire = create_access_token(user_id=user_in_base.id)

    response = JSONResponse(
        content={
            "success": True,
            "access_token": access_token,
            "expiresAt": expire.isoformat(),
            "is_new": new,
            "user": {
                "telegram_id": user_in_base.telegram_id,
                "first_name": user_in_base.first_name,
                "last_name": user_in_base.last_name,
                "username": user_in_base.username,
                "photo_url": user_in_base.photo_url,
            },
        },
        status_code=status.HTTP_201_CREATED if new else status.HTTP_200_OK,
    )

    return response
