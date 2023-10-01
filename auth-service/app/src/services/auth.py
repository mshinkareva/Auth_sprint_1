from functools import lru_cache, wraps
from typing import Optional

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, Request
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash

from src.core.config import logger
from src.db.postgres import get_session
from src.db.redis import get_redis
from src.models.data import UserSingUp, UserLogin, UserInDb
from src.models.role import Role
from src.models.user import User
from src.settings import settings


class AuthException(HTTPException):
    def __init__(
        self, detail: str = None, status_code: int = status.HTTP_403_FORBIDDEN
    ):
        super().__init__(status_code=status_code, detail=detail)


def roles_required(roles_list: list[str]):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user: UserInDb = getattr(kwargs.get('request'), 'user_data')
            if not user:
                raise AuthException(
                    'This operation is forbidden for you',
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            has_required_roles = bool(
                set(roles_list).intersection(set(user.roles_list))
            )
            if not has_required_roles:
                raise AuthException(
                    'This operation is forbidden for you',
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            return await function(*args, **kwargs)

        return wrapper

    return decorator


requires_admin = roles_required(roles_list=['admin'])


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request, pg: AsyncSession = Depends(get_session)
    ) -> UserInDb | None:
        authorize = AuthJWT(req=request)
        await authorize.jwt_optional()
        user_email = await authorize.get_jwt_subject()
        if not user_email:
            return None
        result = await pg.execute(
            select(User)
            .where(User.email == user_email)
            .options(selectinload(User.roles))
        )
        user = result.scalars().first()
        return UserInDb.from_orm(user)


async def get_current_user_global(
    request: Request, user: AsyncSession = Depends(JWTBearer())
):
    setattr(request, 'user_data', user)


class AuthServiceBase:
    def __init__(self, redis: Redis, pg: AsyncSession, auth: AuthJWT):
        self.redis = redis
        self.pg = pg
        self.auth = auth

    async def get_by_login(self, login: str) -> User | None:
        result = await self.pg.execute(
            select(User).where(User.login == login).options(selectinload(User.roles))
        )
        user_found = result.scalars().first()
        return user_found if user_found else None

    async def get_by_mail(self, mail: str) -> User | None:
        result = await self.pg.execute(
            select(User).where(User.email == mail).options(selectinload(User.roles))
        )
        user_found = result.scalars().first()
        return user_found if user_found else None

    async def check_password(self, user: UserLogin) -> bool:
        result = await self.pg.execute(
            select(User.password).where(User.email == user.email)
        )
        password_hash = result.scalars().first()
        result = check_password_hash(password_hash, user.password)
        return bool(result)

    async def add_user(self, user: UserSingUp) -> User:
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

        user_role = await self.pg.execute(select(Role).where(Role.name == "registered"))
        user_role = user_role.scalars().first()

        user_signup.roles.append(user_role)
        self.pg.add(user_signup)
        await self.pg.commit()
        return user_signup

    async def add_jwt_to_redis(self, jwt_val: str):
        await self.redis.set(jwt_val, "true", settings.access_expires)

    async def check_token_is_expired(self, login: str, jwt_val: str) -> bool:
        result = self.redis.get(f'{login}::{jwt_val}')
        return bool(result)

    async def create_access_token(self, payload: str, user_claims: Optional[dict] = {}):
        access_token = await self.auth.create_access_token(
            payload, user_claims=user_claims
        )
        return access_token

    async def create_refresh_token(
        self, payload: str, user_claims: Optional[dict] = {}
    ):
        refresh_token = await self.auth.create_refresh_token(
            payload, user_claims=user_claims
        )
        return refresh_token


class AuthService(AuthServiceBase):
    def __init__(self, redis: Redis, pg: AsyncSession, auth: AuthJWT):
        super().__init__(redis, pg, auth)
        self.auth = auth

    async def revoke_both_tokens(self) -> None:
        refresh_jti = (await self.auth.get_raw_jwt()).get('refresh_jti')
        access_jti = (await self.auth.get_raw_jwt())['jti']
        await self.add_jwt_to_redis(access_jti)
        print(f'🔴  access_jti {access_jti}')
        if refresh_jti:
            await self.add_jwt_to_redis(refresh_jti)


@lru_cache()
def get_auth_service_base(
    redis: Redis = Depends(get_redis),
    pg: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> AuthServiceBase:
    return AuthServiceBase(redis, pg, auth)


@lru_cache()
def get_auth_service(
    redis: Redis = Depends(get_redis),
    pg: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> AuthService:
    return AuthService(redis, pg, auth)
