"""add initial admin user

Revision ID: a7b4ccf7b80e
Revises: 
Create Date: 2025-04-09 23:35:49.924964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import auth


# revision identifiers, used by Alembic.
revision: str = 'a7b4ccf7b80e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET client_encoding TO 'UTF8';")
    
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(100), nullable=False),
    )
    
    op.execute(f"""
        INSERT INTO users (username, hashed_password)
        VALUES ('admin', '{auth.get_password_hash('secret')}')
    """)


def downgrade() -> None:
    op.drop_table('users')