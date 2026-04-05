from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'wx-content-assistant'
    app_env: str = 'dev'
    app_port: int = 8000

    database_url: str
    redis_url: str

    admin_api_key: str = 'dev-admin-key'

    wechat_token: str = ''
    wechat_app_id: str = ''
    wechat_app_secret: str = ''
    wechat_aes_key: str = ''
    wechat_api_base: str = 'https://api.weixin.qq.com'


@lru_cache
def get_settings() -> Settings:
    return Settings()
