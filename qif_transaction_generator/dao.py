# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qif_transaction_generator.models import Receipt

logger = logging.getLogger(__name__)


class DBUtil:
    def __init__(self, path):
        logger.debug('DB path = "%s"', path)
        self._engine = create_engine(path)
        self.Session = sessionmaker(bind=self._engine)

    def create_receipt(self, receipt):
        session = self.Session()
        session.add(receipt)
        session.commit()

        return receipt.id

    def begin_session(self):
        return self.Session()

    def get_receipt_by_status(self, session, status_ids):
        query = session.query(Receipt).filter(
            Receipt.status_id.in_(status_ids))
        result = query.all()
        return result

    def get_receipt_without_items_by_status(self, session, status_ids):
        query = session.query(Receipt).filter(~Receipt.items.any()).filter(
            Receipt.status_id.in_(status_ids))
        result = query.all()
        return result

    def create_accounts(self, accounts_list):
        session = self.Session()
        session.add_all(accounts_list)
        session.commit()
