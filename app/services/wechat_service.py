import hashlib
from typing import Any

from app.core.config import get_settings

settings = get_settings()


def verify_signature(signature: str, timestamp: str, nonce: str) -> bool:
    token = settings.wechat_token
    values = sorted([token, timestamp, nonce])
    digest = hashlib.sha1(''.join(values).encode('utf-8')).hexdigest()
    return digest == signature


def build_text_reply(content: str) -> dict[str, Any]:
    return {'msgtype': 'text', 'text': {'content': content}}
