"""Add status DONE

Revision ID: d119de3374b0
Revises: 26f5cf01525b
Create Date: 2019-12-20 07:23:09.288393

"""
from alembic import op
from sqlalchemy.orm.session import Session
from sys import path as sys_path
sys_path.append('./')
from qif_transaction_generator.models import Status, StatusEnum


# revision identifiers, used by Alembic.
revision = 'd119de3374b0'
down_revision = '26f5cf01525b'
branch_labels = None
depends_on = None


def upgrade():
    statuses = Status.__table__
    op.bulk_insert(statuses,
                   [
                        {'id': StatusEnum.DONE.value,
                         'code': StatusEnum.DONE.name}
                   ])


def downgrade():
    session = Session(bind=op.get_bind())
    q = Status.__table__.delete().where(
            Status.code.in_([StatusEnum.DONE.name]))
    session.execute(q)
    session.commit()
