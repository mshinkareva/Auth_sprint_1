from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    db_host: str = ...
    db_port: str = ...

    service_url: str = ...


class DatabaseSettings(BaseSettings):
    name: str = Field(..., env='POSTGRES_DB')
    user: str = ...
    password: str = ...
    host: str = ...
    port: int = ...

    class Config:
        env_prefix = 'postgres_'
        env_file = (
            '/Users/mariya.shinkareva/PycharmProjects/new_admin_panel_sprint_3/.env'
        )
        env_file_encoding = 'utf-8'


test_settings = TestSettings()
