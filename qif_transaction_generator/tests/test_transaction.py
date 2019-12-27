# -*- coding: utf-8 -*-

import unittest

import datetime

import qif_transaction_generator.models as models
import qif_transaction_generator.transaction as transaction

class TestConvertReceiptsToQIFTransaction(unittest.TestCase):

    def positive_case(self):
        a1 = models.Account(full_name='Account 1')
        i1 = models.Item(name='item 1', sum=100, account=a1)
        a2 = models.Account(full_name='Account 2')
        i2 = models.Item(name='item 2', sum=200, account=a2)
        r = models.Receipt(id='receipt_1',
                           purchase_date='my date',
                           total='300', items=[i1, i2])
        result = transaction.convert([r])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].source, 'test')
        self.assertEqual(result[0].date, 'my date')
        self.assertEqual(result[0].amount, 3)
        self.assertEqual(result[0].description, None)

        self.assertEqual(len(result[0].accounts), 2)
        self.assertEqual(result[0].accounts[0].category, a1.full_name)
        self.assertEqual(result[0].accounts[0].description, None)
        self.assertEqual(result[0].accounts[0].amount, 100)

        self.assertEqual(result[0].accounts[1].category, a2.full_name)
        self.assertEqual(result[0].accounts[1].description, None)
        self.assertEqual(result[0].accounts[1].amount, 200)

    def test_with_empty_accounts(self):
        r = models.Receipt(id='receipt_1',
                   purchase_date='my date',
                   total='300', items=[])

        self.assertRaises(AssertionError, transaction.convert, [r])

    def test_with_empty_receipts(self):
        result = transaction.convert([])

        self.assertEqual(result, [])

class TestDumpQIFTransaction(unittest.TestCase):

    def test_case_with_split_transaction(self):
        a1 = transaction.Account(
            'Расходы:Питание:дома:Продукты:Молочные продукты:Йогурт',
            'description for dinning',
            1200)
        a2 = transaction.Account(
            'Расходы:Телефон:My',
            'description for gloceries',
            1500)
        t = transaction.Transaction(
            'Активы:Текущие активы:Оборотный капитал:Alfa card',
            datetime.datetime(2019, 2, 20), 2700,
            'My main description',
            [a1, a2])

        result = t.dump()

        self.assertEqual(len(result), 15)
        self.assertEqual(result[0], '!Account')
        self.assertEqual(result[1], 'NАктивы:Текущие активы:Оборотный капитал:Alfa card')
        self.assertEqual(result[2], 'TCash')
        self.assertEqual(result[3], '^')
        self.assertEqual(result[4], '!Type:Cash')
        self.assertEqual(result[5], 'D02/20/2019')
        self.assertEqual(result[6], 'U-2700.00')
        self.assertEqual(result[7], 'PMy main description')
        self.assertEqual(result[8], 'SРасходы:Питание:дома:Продукты:Молочные продукты:Йогурт')
        self.assertEqual(result[9], 'Edescription for dinning')
        self.assertEqual(result[10], '$-1200.00')
        self.assertEqual(result[11], 'SРасходы:Телефон:My')
        self.assertEqual(result[12], 'Edescription for gloceries')
        self.assertEqual(result[13], '$-1500.00')
        self.assertEqual(result[14], '^')

    def test_case_with_unite_transaction(self):
        a = transaction.Account(
            'Expenses:Phone',
            'unite transaction',
            500)
        t = transaction.Transaction(
            'cash account',
            datetime.datetime(2018, 8, 8),
            500,
            'to my mobile phone',
            [a])

        result = t.dump()

        self.assertEqual(len(result), 10)
        self.assertEqual(result[0], '!Account')
        self.assertEqual(result[1], 'Ncash account')
        self.assertEqual(result[2], 'TCash')
        self.assertEqual(result[3], '^')
        self.assertEqual(result[4], '!Type:Cash')
        self.assertEqual(result[5], 'D08/08/2018')
        self.assertEqual(result[6], 'U-500.00')
        self.assertEqual(result[7], 'Pto my mobile phone')
        self.assertEqual(result[8], 'LExpenses:Phone')
        self.assertEqual(result[9], '^')

    def test_split_transaction_without_description(self):
        a1 = transaction.Account(
            'Расходы:Питание:дома:Продукты:Молочные продукты:Йогурт',
            'description for dinning',
            1200)
        a2 = transaction.Account(
            'Расходы:Телефон:My',
            None,
            1500)
        t = transaction.Transaction(
            'Активы:Текущие активы:Оборотный капитал:Alfa card',
            datetime.datetime(2019, 2, 20), 2700,
            'My main description',
            [a1, a2])

        result = t.dump()

        self.assertEqual(len(result), 14)
        self.assertEqual(result[0], '!Account')
        self.assertEqual(result[1], 'NАктивы:Текущие активы:Оборотный капитал:Alfa card')
        self.assertEqual(result[2], 'TCash')
        self.assertEqual(result[3], '^')
        self.assertEqual(result[4], '!Type:Cash')
        self.assertEqual(result[5], 'D02/20/2019')
        self.assertEqual(result[6], 'U-2700.00')
        self.assertEqual(result[7], 'PMy main description')
        self.assertEqual(result[8], 'SРасходы:Питание:дома:Продукты:Молочные продукты:Йогурт')
        self.assertEqual(result[9], 'Edescription for dinning')
        self.assertEqual(result[10], '$-1200.00')
        self.assertEqual(result[11], 'SРасходы:Телефон:My')
        self.assertEqual(result[12], '$-1500.00')
        self.assertEqual(result[13], '^')

    def test_unite_transaction_without_description(self):
        a = transaction.Account(
            'Expenses:Phone',
            'unite transaction',
            500)
        t = transaction.Transaction(
            'cash account',
            datetime.datetime(2018, 8, 8),
            500,
            None,
            [a])

        result = t.dump()

        self.assertEqual(len(result), 9)
        self.assertEqual(result[0], '!Account')
        self.assertEqual(result[1], 'Ncash account')
        self.assertEqual(result[2], 'TCash')
        self.assertEqual(result[3], '^')
        self.assertEqual(result[4], '!Type:Cash')
        self.assertEqual(result[5], 'D08/08/2018')
        self.assertEqual(result[6], 'U-500.00')
        self.assertEqual(result[7], 'LExpenses:Phone')
        self.assertEqual(result[8], '^')
