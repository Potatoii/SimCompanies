import os.path
from typing import Optional

from pydantic import Field

from toml_settings import TomlSettings

root_path = os.path.dirname(os.path.abspath(__file__))


class LogSettings(TomlSettings):
    log_name: str = "simbot.log"
    stdout_level: str = "INFO"
    file_level: str = "INFO"


class UserSettings(TomlSettings):
    email: str
    password: str


class MailSettings(TomlSettings):
    host: Optional[str] = Field(required=False, default="smtp.qq.com")
    port: Optional[int] = Field(required=False, default=465)
    username: Optional[str] = Field(required=False, default="")
    password: Optional[str] = Field(required=False, default="")


class BarkSettings(TomlSettings):
    bark_key: Optional[str]


class NoticeSettings(TomlSettings):
    mail: MailSettings = MailSettings()
    bark: BarkSettings = BarkSettings()


log_config = LogSettings()
user_config = UserSettings()
notice_config = NoticeSettings()
