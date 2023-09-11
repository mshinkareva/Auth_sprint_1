from functools import lru_cache
from typing import Optional

from fastapi import Depends
from sqlmodel import select, update, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.postgres import get_session
from src.models.data import RoleInDb
from src.models.role import Role
from src.models.user_roles import UserRoles

from src.models.user import User
from src.core.config import logger


class RoleService:
    def __init__(self, pg: AsyncSession) -> None:
        self.pg = pg

    async def exist_role(self, name: str) -> bool:
        logger.info("Check if role exist")
        result = await self.pg.execute(select(Role).where(Role.name == name))
        found = result.scalars().first()

        return bool(found)

    async def create_role(self, name: str, description: str) -> Optional[Role]:
        logger.info("Start create_role")
        if await self.exist_role(name=name):
            return None
        role = Role(name=name, description=description)
        self.pg.add(role)
        await self.pg.commit()
        return role

    async def get_roles(self) -> list[RoleInDb]:
        logger.info("Start all get_permissions")
        data = await self.pg.execute(select(Role))
        return [
            RoleInDb(name=role.name, description=role.description)
            for role in data.scalars()
        ]

    async def delete_role(self, name: str) -> bool:
        logger.info("Start delete_role")
        if not await self.exist_role(name=name):
            return False

        result = await self.pg.execute(delete(Role).where(Role.name == name))
        await self.pg.commit()
        return bool(result)

    async def exist_user(self, login: str) -> bool:
        result = await self.pg.execute(select(User).where(User.login == login))
        found = result.scalars().first()

        return bool(found)

    async def exist_user_role(self, login: str) -> bool:
        result = await self.pg.execute(
            select(UserRoles).where(UserRoles.user_login == login)
        )
        found = result.scalars().first()

        return bool(found)

    async def set_user_role(self, login: str, name: str) -> bool:
        logger.info("Start set_role_to_user")

        if not await self.exist_user(login=login):
            return False

        if not await self.exist_role(name=name):
            return False

        if await self.exist_user_role(login=login):
            values = {"user_role": name}
            await self.pg.execute(
                update(UserRoles).where(UserRoles.user_login == login).values(**values)
            )
            await self.pg.commit()
        else:
            user_role = UserRoles(user_login=login, user_role=name)
            self.pg.add(user_role)
            await self.pg.commit()

        return True

    async def delete_user_role(self, login: str, role: str) -> bool:
        logger.info("Delete set_role_to_user")

        if not await self.exist_user(login=login):
            return False

        if await self.exist_user_role(login=login):
            await self.pg.execute(
                delete(UserRoles).where(
                    UserRoles.user_login == login and UserRoles.user_role == role
                )
            )
            await self.pg.commit()

        return True


@lru_cache()
def role_services(
    pg: AsyncSession = Depends(get_session),
) -> RoleService:
    return RoleService(pg=pg)
