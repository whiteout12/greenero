"""empty message

Revision ID: 7472330287e8
Revises: 89f88a8b9472
Create Date: 2020-11-08 13:19:53.921628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7472330287e8'
down_revision = '89f88a8b9472'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('billdebts', sa.Column('token', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('billdebts', 'token')
    # ### end Alembic commands ###