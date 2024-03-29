"""Updated preferences

Revision ID: dbd184b925f9
Revises: cc53cd54da79
Create Date: 2022-04-09 20:38:03.398426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbd184b925f9'
down_revision = 'cc53cd54da79'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('preferences', sa.Column('last_sent_time', sa.Integer(), nullable=True, default=0))
    op.add_column('preferences', sa.Column('last_sent_id', sa.Integer(), nullable=True, default=0))
    op.drop_column('preferences', 'last_sent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('preferences', sa.Column('last_sent', sa.INTEGER(), nullable=True))
    op.drop_column('preferences', 'last_sent_id')
    op.drop_column('preferences', 'last_sent_time')
    # ### end Alembic commands ###
