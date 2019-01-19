# -*- coding: utf-8 -*-

import dateutil.parser

from qif_transaction_generator.dao import DBUtil
from qif_transaction_generator.config import Config


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
