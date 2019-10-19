# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qif_transaction_generator.models import Receipt, Dictionary

logger = logging.getLogger(__name__)


class DBUtil:
    def __init__(self, path):
        logger.debug('DB path = "%s"', path)
        self._engine = create_engine(path)
        self.Session = sessionmaker(bind=self._engine)

    def create(self, obj):
        session = self.Session()
        session.add(obj)
        session.commit()

        return obj.id

    def create_receipt(self, receipt):
        return self.create(receipt)

    def get_current_session(self):
        return self.current_session or self.begin_session()

    def begin_session(self):
        self.current_session = self.Session()
        return self.current_session

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

    def get_dictionaries_by_phrases(self, phrases_list):
        query = self.get_current_session().query(Dictionary).filter(
            Dictionary.phrase.in_(phrases_list)).order_by(
                Dictionary.weight.desc()).limit(5)
        return query.all()

    def get_dictionary_by_full_item_name(self, item_name):
        return self.get_current_session().query(Dictionary).filter(
            Dictionary.phrase == item_name).order_by(
                Dictionary.weight.desc()).limit(1).all()
