import unittest
import unittest.mock as mock
from qif_transaction_generator.gnucash import parse_accounts
from qif_transaction_generator.models import Account, AccountTypeEnum


class TestGnucash(unittest.TestCase):

    @mock.patch('qif_transaction_generator.gnucash.ET.parse')
    def test_call_et_parse(self, mock_ET_parse):
        result = parse_accounts('test_path')

        mock_ET_parse.assert_called_once_with('test_path')
        self.assertEqual(result, [])

    def test_parsing(self):
        root = Account(
            guid='d6578d8d7fb99ccfe79bdf5e763e381f',
            name='Root Account',
            account_type_id=AccountTypeEnum.ROOT.value)
        income = Account(
            guid='f8e1db6218575d4f062ac4c30325699a',
            name='Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='d6578d8d7fb99ccfe79bdf5e763e381f')

        result = parse_accounts(
            'qif_transaction_generator/tests/test_accounts.gnucash')

        self.assertEqual(len(result), 2)
        self._assert_account_equal(result[0], root)
        self._assert_account_equal(result[1], income)

    def _assert_account_equal(self, o1, o2):
        self.assertEqual(o1.guid, o2.guid)
        self.assertEqual(o1.name, o2.name)
        self.assertEqual(o1.description, o2.description)
        self.assertEqual(o1.parent_guid, o2.parent_guid)
        self.assertEqual(o1.account_type_id, o2.account_type_id)
