import unittest
import unittest.mock as mock

from qif_transaction_generator.app import App
from qif_transaction_generator.config import Config
from qif_transaction_generator.dao import DBUtil
from qif_transaction_generator.models import FnsReceipt, StatusEnum,\
    Receipt


class TestAppGenerateTransaction(unittest.TestCase):

    @mock.patch.object(DBUtil, '__init__', lambda x, y: None)
    def setUp(self):
        config = Config()
        config.dbpath = 'dbpath'
        config.login = 'test_login'
        config.password = 'test_password'

        self.app = App()
        self.app.init()

    @mock.patch('qif_transaction_generator.app.convert')
    @mock.patch(
        'qif_transaction_generator.dao.DBUtil.get_receipts_by_status_with_items_and_accounts')
    def test_missing_receipts(self,
                              mock_get_receipts_by_status_with_items_and_accounts,
                              mock_convert):
        mock_get_receipts_by_status_with_items_and_accounts.return_value = []
        self.app.generate_transaction('test_session')

        mock_get_receipts_by_status_with_items_and_accounts.assert_called_once_with([5])
        mock_convert.assert_not_called()

    @mock.patch('qif_transaction_generator.app.convert')
    @mock.patch(
        'qif_transaction_generator.dao.DBUtil.get_receipts_by_status_with_items_and_accounts')
    def test_with_receipts(self,
                           mock_get_receipts_by_status_with_items_and_accounts,
                           mock_convert):
        mock_get_receipts_by_status_with_items_and_accounts.return_value = ['receipt1', 'receipt2']
        self.app.generate_transaction('test_session')

        mock_get_receipts_by_status_with_items_and_accounts.assert_called_once_with([5])
        mock_convert.assert_called_once_with(['receipt1', 'receipt2'])

    @mock.patch('qif_transaction_generator.app.convert')
    @mock.patch(
        'qif_transaction_generator.dao.DBUtil.get_receipts_by_status_with_items_and_accounts')
    def test_with_receipts_transaction(self,
                                       mock_get_receipts_by_status_with_items_and_accounts,
                                       mock_convert):
        mock_get_receipts_by_status_with_items_and_accounts.return_value = ['receipt1', 'receipt2']
        mock_out_file = mock.Mock()
        mock_t1 = mock.Mock()
        mock_t1.dump.return_value = ['item1', 'item2']
        mock_t2 = mock.Mock()
        mock_t2.dump.return_value = ['item3']
        mock_t3 = mock.Mock()
        mock_t3.dump.return_value = []
        mock_convert.return_value = [mock_t1, mock_t2, mock_t3]
        self.app.generate_transaction(mock_out_file)

        mock_get_receipts_by_status_with_items_and_accounts.assert_called_once_with([5])
        mock_convert.assert_called_once_with(['receipt1', 'receipt2'])
        mock_t1.dump.assert_called_once()
        mock_t2.dump.assert_called_once()
        mock_t3.dump.assert_called_once()
        name, args, kwargs = mock_out_file.write.mock_calls[0]
        self.assertEqual(args[0], 'item1\nitem2')
        name, args, kwargs = mock_out_file.write.mock_calls[1]
        self.assertEqual(args[0], 'item3')
        name, args, kwargs = mock_out_file.write.mock_calls[2]
        self.assertEqual(args[0], '')
        self.assertEqual(mock_out_file.write.call_count, 3)
