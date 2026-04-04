from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    telegram_bot_token: str = Field(default='', alias='TELEGRAM_BOT_TOKEN')
    public_base_url: str = Field(default='http://127.0.0.1:8000', alias='PUBLIC_BASE_URL')
    backend_host: str = Field(default='127.0.0.1', alias='BACKEND_HOST')
    backend_port: int = Field(default=8000, alias='BACKEND_PORT')
    city_name: str = Field(default='Baku', alias='CITY_NAME')


settings = Settings()
