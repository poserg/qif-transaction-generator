"""Split Receipts to Receipts and FnsReceipts

Revision ID: 0e24941e3f7c
Revises: d119de3374b0
Create Date: 2019-12-28 17:07:08.230676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e24941e3f7c'
down_revision = 'd119de3374b0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('fns_receipts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('fn', sa.String(), nullable=False),
                    sa.Column('fp', sa.String(), nullable=False),
                    sa.Column('fd', sa.String(), nullable=False),
                    sa.Column('purchase_date', sa.DateTime(), nullable=False),
                    sa.Column('total', sa.String(), nullable=False),
                    sa.Column('status_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['status_id'], ['statuses.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # Drop old table receipts
    op.drop_table('receipts')
    op.create_table('receipts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('purchase_date', sa.DateTime(), nullable=True),
                    sa.Column('total', sa.Integer(), nullable=True),
                    sa.Column('raw', sa.Text(), nullable=False),
                    sa.Column('ecash_total_sum', sa.Integer(), nullable=True),
                    sa.Column('cash_total_sum', sa.Integer(), nullable=True),
                    sa.Column('status_id', sa.Integer(), nullable=False),
                    sa.Column('fns_receipt_id', sa.Integer, nullable=True),
                    sa.ForeignKeyConstraint(['status_id'], ['statuses.id'],
                                            name='fk_receipt_status_id'),
                    sa.ForeignKeyConstraint(['fns_receipt_id'],
                                            ['fns_receipts.id'],
                                            name='fk_receipt_fns_receipts_id'),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('receipts')
    op.drop_table('fns_receipts')
    op.create_table('receipts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('fn', sa.String(), nullable=False),
                    sa.Column('fp', sa.String(), nullable=False),
                    sa.Column('fd', sa.String(), nullable=False),
                    sa.Column('purchase_date', sa.DateTime(), nullable=False),
                    sa.Column('total', sa.String(), nullable=False),
                    sa.Column('raw', sa.Text(), nullable=True),
                    sa.Column('ecash_total_sum', sa.Integer(), nullable=True),
                    sa.Column('cash_total_sum', sa.Integer(), nullable=True),
                    sa.Column('status_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['status_id'], ['statuses.id'],
                                            name='fk_receipt_status_id'),
                    sa.PrimaryKeyConstraint('id')
                    )
