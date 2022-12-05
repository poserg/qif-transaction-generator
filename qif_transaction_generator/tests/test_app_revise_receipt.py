import unittest
import unittest.mock as mock

from qif_transaction_generator.app import App
from qif_transaction_generator.config import Config
from qif_transaction_generator.dao import DBUtil
from qif_transaction_generator.models import FnsReceipt, StatusEnum


class TestAppProcessReviseReceipt(unittest.TestCase):

    @mock.patch.object(DBUtil, '__init__', lambda x, y: None)
    def setUp(self):
        config = Config()
        config.dbpath = 'dbpath'
        config.login = 'test_login'
        config.password = 'test_password'

        self.app = App()
        self.app.init()

    @mock.patch('qif_transaction_generator.app.revise_info')
    @mock.patch('qif_transaction_generator.app.check_receipt')
    @mock.patch(
        'qif_transaction_generator.dao.DBUtil.get_receipt_by_status')
    def test_process_revise_receipt(self,
                                    mock_get_receipt_by_status,
                                    mock_check_receipt,
                                    mock_revise_info):
        self.app._process_revise_receipt('test_session')

        mock_get_receipt_by_status.assert_called_once_with(
            'test_session', [1, 3])

        mock_check_receipt.assert_not_called()
        mock_revise_info.assert_not_called()

    @mock.patch('qif_transaction_generator.app.revise_info')
    @mock.patch('qif_transaction_generator.app.check_receipt')
    @mock.patch('qif_transaction_generator.dao.DBUtil.get_receipt_by_status')
    def test_false_check_receipt(self,
                                 mock_get_receipt_by_status,
                                 mock_check_receipt,
                                 mock_revise_info):
        r = FnsReceipt(status_id=StatusEnum.CREATED.value)
        mock_get_receipt_by_status.return_value = [r]
        mock_check_receipt.return_value = False

        self.app._process_revise_receipt('test_session')

        self.assertEqual(r.status_id, StatusEnum.NOT_FOUND.value)
        mock_check_receipt.assert_called_once_with(r)
        mock_revise_info.assert_not_called()

    @mock.patch('qif_transaction_generator.app.revise_info')
    @mock.patch('qif_transaction_generator.app.check_receipt')
    @mock.patch('qif_transaction_generator.dao.DBUtil.get_receipt_by_status')
    def test_true_check_receipt(self,
                                mock_get_receipt_by_status,
                                mock_check_receipt,
                                mock_revise_info):
        r = FnsReceipt(status_id=StatusEnum.CREATED.value)
        mock_get_receipt_by_status.return_value = [r]
        mock_check_receipt.return_value = True
        mock_revise_info.return_value = '[{]'

        self.app._process_revise_receipt('test_session')

        self.assertEqual(r.status_id, StatusEnum.NOT_FOUND.value)
        mock_check_receipt.assert_called_once_with(r)
        mock_revise_info.assert_called_once_with(
            r, 'test_login', 'test_password')

    @mock.patch('qif_transaction_generator.app.revise_info')
    @mock.patch('qif_transaction_generator.app.check_receipt')
    @mock.patch('qif_transaction_generator.dao.DBUtil.get_receipt_by_status')
    def test_true_check_and_parse_receipt(self,
                                          mock_get_receipt_by_status,
                                          mock_check_receipt,
                                          mock_revise_info):
        r = FnsReceipt(id=2, status_id=StatusEnum.CREATED.value)
        mock_get_receipt_by_status.return_value = [r]
        mock_check_receipt.return_value = True

        mock_info = mock.MagicMock()
        mock_revise_info.return_value = mock_info
        mock_info.json.return_value = '{[]}'
        mock_session = mock.MagicMock()

        self.app._process_revise_receipt(mock_session)

        self.assertEqual(r.status_id, StatusEnum.LOADED.value)
        mock_check_receipt.assert_called_once_with(r)
        mock_revise_info.assert_called_once_with(
            r, 'test_login', 'test_password')

        mock_session.add.assert_called_once()
        arg = mock_session.add.call_args_list[0][0][0]
        self.assertEqual(arg.status_id, 4)
        self.assertEqual(arg.fns_receipt_id, 2)
        self.assertEqual(arg.raw, '{[]}')
