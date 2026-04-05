from fastapi import Header, HTTPException

from app.core.config import get_settings


settings = get_settings()


def verify_admin_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail='invalid api key')
