import hashlib
import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

from app.services import wechat_service


def test_verify_signature_success():
    wechat_service.settings.wechat_token = 'test-token'
    timestamp = '1710000000'
    nonce = 'xyz'
    raw = ''.join(sorted(['test-token', timestamp, nonce]))
    signature = hashlib.sha1(raw.encode('utf-8')).hexdigest()
    assert wechat_service.verify_signature(signature, timestamp, nonce)


def test_verify_signature_fail():
    wechat_service.settings.wechat_token = 'test-token'
    assert wechat_service.verify_signature('invalid', '1', '2') is False
