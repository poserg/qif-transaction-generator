# -*- coding: utf-8 -*-

import dateutil.parser

from qif_transaction_generator.dao import DBUtil


db_util = DBUtil('sqlite:///db.sqlite')


def add_receipt(fn, fp, fd, purchase_date, total):
    date = dateutil.parser.parse(purchase_date)
    db_util.create_receipt(fn, fp, fd, date, total)
