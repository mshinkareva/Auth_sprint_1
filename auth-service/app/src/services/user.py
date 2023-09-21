from functools import lru_cache

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import logger
from src.db.postgres import get_session
from src.models.data import UserInDb
from src.models.user import User


class UserService:
    def __init__(self, pg: AsyncSession) -> None:
        self.pg = pg

    async def get_users(self) -> list[UserInDb]:
        logger.info("Start get_users")
        data = await self.pg.execute(select(User))
        return [UserInDb(login=user.login, email=user.email) for user in data.scalars()]

    async def get_user(self, login) -> UserInDb:
        logger.info("Start get_user")
        result = await self.pg.execute(select(User).where(User.login == login))
        user_found = result.scalars().first()
        return (
            UserInDb(login=user_found.login, email=user_found.email)
            if user_found
            else None
        )


@lru_cache()
def users_services(
    pg: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(pg=pg)
