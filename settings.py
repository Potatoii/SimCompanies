import os.path
from typing import Optional, List

from pydantic import Field

from toml_settings import TomlSettings

root_path = os.path.dirname(os.path.abspath(__file__))


class LogSettings(TomlSettings):
    __table_name__ = "log"
    log_name: str = "simbot.log"
    stdout_level: str = "INFO"
    file_level: str = "INFO"


class UserSettings(TomlSettings):
    __table_name__ = "user"
    email: str
    password: str


class MailSettings(TomlSettings):
    __table_name__ = "notice.mail"
    host: Optional[str] = Field(required=False, default="smtp.qq.com")
    port: Optional[int] = Field(required=False, default=465)
    username: Optional[str] = Field(required=False, default="")
    password: Optional[str] = Field(required=False, default="")


class BarkSettings(TomlSettings):
    __table_name__ = "notice.bark"
    bark_key: Optional[str] = Field(required=False, default="")


class NoticeSettings(TomlSettings):
    __table_name__ = "notice"
    mail: MailSettings = MailSettings()
    bark: BarkSettings = BarkSettings()


class MarketSettings(TomlSettings):
    __table_name__ = "market"
    item_list: Optional[List] = Field(required=False, default=[])


log_config = LogSettings()
user_config = UserSettings()
notice_config = NoticeSettings()
market_config = MarketSettings()
