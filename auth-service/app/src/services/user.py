import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import logger
from src.db.postgres import get_session
from src.models.data import UserInDb
from src.models.user import User


class UserService:
    def __init__(self, pg: AsyncSession) -> None:
        self.pg = pg

    async def get_users(self) -> list[User]:
        logger.info("Start get_users")
        data = await self.pg.execute(select(User).options(selectinload(User.roles)))
        return data.scalars().all()

    async def get_user(self, login) -> UserInDb:
        logger.info("Start get_user")
        result = await self.pg.execute(select(User).where(User.login == login))
        user_found = result.scalars().first()
        return (
            UserInDb(login=user_found.login, email=user_found.email)
            if user_found
            else None
        )

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        logger.info("Start get_user_by_id")
        result = await self.pg.execute(
            select(User).where(User.id == user_id).options(selectinload(User.roles))
        )
        user_found = result.scalars().first()
        return user_found if user_found else None


@lru_cache()
def users_services(
    pg: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(pg=pg)
