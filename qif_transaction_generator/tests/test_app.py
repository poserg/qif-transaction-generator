import unittest
import unittest.mock as mock
from unittest.mock import call

from datetime import datetime

from qif_transaction_generator.app import App
from qif_transaction_generator.config import Config
from qif_transaction_generator.dao import DBUtil
from qif_transaction_generator.models import Account, Item


class TestAppWithoutInit(unittest.TestCase):

    @mock.patch.object(DBUtil, '__init__', lambda x, y: None)
    @mock.patch(
        'qif_transaction_generator.dao.DBUtil.create_receipt')
    def test_db_util_assert(self, mock_db_util_create_receipt):
        today = datetime.today()

        self.app = App()
        self.assertRaises(AttributeError, self.app.add_receipt, 'fn', 'fp',
                          'fd', today.isoformat(), '123')

        self.app.init()
        self.app.add_receipt('fn', 'fp', 'fd', today.isoformat(), '123')
        self.assertEqual(mock_db_util_create_receipt.call_count, 1)


class TestAppAddReceipt(unittest.TestCase):

    @mock.patch.object(DBUtil, '__init__', lambda x, y: None)
    def setUp(self):
        config = Config()
        config.dbpath = 'dbpath'

        self.app = App()
        self.app.init()

    @mock.patch(
        'qif_transaction_generator.dao.DBUtil.create_receipt')
    def test_add_receipt_good_case(self, mock_db_util_create_receipt):
        today = datetime.today()

        self.app.add_receipt('fn', 'fp', 'fd', today.isoformat(), '123')
        self.assertEqual(mock_db_util_create_receipt.call_count, 1)

        name, args, kwargs = mock_db_util_create_receipt.mock_calls[0]
        self.assertEqual(args[0].fn, 'fn')
        self.assertEqual(args[0].fp, 'fp')
        self.assertEqual(args[0].fd, 'fd')
        self.assertEqual(args[0].purchase_date, today)
        self.assertEqual(args[0].total, '123')
        self.assertEqual(args[0].status_id, 1)

    def test_add_receipt_date_parse_raise(self):
        self.assertRaises(ValueError, self.app.add_receipt, 'fn', 'fp', 'fd',
                          'today', '123')


class TestAppAddPhrase(unittest.TestCase):

    @mock.patch.object(DBUtil, '__init__', lambda x, y: None)
    def setUp(self):
        config = Config()
        config.dbpath = 'dbpath'
        config.args = type("TestArgs", (object,), {})()
        config.args.guid = 'test_guid'
        config.args.phrase = 'test_phrase'

        self.app = App()
        self.app.init()

    @mock.patch('qif_transaction_generator.dao.DBUtil.create')
    def test_add_phrase_good_case(self, mock_db_util_create):
        self.app.add_phrase()
        self.assertEqual(mock_db_util_create.call_count, 1)
        name, args, kwargs = mock_db_util_create.mock_calls[0]
        self.assertEqual(args[0].account_guid, 'test_guid')
        self.assertEqual(args[0].phrase, 'test_phrase')
        self.assertEqual(args[0].weight, 0)


class TestAppSearchAccounts(unittest.TestCase):

    def test_search_accounts(self):
        app = App()
        app.db_util = mock.Mock()

        root = Account(
            guid='root_guid',
            name='Root Account',
            full_name='Root Account')
        income = Account(
            guid='income_guid',
            name='Income Account',
            full_name='Income Account')

        app.db_util.search_accounts.return_value = [root, income]

        result = app.search_accounts('search text')
        app.db_util.search_accounts.assert_called_once_with('search text')
        self.assertEqual(result, [root, income])

    def test_search_accounts_with_empty_result(self):
        app = App()
        app.db_util = mock.Mock()

        app.db_util.search_accounts.return_value = []
        result = app.search_accounts('search text')
        app.db_util.search_accounts.assert_called_once_with('search text')
        self.assertEqual(result, None)

    def test_search_accounts_without_result(self):
        app = App()
        app.db_util = mock.Mock()

        app.db_util.search_accounts.return_value = None
        result = app.search_accounts('search text')
        app.db_util.search_accounts.assert_called_once_with('search text')
        self.assertEqual(result, None)


class TestAppEnrichReceipts(unittest.TestCase):

    def setUp(self):
        self.app = App()
        self.app.db_util = mock.Mock()

    @mock.patch('qif_transaction_generator.app.enrich_receipt')
    def test_enrich_without_receipts(self, mock_enrich_receipt):
        self.app.db_util.get_receipt_without_items_by_status.return_value = []
        self.app.enrich_receipts()
        mock_enrich_receipt.assert_not_called()

    @mock.patch('qif_transaction_generator.app.enrich_receipt')
    def test_enrich_one_receipt(self, mock_enrich_receipt):
        self.app.db_util.get_receipt_without_items_by_status.return_value = [
            Item(id=3)]
        self.app.enrich_receipts()

        mock_enrich_receipt.assert_called_once_with(self.app.db_util, 3)

    @mock.patch('qif_transaction_generator.app.enrich_receipt')
    def test_enrich_multiple_receipts(self, mock_enrich_receipt):
        self.app.db_util.get_receipt_without_items_by_status.return_value = \
            [Item(id=6), Item(id=3), Item(id=8)]
        self.app.enrich_receipts()

        self.assertEqual(mock_enrich_receipt.call_args_list, [
            call(self.app.db_util, 6),
            call(self.app.db_util, 3),
            call(self.app.db_util, 8)])
