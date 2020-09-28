"""Initial migration.

Revision ID: 1007aed5b0b0
Revises: 9734a59e6dd7
Create Date: 2020-09-28 14:18:41.197078

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1007aed5b0b0'
down_revision = '9734a59e6dd7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('userid', sa.Integer(), nullable=False),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('firstname', sa.String(), nullable=True),
    sa.Column('lastname', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('userid')
    )
    op.create_table('friends',
    sa.Column('friendshipid', sa.Integer(), nullable=False),
    sa.Column('userid', sa.Integer(), nullable=False),
    sa.Column('frienduserid', sa.Integer(), nullable=False),
    sa.Column('statusid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['frienduserid'], ['users.userid'], ),
    sa.ForeignKeyConstraint(['userid'], ['users.userid'], ),
    sa.PrimaryKeyConstraint('friendshipid')
    )
    op.create_table('invoices',
    sa.Column('invoiceid', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('userid', sa.Integer(), nullable=False),
    sa.Column('frienduserid', sa.Integer(), nullable=False),
    sa.Column('statusid', sa.Integer(), nullable=True),
    sa.Column('invoice_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('duedate', sa.Date(), nullable=True),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('invoice_version', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['frienduserid'], ['users.userid'], ),
    sa.ForeignKeyConstraint(['userid'], ['users.userid'], ),
    sa.PrimaryKeyConstraint('invoiceid')
    )
    op.drop_table('transactions')
    op.drop_table('usergroups')
    op.drop_table('payments')
    op.drop_table('debts')
    op.drop_table('optionsfriendshipstatus')
    op.drop_table('groupmembers')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groupmembers',
    sa.Column('groupmemberid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('userid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('groupid', sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.create_table('optionsfriendshipstatus',
    sa.Column('friedndshipstatusid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('statusid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    )
    op.create_table('debts',
    sa.Column('debtid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('geldenäruserid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('borgenäruserid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('amount', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('invoicedate', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('duedate', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('closed', postgresql.BIT(length=1), autoincrement=False, nullable=True)
    )
    op.create_table('payments',
    sa.Column('paymentid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('amount', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('paymentdate', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('typeid', sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.create_table('usergroups',
    sa.Column('usergroupid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('usergroupname', sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    )
    op.create_table('transactions',
    sa.Column('transactionid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('debtid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('paymentid', sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.drop_table('invoices')
    op.drop_table('friends')
    op.drop_table('users')
    # ### end Alembic commands ###
