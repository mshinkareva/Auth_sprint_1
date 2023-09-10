import uuid as uuid_pkg

from sqlmodel import SQLModel, Field


class Role(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default=uuid_pkg.uuid4(),
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
    )
    name: str = Field(max_length=256, min_length=6, nullable=False)
    description: str = Field(max_length=256, min_length=6)

    def __repr__(self) -> str:
        return f'<Role {self.name}>'
