from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = 'Some project name'
    redis_host: str = ...
    redis_port: int = ...

    postgres_name: str = ...
    postgres_user: str = ...
    postgres_password: str = ...
    postgres_host: str = ...
    postgres_port: str = ...

    def pg_url(self):
        return f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_name}'


settings = Settings()
