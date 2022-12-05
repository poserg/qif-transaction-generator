import unittest
import unittest.mock as mock
from qif_transaction_generator.gnucash import parse_accounts,\
    set_up_account_names
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


class TestSetUpAccountNames(unittest.TestCase):

    def test_set_up_account_names(self):
        root = Account(
            guid='root_guid',
            name='Root Account',
            account_type_id=AccountTypeEnum.ROOT.value)
        income = Account(
            guid='income_guid',
            name='Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid')
        sub_income = Account(
            guid='sub_income_guid',
            name='Sub Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Sub Income',
            parent_guid='income_guid')
        sub_income2 = Account(
            guid='sub_income_guid2',
            name='Sub Income2',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Sub Income',
            parent_guid='income_guid')

        accounts = [sub_income, root, income, sub_income2]
        print(accounts)
        set_up_account_names(accounts)

        print(accounts)
        self.assertTrue(accounts[0].equals(Account(
            guid='sub_income_guid',
            full_name='Income:Sub Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Sub Income',
            parent_guid='income_guid',
            name='Sub Income')))
        self.assertTrue(accounts[1].equals(Account(
            guid='root_guid',
            name='Root Account',
            account_type_id=AccountTypeEnum.ROOT.value,
            full_name='')))
        self.assertTrue(accounts[2].equals(Account(
            guid='income_guid',
            full_name='Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid',
            name='Income')))
        self.assertTrue(accounts[3].equals(Account(
            guid='sub_income_guid2',
            full_name='Income:Sub Income2',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Sub Income',
            parent_guid='income_guid',
            name='Sub Income2')))

    def test_full_names(self):
        root = Account(
            guid='root_guid',
            name='Root Account',
            account_type_id=AccountTypeEnum.ROOT.value)
        income = Account(
            guid='income_guid',
            name='Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid')
        cash = Account(
            guid='cash_guid',
            name='Cash',
            account_type_id=AccountTypeEnum.CASH.value,
            description='Cash in wallet',
            parent_guid='root_guid')
        salary = Account(
            guid='salary_guid',
            name='Salary',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='My salary',
            parent_guid='income_guid')
        expense = Account(
            guid='expense_guid',
            name='Expense',
            account_type_id=AccountTypeEnum.EXPENSE.value,
            description='Expense',
            parent_guid='root_guid')
        phone = Account(
            guid='phone_guid',
            name='Mobile phone',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='phone',
            parent_guid='expense_guid')

        set_up_account_names([income, root, cash, expense, salary, phone])

        self.assertEqual(root.full_name, '')
        self.assertEqual(income.full_name, 'Income')
        self.assertEqual(cash.full_name, 'Cash')
        self.assertEqual(salary.full_name, 'Income:Salary')
        self.assertEqual(expense.full_name, 'Expense')
        self.assertEqual(phone.full_name, 'Expense:Mobile phone')
