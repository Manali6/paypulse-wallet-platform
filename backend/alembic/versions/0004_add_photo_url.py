"""add photo_url

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-30 07:07:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('users', sa.Column('photo_url', sa.String(length=512), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'photo_url')
