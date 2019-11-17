# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from qif_transaction_generator.models import Receipt, Dictionary, Item, \
    Account

logger = logging.getLogger(__name__)


class DBUtil:
    def __init__(self, path):
        logger.debug('DB path = "%s"', path)
        self._engine = create_engine(path)
        self.Session = sessionmaker(bind=self._engine)
        self.current_session = None

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

    def get_receipt_by_id(self, session, ids):
        query = session.query(Receipt).filter(
            Receipt.id.in_(ids))
        result = query.all()
        return result

    def get_receipt_without_items_by_status(self, status_ids):
        session = self.begin_session()
        query = session.query(Receipt.id).filter(
            Receipt.status_id.in_(status_ids))
        result = query.all()
        session.close()
        return result

    def create_accounts(self, accounts_list):
        session = self.get_current_session()
        session.add_all(accounts_list)

    def get_dictionaries_by_phrases(self, phrases_list):
        query = self.get_current_session().query(Dictionary).filter(
            Dictionary.phrase.in_(phrases_list)).order_by(
                Dictionary.weight.desc()).limit(5)
        return query.all()

    def get_dictionary_by_full_item_name(self, item_name):
        return self.get_current_session().query(Dictionary).filter(
            Dictionary.phrase == item_name).order_by(
                Dictionary.weight.desc()).limit(1).all()

    def search_accounts(self, search_text):
        r1 = self.get_current_session().query(Account).filter(or_(
            Account.name.ilike(f'%{search_text}%'),
            Account.description.ilike(f'%{search_text}%'))).all()
        logger.debug('result of searching by name and desc: %s', r1)

        r2 = self.get_current_session().query(Account).filter(
            Account.parent_guid.in_([x.guid for x in r1])).all()
        logger.debug('result of searching by parent guid: %s', r2)
        r1.extend(r2)
        return r1

    def get_all_accounts(self):
        return self.get_current_session().query(Account).all()

    def delete_all(self, list):
        session = self.get_current_session()
        for l in list:
            session.delete(l)

    def commit_current_sesssion(self):
        self.get_current_session().commit()
