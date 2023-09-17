import logging
from typing import Optional
import asyncio

import typer
from fastapi import Depends
from sqlmodel import select
from typing_extensions import Annotated
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors

from src.db.postgres import get_session
from src.models.role import Role
from src.models.user import User
from src.models.user_roles import UserRoles
from src.services.role import role_services, RoleService
from src.services.auth import get_auth_service
from src.models.data import UserSingUp

async def get_session():
    app = typer.Typer()
    role_service = RoleService(get_session())
    auth = get_auth_service(get_session())



def add_model(model):
    with get_session_sync() as session:
        try:
            session.add(model)
            session.commit()
        except errors.lookup(UNIQUE_VIOLATION):
            logging.log(logging.INFO, f'{model.__repr__()} had been already created')
        else:
            logging.log(logging.INFO, f'Create {model}')


def get_user(login: str) -> User:
    with get_session_sync() as session:
        try:
            user = select(User).where(User.login == login)
            result = session.exec(user)
        except BaseException as e:
            logging.log(logging.ERROR, e)
        else:
            return result.first()


def get_role(role: str) -> Role:
    with get_session_sync() as session:
        try:
            user = select(Role).where(Role.name == role)
            result = session.exec(user)
        except BaseException as e:
            logging.log(logging.ERROR, e)
        else:
            return result.first()


@app.command()
def create_user(login: str,
                password: str,
                email: str,
                first_name: Annotated[Optional[str], typer.Argument()] = 'Admin',
                last_name: Annotated[Optional[str], typer.Argument()] = 'Super',
                role: Annotated[Optional[str], typer.Argument()] = None,
                ):
    asyncio.run(create_user_async(login, password, email, first_name, last_name, role))


async def create_user_async(login: str,
                            password: str,
                            email: str,
                            first_name: str = 'Admin',
                            last_name: str = 'Super',
                            role: str = None,
                            ):
    """
    Create a new user with USERNAME.
    """
    pg = role_services(get_session())
    user = UserSingUp(login=login,
                      password=password,
                      email=email,
                      first_name=first_name,
                      last_name=last_name,
                      )
    if await pg.exist_user(login):
        logging.error('User has already been created')
    else:
        await auth.add_user(user)
        exist = pg.exist_role(role)
        if role is not None and exist:
            await pg.set_user_role(login, role)
        elif not exist:
            logging.error('Role not found')
        else:
            logging.info(f'Role not set for {login}')


@app.command()
def create_role(name: str, description: str):
    asyncio.run(create_role_async(name, description))


async def create_role_async(name: str, description: str):
    if await role_service.exist_role(name):
        logging.log(logging.ERROR, "Role has already been created")
    else:
        await role_service.create_role(name, description)


@app.command()
def set_role(login: str, role: str):
    asyncio.run(set_role_async(login, role))


async def set_role_async(login: str, role: str):
    if not await role_service.exist_role(role):
        logging.log(logging.ERROR, "Role not found")
    elif not await role_service.exist_user(login):
        logging.log(logging.ERROR, "User not found")
    else:
        await role_service.set_user_role(login, role)


if __name__ == "__main__":
    app()
