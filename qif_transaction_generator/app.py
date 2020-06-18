# -*- coding: utf-8 -*-

import dateutil.parser
import logging

from fns import check_receipt, revise_info
from . dao import DBUtil
from . config import Config
from . models import Receipt, StatusEnum, Dictionary, FnsReceipt

from . gnucash import parse_accounts, set_up_account_names, get_difference_list
from . enriching import enrich_receipt
from . transaction import convert_with_merging_items, convert

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
        r = FnsReceipt(
            fn=fn,
            fp=fp,
            fd=fd,
            purchase_date=date,
            total=total,
            status_id=StatusEnum.CREATED.value)
        return self.db_util.create_receipt(r)

    def revise_receipt(self):
        assert self.config.login, 'login mustn\'t be empty'
        assert self.config.password, 'password mustn\'t be empty'
        session = self.db_util.begin_session()
        try:
            self._process_revise_receipt(session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def sync_accounts(self):
        assert self.config.args.account_file
        accounts = parse_accounts(self.config.args.account_file)
        set_up_account_names(accounts)

        db_accounts = self.db_util.get_all_accounts()

        to_add, to_delete, to_modify = get_difference_list(
            accounts, db_accounts)
        logger.info('to_add: %s', to_add)
        logger.info('to_delete: %s', to_delete)
        logger.info('to_modify: %s', to_modify)

        if to_add:
            self.db_util.create_accounts(to_add)
        if to_delete:
            self.db_util.delete_all(to_delete)
        if to_add or to_delete or to_modify:
            self.db_util.commit_current_sesssion()

    def enrich_receipts(self):
        receipts = self.db_util.get_receipt_without_items_by_status(
            [StatusEnum.LOADED.value, StatusEnum.CREATED_FROM_FILE.value])
        logger.info('found %d receipt(s) for enriching' % len(receipts))
        logger.debug('ids: %s', receipts)

        for r in receipts:
            enrich_receipt(self.db_util, r.id)

    def _process_revise_receipt(self, session):
        receipts = self.db_util.get_receipt_by_status(
            session, [StatusEnum.CREATED.value, StatusEnum.NOT_FOUND.value])
        logger.info('found %d receipt(s) for revising' % len(receipts))
        logger.debug(receipts)

        for fns_r in receipts:
            logger.info('revising %s' % fns_r)
            if check_receipt(fns_r):
                fns_r.status_id = StatusEnum.FOUND.value
                logger.debug('receipt exists')
                info = revise_info(fns_r, self.config.login, self.config.password)
                try:
                    logger.debug('info: %s' % info.json())
                    fns_r.status_id = StatusEnum.LOADED.value
                    r = Receipt(
                        status_id=StatusEnum.LOADED.value,
                        fns_receipt_id=fns_r.id,
                        raw=str(info.json()))
                    session.add(r)
                except:
                    logger.warning('info isn\'t a json')
                    fns_r.status_id = StatusEnum.NOT_FOUND.value
            else:
                logger.warning('receipt doesn\'t exist')
                fns_r.status_id = StatusEnum.NOT_FOUND.value
        if len(receipts) == 0:
            logger.info('there\'re not receipts for revising')

    def add_phrase(self):
        assert self.config.args.phrase
        assert self.config.args.guid

        d = Dictionary(account_guid=self.config.args.guid,
                       phrase=self.config.args.phrase.lower(),
                       weight=0)
        return self.db_util.create(d)

    def search_accounts(self, search_text):
        logger.debug('start search_accounts')
        assert search_text

        r = self.db_util.search_accounts(search_text)
        if r and len(r) > 0:
            logger.info('search result:')
            for i in r:
                logger.info(' ' + i.guid + ' : ' + i.full_name)
            return r
        else:
            logger.info('search result is empty')

    def generate_transaction(self, output_file, is_merge_transaction, limit):
        logger.debug('start generate transaction')
        receipts = self.db_util.get_receipts_by_status_with_items_and_accounts(
            [StatusEnum.DONE.value], limit)
        if receipts:
            logger.debug('Found %d receipt(s) with status DONE', len(receipts))
            if is_merge_transaction:
                transactions = convert_with_merging_items(receipts)
            else:
                transactions = convert(receipts)
            for t in transactions:
                logger.debug('Write transaction {%s} to file', t)
                output_file.write('\n'.join(t.dump()))

    def add_json(self, json_file):
        r = Receipt(raw=json_file.read(),
                    status_id=StatusEnum.CREATED_FROM_FILE.value)
        return self.db_util.create_receipt(r)
