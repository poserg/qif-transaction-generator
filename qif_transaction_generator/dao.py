# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qif_transaction_generator.models import Receipt, StatusEnum


class DBUtil:
    def __init__(self, path):
        logging.debug('DB path = "%s"', path)
        self._engine = create_engine(path)
        self.Session = sessionmaker(bind=self._engine)

    def create_receipt(self, fn, fp, fd, purchase_date, total):
        r = Receipt(fn=fn,
                    fp=fp,
                    fd=fd,
                    purchase_date=purchase_date,
                    total=total,
                    status_id=StatusEnum.CREATED.value)
        session = self.Session()
        session.add(r)
        session.commit()

        return r.id
