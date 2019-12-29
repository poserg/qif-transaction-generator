"""Add status CREATED_FROM_FILE

Revision ID: 49d74e6d372c
Revises: 0e24941e3f7c
Create Date: 2019-12-28 11:38:36.884353

"""
from alembic import op
from sqlalchemy.orm.session import Session
from sys import path as sys_path
sys_path.append('./')
from qif_transaction_generator.models import Status, StatusEnum


# revision identifiers, used by Alembic.
revision = '49d74e6d372c'
down_revision = '0e24941e3f7c'
branch_labels = None
depends_on = None


def upgrade():
    statuses = Status.__table__
    op.bulk_insert(statuses,
                   [
                        {'id': StatusEnum.CREATED_FROM_FILE.value,
                         'code': StatusEnum.CREATED_FROM_FILE.name}
                   ])


def downgrade():
    session = Session(bind=op.get_bind())
    q = Status.__table__.delete().where(
            Status.code.in_([StatusEnum.CREATED_FROM_FILE.name]))
    session.execute(q)
    session.commit()
