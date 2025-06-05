from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import settings
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/telegram-login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    auth_exception = HTTPException(status_code=401, detail="Authentication is required")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        user_id = payload.get("user_id")
        if not user_id:
            raise auth_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="api/auth/telegram-login", auto_error=False
)


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
) -> Optional[User]:
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        user_id = payload.get("user_id")
        if not user_id:
            return None
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None

    user = await User.get_or_none(id=user_id)
    return user


OptionalUserDep = Annotated[Optional[User], Depends(get_optional_user)]
