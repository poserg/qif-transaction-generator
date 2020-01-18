# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

ratio = 100

class Account:

    def __init__(self, category, description, amount):
        self.category = category
        self.description = description
        self.amount = amount

    def __str__(self):
        return '<Account %s, %2.f, %s>' % (
                self.category,
                self.amount,
                self.description
            )

class Transaction:

    def __init__(self, source, date, amount, description, accounts):
        assert type(accounts) is list, '"accounts must be list"'
        assert len(accounts) > 0, '"accounts" mustn\'t be empty'
        self.source = source
        self.date = date
        self.amount = amount
        self.description = description
        self.accounts = accounts

    def __str__(self):
        return '<Transaction %s, %s, %s, %s>'% (
            self.date,
            self.amount,
            self.description,
            self.accounts
        )

    def dump(self):
        result = []

        # Header of account
        result.append('!Account')

        # Source account
        result.append('N' + self.source)

        result.append('TCash')

        # End of the entry
        result.append('^')

        # Header
        result.append('!Type:Cash')

        # Date
        result.append('D' + self.date.strftime('%m/%d/%Y'))

        # Amount
        result.append('U' + '-%.2f' % self.amount)

        # Payee
        if self.description:
            result.append('P' + self.description)

        if len(self.accounts) == 1:
            # Category
            result.append('L' + self.accounts[0].category)
        else:
            # split transaction
            for account in self.accounts:
                # Category in split
                result.append('S' + account.category)

                # Memo in split
                if account.description:
                    result.append('E' + account.description)

                # Dollar amount of split
                result.append('$' + '-%.2f' % account.amount)

        # End of the entry
        result.append('^\n')

        return result

def convert(receipts):
    logger.debug('start convert receipt to qif transaction')
    result = []
    for r in receipts:
        accounts = [Account(item.account.full_name, item.name, item.sum / ratio) for item in r.items]
        t = Transaction('test', r.purchase_date, r.total / ratio, None, accounts)
        result.append(t)
    return result
