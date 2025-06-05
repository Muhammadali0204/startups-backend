import hmac
import hashlib
import datetime

from jose import jwt

from .config import settings


def verify_telegram_hash(data: dict, received_hash: str) -> bool:
    secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items()) if k != "hash" and v is not None
    )
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
    expected_hash = expected_hash.hexdigest()

    return hmac.compare_digest(expected_hash, received_hash)


def create_access_token(*, user_id: int) -> str:
    return _create_token(
        token_type="access_token",
        lifetime=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        user_id=user_id,
    )


def _create_token(
    token_type: str,
    lifetime: datetime.timedelta,
    user_id: int,
) -> str:
    payload = {}
    expire = datetime.datetime.now(datetime.timezone.utc) + lifetime
    payload["type"] = token_type
    payload["exp"] = expire
    payload["iat"] = datetime.datetime.now(datetime.UTC)
    payload["user_id"] = str(user_id)
    return (
        jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM),
        expire,
    )
