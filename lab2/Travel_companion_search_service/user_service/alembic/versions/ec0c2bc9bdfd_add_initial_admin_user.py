"""add initial admin user

Revision ID: ec0c2bc9bdfd
Revises: 
Create Date: 2025-04-09 20:06:20.989678

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'ec0c2bc9bdfd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET client_encoding TO 'UTF8';")
    
    op.create_table(
        'users_info',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=False)
    )
    
    op.execute("""
        INSERT INTO users_info (username, email, full_name)
        VALUES ('admin', 'admin@ya.ru', 'Adminov Admin')
    """)


def downgrade() -> None:
    op.drop_table('users_info')
