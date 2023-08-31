import datetime
from sqlmodel import SQLModel, Field
from pydantic import EmailStr
import uuid as uuid_pkg


class User(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default=uuid_pkg.uuid4(),
        primary_key=True,
        index=True,
        unique=True,
        nullable=False)
    login: str = Field(
        max_length=256,
        min_length=6,
        index=True,
        unique=True,
        nullable=False)
    password: str = Field(max_length=256, min_length=6, nullable=False)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    created_at: datetime.datetime = datetime.datetime.now()

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class UserSingUp(SQLModel):
    login: str
    password: str = Field(max_length=256, min_length=6)
    first_name: str
    last_name: str
    email: EmailStr


class UserLogin(SQLModel):
    login: str
    password: str = Field(max_length=256, min_length=6)