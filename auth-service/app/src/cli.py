from typing import Optional

import typer
from typing_extensions import Annotated

from src.db.postgres import get_session_sync
from src.models.user import User

app = typer.Typer()


@app.command()
def create_user(login: str,
                password: str,
                email: str,
                first_name: Annotated[Optional[str], typer.Argument()] = 'Admin',
                last_name: Annotated[Optional[str], typer.Argument()] = 'Super',
                ):
    """
    Create a new user with USERNAME.
    """
    user = User(login=login, password=password, email=email, first_name=first_name, last_name=last_name)
    with get_session_sync() as session:
        session.add(user)
        session.commit()


if __name__ == "__main__":
    app()
