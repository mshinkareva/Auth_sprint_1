"""Add user roles table

Revision ID: f33ced38b24c
Revises: 32b39a179dd6
Create Date: 2023-09-06 15:01:21.152742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = 'f33ced38b24c'
down_revision: Union[str, None] = '32b39a179dd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('userroles',
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('user_login', sqlmodel.sql.sqltypes.AutoString(length=256), nullable=False),
    sa.Column('user_role', sqlmodel.sql.sqltypes.AutoString(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_userroles_id'), 'userroles', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_userroles_id'), table_name='userroles')
    op.drop_table('userroles')
    # ### end Alembic commands ###
