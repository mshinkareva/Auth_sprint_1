import uuid as uuid_pkg

from sqlmodel import SQLModel, Field


class UserRoles(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default=uuid_pkg.uuid4(),
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
    )

    user_login: str = Field(max_length=256, min_length=6, nullable=False)
    user_role: str = Field(max_length=256, min_length=6, nullable=False)
