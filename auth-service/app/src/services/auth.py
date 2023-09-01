from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from redis.asyncio import Redis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.postgres import get_session
from src.db.redis import get_redis
from src.models.user import User
from src.services.const import CACHE_EXPIRE_REFRESH_TOKEN


class AuthService:
    def __init__(self, redis: Redis, pg: AsyncSession):
        self.redis = redis
        self.pg = pg

    async def get_by_login(self, login: str) -> User | None:
        result = await self.pg.execute(select(User).where(User.login == login))
        user_found = result.scalars().first()
        return user_found if user_found else None

    async def get_by_mail(self, mail: str) -> User | None:
        result = await self.pg.execute(select(User).where(User.email == mail))
        user_found = result.scalars().first()
        return user_found if user_found else None

    async def check_password(self, login: str, password: str) -> bool:
        result = await self.pg.execute(
            select(User).where((User.password == password) & (User.login == login))
        )
        return bool(result)

    async def add_user(self, user):
        self.pg.add(user)
        await self.pg.commit()
        await self.pg.refresh(user)

    async def add_jwt_to_redis(self, login: str, jwt_val: str):
        self.redis.set(f'{login}::{jwt_val}', jwt_val, CACHE_EXPIRE_REFRESH_TOKEN)

    async def revoke_both_tokens(self, login, authorize: AuthJWT) -> None:
        refresh_jti = (await authorize.get_raw_jwt())['jti']
        access_jti = (await authorize.get_raw_jwt())['access_jti']
        await self.add_jwt_to_redis(login, access_jti)
        await self.add_jwt_to_redis(login, refresh_jti)


@lru_cache()
def get_auth_service(
    redis: Redis = Depends(get_redis),
    pg: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(redis, pg)
