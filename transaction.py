# -*- coding: utf-8 -*-

class Transaction:

    def __init__(self, date, amount, description, target_account):
        self.date = date
        self.amount = amount
        self.description = description
        self.target_account = target_account

    def __str__(self):
        return '<Transaction %s, %s, %s, %s>'% (
            self.date,
            self.amount,
            self.description,
            self.target_account
        )

    def to_qif_line(self):
        result = []

        # Header
        result.append('!Type:Cash')

        # Date
        result.append('D' + self.date.strftime('%m/%d/%y'))

        # Amount
        result.append('T' + '%.2f' % self.amount)

        # Payee
        result.append('P' + self.description)

        if type(self.target_account) is str:
            # Category
            result.append('L' + self.target_account)
        elif type(self.target_account) is list:
            for account in self.target_account:
                # Category in split
                result.append('S' + account.category)

                # Memo in split
                result.append('E' + account.description)

                # Dollar amount of split
                result.append('$' + '%.2f' % account.amount)
        else:
            assert False, '"target_account" mustn\'t be empty'

        # End of the entry
        result.append('^')

        return result
