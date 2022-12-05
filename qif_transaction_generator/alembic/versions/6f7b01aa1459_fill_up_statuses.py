"""Fill up statuses

Revision ID: 6f7b01aa1459
Revises: 6e609953b4c4
Create Date: 2019-01-15 07:18:15.830561

"""
from alembic import op
from sqlalchemy.orm.session import Session
from qif_transaction_generator.models import Status, StatusEnum


# revision identifiers, used by Alembic.
revision = '6f7b01aa1459'
down_revision = '6e609953b4c4'
branch_labels = None
depends_on = None


def upgrade():
    statuses = Status.__table__
    op.bulk_insert(statuses,
                   [
                        {'id': StatusEnum.CREATED.value,
                         'code': StatusEnum.CREATED.name},
                        {'id': StatusEnum.FOUND.value,
                         'code': StatusEnum.FOUND.name},
                        {'id': StatusEnum.NOT_FOUND.value,
                         'code': StatusEnum.NOT_FOUND.name},
                        {'id': StatusEnum.LOADED.value,
                         'code': StatusEnum.LOADED.name}
                   ])


def downgrade():
    session = Session(bind=op.get_bind())
    q = Status.__table__.delete().where(
            Status.code.in_([StatusEnum.CREATED.name,
                             StatusEnum.FOUND.name,
                             StatusEnum.NOT_FOUND.name,
                             StatusEnum.LOADED.name]))
    session.execute(q)
    session.commit()
