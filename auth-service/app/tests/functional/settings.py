from pydantic import BaseSettings, Field

import dotenv


dotenv.load_dotenv("/Users/mariya.shinkareva/PycharmProjects/Auth_sprint_1/auth-service/env/.tests.env")


class TestSettings(BaseSettings):
    postgres_db: str = Field(..., env='POSTGRES_DB')
    postgres_host: str = ...
    postgres_port: str = ...
    postgres_password: str = ...
    postgres_user: str = ...

    service_url: str = ...


class DatabaseSettings(BaseSettings):
    db: str = Field(..., env='POSTGRES_DB')
    user: str = ...
    password: str = ...
    host: str = ...
    port: int = ...


test_settings = TestSettings()

