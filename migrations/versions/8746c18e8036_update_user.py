"""update user

Revision ID: 8746c18e8036
Revises: e6a2d1854cf7
Create Date: 2024-10-28 21:36:18.044897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8746c18e8036'
down_revision: Union[str, None] = 'e6a2d1854cf7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_id', sa.BigInteger(), nullable=False))
    op.add_column('users', sa.Column('email', sa.String(), nullable=False))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('is_enabled', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_enabled')
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'email')
    op.drop_column('users', 'user_id')
    # ### end Alembic commands ###