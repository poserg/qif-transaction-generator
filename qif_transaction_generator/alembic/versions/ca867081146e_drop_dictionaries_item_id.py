"""Drop dictionaries.item_id

Revision ID: ca867081146e
Revises: cdd227c0801b
Create Date: 2019-10-16 21:15:12.714444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca867081146e'
down_revision = 'cdd227c0801b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('dictionaries')
    op.create_table('dictionaries',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column(
                        'account_guid', sa.String(length=32), nullable=False),
                    sa.Column('phrase', sa.String(), nullable=False),
                    sa.Column('weight', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['account_guid'],
                        ['accounts.guid'],
                    ), sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('dictionaries')
    op.create_table('dictionaries',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column(
                        'account_guid', sa.String(length=32), nullable=False),
                    sa.Column('item_id', sa.Integer(), nullable=False),
                    sa.Column('phrase', sa.String(), nullable=False),
                    sa.Column('weight', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['account_guid'],
                        ['accounts.guid'],
                    ), sa.ForeignKeyConstraint(
                        ['item_id'],
                        ['items.id'],
                    ), sa.PrimaryKeyConstraint('id'))
