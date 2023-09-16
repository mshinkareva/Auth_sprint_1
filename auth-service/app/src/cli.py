import logging
from typing import Optional

import typer
from sqlmodel import select
from typing_extensions import Annotated
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors

from src.db.postgres import get_session_sync
from src.models.role import Role
from src.models.user import User
from src.models.user_roles import UserRoles


app = typer.Typer()


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
    """
    Create a new user with USERNAME.
    """
    user = User(login=login,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                )
    add_model(user)
    if role and get_role(role):
        user_role = UserRoles(user_role=role, user_login=login)
        add_model(user_role)


@app.command()
def create_role(name: str, description: str):
    role = Role(name=name, description=description)
    add_model(role)
    pass


@app.command()
def set_role(login: str,
             role: str,
             ):
    if get_role(role) is None:
        logging.log(logging.ERROR, "Role not found")
    elif get_user(login) is None:
        logging.log(logging.ERROR, "User not found")
    else:
        user_role = UserRoles(
            user_login=login,
            user_role=role,
        )
        add_model(user_role)


if __name__ == "__main__":
    app()
