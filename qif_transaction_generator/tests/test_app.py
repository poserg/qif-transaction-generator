import unittest
import unittest.mock as mock

from datetime import datetime

from qif_transaction_generator.app import App
from qif_transaction_generator.config import Config
from qif_transaction_generator.dao import DBUtil


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
