import hashlib
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.redis_client import redis_client

settings = get_settings()


def verify_signature(signature: str, timestamp: str, nonce: str) -> bool:
    token = settings.wechat_token
    values = sorted([token, timestamp, nonce])
    digest = hashlib.sha1(''.join(values).encode('utf-8')).hexdigest()
    return digest == signature


def _token_cache_key() -> str:
    return f'wechat:access_token:{settings.wechat_app_id}'


def get_access_token(force_refresh: bool = False) -> str:
    cache_key = _token_cache_key()
    if not force_refresh:
        cached = redis_client.get(cache_key)
        if cached:
            return cached

    if not settings.wechat_app_id or not settings.wechat_app_secret:
        raise RuntimeError('wechat credentials are not configured')

    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            f'{settings.wechat_api_base}/cgi-bin/token',
            params={
                'grant_type': 'client_credential',
                'appid': settings.wechat_app_id,
                'secret': settings.wechat_app_secret,
            },
        )
        response.raise_for_status()
        payload = response.json()

    access_token = payload.get('access_token')
    expires_in = int(payload.get('expires_in', 7200))
    if not access_token:
        raise RuntimeError(f'failed to get access token: {payload}')

    redis_client.set(cache_key, access_token, ex=max(60, expires_in - 120))
    return access_token


def send_text_message(openid: str, content: str) -> dict[str, Any]:
    token = get_access_token()
    payload = {
        'touser': openid,
        'msgtype': 'text',
        'text': {'content': content},
    }
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            f'{settings.wechat_api_base}/cgi-bin/message/custom/send',
            params={'access_token': token},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    if data.get('errcode', 0) != 0:
        raise RuntimeError(f"wechat send failed: {data}")

    return data
