# -*- coding: utf-8 -*-

class Account:

    def __init__(self, category, description, amount):
        self.category = category
        self.description = description
        self.amount = amount

    def __str__(selft):
        return '<Account %s, %2.f, %s>' % (
                self.category,
                self.amount,
                self.description
            )

class Transaction:

    def __init__(self, date, amount, description, accounts):
        assert type(accounts) is list, '"accounts must be list"'
        assert len(accounts) > 0, '"accounts" mustn\'t be empty'
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

        # Header
        result.append('!Type:Cash')

        # Date
        result.append('D' + self.date.strftime('%m/%d/%y'))

        # Amount
        result.append('T' + '%.2f' % self.amount)

        # Payee
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
                result.append('E' + account.description)

                # Dollar amount of split
                result.append('$' + '%.2f' % account.amount)

        # End of the entry
        result.append('^')

        return result
