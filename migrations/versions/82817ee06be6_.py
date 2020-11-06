"""empty message

Revision ID: 82817ee06be6
Revises: 6a59736e6af5
Create Date: 2020-11-06 15:37:24.339701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82817ee06be6'
down_revision = '6a59736e6af5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invoiceitems', 'invoice_version')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invoiceitems', sa.Column('invoice_version', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###