from functools import lru_cache
from typing import Optional

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from redis.asyncio import Redis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash
from src.core.config import logger
from src.db.postgres import get_session
from src.db.redis import get_redis
from src.models.data import UserSingUp, UserLogin
from src.models.user import User
from src.services.const import CACHE_EXPIRE_REFRESH_TOKEN
from src.settings import settings


class AuthService:
    def __init__(
        self, redis: Redis, pg: AsyncSession, auth: AuthJWT
    ):
        self.redis = redis
        self.pg = pg
        self.auth = auth

    async def get_by_login(self, login: str) -> User | None:
        result = await self.pg.execute(select(User).where(User.login == login))
        user_found = result.scalars().first()
        return user_found if user_found else None

    async def get_by_mail(self, mail: str) -> User | None:
        result = await self.pg.execute(select(User).where(User.email == mail))
        user_found = result.scalars().first()
        return user_found if user_found else None

    async def check_password(self, user: UserLogin) -> bool:
        result = await self.pg.execute(
            select(User.password).where(User.login == user.login)
        )
        password_hash = result.scalars().first()
        result = check_password_hash(password_hash, user.password)
        return bool(result)

    async def add_user(self, user: UserSingUp) -> None:
        hashed_pwd = generate_password_hash(user.password)
        logger.info(f"/signup - user: {user.login}")
        user_signup = User(
            login=user.login,
            password=hashed_pwd,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )
        # TODO history
        logger.warning(f'❌ ❌ ❌ {user_signup}')

        self.pg.add(user_signup)
        await self.pg.commit()

    async def add_jwt_to_redis(self, login: str, jwt_val: str):
        await self.redis.set(jwt_val, "true", settings.access_expires)

    async def revoke_both_tokens(self, login) -> None:
        refresh_jti = (await self.auth.get_raw_jwt())['refresh_jti']
        access_jti = (await self.auth.get_raw_jwt())['jti']
        await self.add_jwt_to_redis(login, access_jti)
        await self.add_jwt_to_redis(login, refresh_jti)

    async def create_access_token(self, payload: str, user_claims: Optional[dict] = {}):
        access_token = await self.auth.create_access_token(payload, user_claims=user_claims)
        return access_token

    async def create_refresh_token(self, payload: str, user_claims: Optional[dict] = {}):
        refresh_token = await self.auth.create_refresh_token(payload, user_claims=user_claims)
        return refresh_token

    async def check_token_is_expired(self, login: str, jwt_val: str) -> bool:
        result = self.redis.get(f'{login}::{jwt_val}')
        return bool(result)


@lru_cache()
def get_auth_service(
    redis: Redis = Depends(get_redis),
    pg: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends()
) -> AuthService:
    return AuthService(redis, pg, auth)
