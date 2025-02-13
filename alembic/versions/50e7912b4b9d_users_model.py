"""create users table

Revision ID: 50e7912b4b9d
Revises: 
Create Date: 2024-11-26 21:31:02.312283

"""
from alembic import op
import sqlalchemy as sa


revision = '50e7912b4b9d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('login', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('login'),
    sa.UniqueConstraint('password')
    )


def downgrade() -> None:
    op.drop_table('users')
