# -*- coding: utf-8 -*-

import dateutil.parser
import logging

from fns import check_receipt, revise_info
from qif_transaction_generator.dao import DBUtil
from qif_transaction_generator.config import Config
from qif_transaction_generator.models import StatusEnum

from qif_transaction_generator.gnucash import parse_accounts
from qif_transaction_generator.json_utils import from_string_to_json, \
    parse_receipt

logger = logging.getLogger(__name__)


class App:
    def __init__(self):
        self.config = Config()

    def init(self):
        assert self.config.dbpath, 'dbpath mustn\'t be empty'
        self.db_util = DBUtil(self.config.dbpath)

    def add_receipt(self, fn, fp, fd, purchase_date, total):
        assert self.db_util, 'App must be init'
        date = dateutil.parser.parse(purchase_date)
        return self.db_util.create_receipt(fn, fp, fd, date, total)

    def revise_receipt(self):
        assert self.config.login, 'login mustn\'t be empty'
        assert self.config.password, 'password mustn\'t be empty'
        session = self.db_util.begin_session()
        try:
            receipts = self.db_util.get_receipt_by_status(
                session,
                [StatusEnum.CREATED.value, StatusEnum.NOT_FOUND.value])
            logger.info('found %d receipt(s) for revising' % len(receipts))
            logger.debug(receipts)

            for r in receipts:
                logger.info('revising %s' % r)
                if check_receipt(r):
                    r.status_id = StatusEnum.FOUND.value
                    logger.debug('receipt exists')
                    info = revise_info(r, self.config.login,
                                       self.config.password)
                    try:
                        logger.debug('info: %s' % info.json())
                        r.raw = str(info.json())
                        r.status_id = StatusEnum.LOADED.value
                    except:
                        logger.warn('info isn\'t a json')
                        r.status_id = StatusEnum.NOT_FOUND.value
                else:
                    logger.warn('receipt doesn\'t exist')
                    r.status_id = StatusEnum.NOT_FOUND.value
            if len(receipts) == 0:
                logger.info('there\'re not receipts for revising')
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def sync_accounts(self):
        assert self.config.args.account_file
        accounts = parse_accounts(self.config.gnucash_account_path)
        self.db_util.create_accounts(accounts)

    def enrich_receipts(self):
        session = self.db_util.begin_session()
        try:
            receipts = self.db_util.get_receipt_without_items_by_status(
                session, [StatusEnum.LOADED.value])
            logger.info('found %d receipt(s) for enriching' % len(receipts))
            logger.debug(receipts)

            for receipt in receipts:
                if receipt.raw is None:
                    logger.error('raw is empty for receipt(%d)', receipt.id)
                else:
                    _parse_receipt_json(receipt)
            # session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


def _parse_receipt_json(receipt):
    json = from_string_to_json(receipt.raw)
    parse_receipt(receipt, json)

    import pdb
    pdb.set_trace()
