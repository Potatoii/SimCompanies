import tomllib
from typing import Any, Optional

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings, DotEnvSettingsSource,
    PydanticBaseSettingsSource
)
from pydantic_settings import SettingsConfigDict


class TomlSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_file="config.local.toml",
        extra="ignore"
    )

    def __init__(self, env_file: str = None):
        if env_file:
            self.model_config["env_file"] = env_file

        super().__init__()

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            TomlConfigSettingsSource(settings_cls, dotenv_settings),
        )


class TomlConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings], dotenv_settings: PydanticBaseSettingsSource):
        super().__init__(settings_cls)
        self.settings_cls = settings_cls
        self.config = settings_cls.model_config
        self.dotenv_settings = dotenv_settings

    def get_table_name(self) -> Optional[str]:
        if hasattr(self.settings_cls, "__table_name__"):
            return getattr(self.settings_cls, "__table_name__")
        return None

    def get_nested_value(self, dictionary, key):
        if isinstance(dictionary, dict):
            if key in dictionary:
                return dictionary[key]
            else:
                for k, v in dictionary.items():
                    result = self.get_nested_value(v, key)
                    if result is not None:
                        return result
        return None

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        table_name = self.get_table_name()
        env_file = self.config.get("env_file")

        if isinstance(self.dotenv_settings, DotEnvSettingsSource):
            env_file = env_file if env_file else self.dotenv_settings.env_file

        if not env_file:
            raise ValueError("No toml env_file")

        try:
            with open(env_file, "rb") as ft:
                file_content_toml = tomllib.load(ft)

                if table_name:
                    table_content = file_content_toml.get(table_name, {})
                    field_value = table_content.get(field_name)
                else:
                    field_value = self.get_nested_value(file_content_toml, field_name)

                return field_value, field_name, False
        except Exception as e:
            raise ValueError(f"Error on open f{env_file}: {e}") from e

    def prepare_field_value(
            self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(field, field_name)
            field_value = self.prepare_field_value(field_name, field, field_value, value_is_complex)
            if field_value is not None:
                d[field_key] = field_value

        return d
