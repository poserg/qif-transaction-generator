# -*- coding: utf-8 -*-

import dateutil.parser

from qif_transaction_generator.dao import DBUtil


def add_receipt(fn, fp, fd, purchase_date, total):
    db_util = DBUtil('sqlite:///db.sqlite')
    date = dateutil.parser.parse(purchase_date)
    return db_util.create_receipt(fn, fp, fd, date, total)
