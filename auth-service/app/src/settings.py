import os

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    project_name: str = ...
    redis_host: str = ...
    redis_port: int = ...

    postgres_db: str = ...
    postgres_user: str = ...
    postgres_password: str = ...
    postgres_host: str = ...
    postgres_port: str = ...

    postgres_engine_echo: bool = False

    authjwt_secret_key: str = "secretfghjrtyui"
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    access_expires: int = 900  # 15 min
    refresh_expires: int = 1800  # 30 min

    jaeger_agent_host: str = Field('jaegertracing', env='JAEGER_AGENT_HOST')
    jaeger_agent_port: int = Field(6831, env='JAEGER_AGENT_PORT')

    def pg_url(self):
        return f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'


settings = Settings(_env_file=os.getenv('ENV_FILE'))
