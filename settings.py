import os.path
from typing import Optional

from pydantic_settings import BaseSettings

root_path = os.path.dirname(os.path.abspath(__file__))


class LogSettings(BaseSettings):
    log_name: str = "simbot.log"
    stdout_level: str = "INFO"
    file_level: str = "INFO"

    class Config:
        env_file = "config.toml", "config.local.toml"
        extra = "ignore"


class UserSettings(BaseSettings):
    email: str
    password: str

    class Config:
        env_file = "config.toml", "config.local.toml"
        extra = "ignore"


class MailSettings(BaseSettings):
    host: Optional[str]
    port: Optional[int]
    username: Optional[str]
    password: Optional[str]

    class Config:
        env_file = "config.toml", "config.local.toml"
        extra = "ignore"


class BarkSettings(BaseSettings):
    bark_key: Optional[str]

    class Config:
        env_file = "config.toml", "config.local.toml"
        extra = "ignore"


class NoticeSettings(BaseSettings):
    mail: MailSettings = MailSettings()
    bark: BarkSettings = BarkSettings()

    class Config:
        env_file = "config.toml", "config.local.toml"
        extra = "ignore"


log_config = LogSettings()
user_config = UserSettings()
notice_config = NoticeSettings()

if __name__ == "__main__":
    print(log_config)
    print(user_config)
    print(notice_config)
