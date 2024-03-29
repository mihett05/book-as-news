"""Added is_active into preferences

Revision ID: ddd8f0e2e238
Revises: dbd184b925f9
Create Date: 2022-04-09 20:48:25.936943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddd8f0e2e238'
down_revision = 'dbd184b925f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('preferences', sa.Column('is_active', sa.Boolean(), nullable=True, default=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('preferences', 'is_active')
    # ### end Alembic commands ###
