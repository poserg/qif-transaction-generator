import unittest
from qif_transaction_generator.gnucash import get_difference_list
from qif_transaction_generator.models import Account, AccountTypeEnum


class TestSyncAccounts(unittest.TestCase):

    def test_get_difference_list(self):
        root = Account(
            guid='root_guid',
            name='Root Account',
            account_type_id=AccountTypeEnum.ROOT.value)
        income1 = Account(
            guid='income_guid',
            name='Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid')
        salary = Account(
            guid='salary_guid',
            name='Salary',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Salary',
            parent_guid='income_guid')
        income1_modify = Account(
            guid='income_guid',
            name='RootAccount:Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid')
        income2 = Account(
            guid='income 2 guid',
            name='Income 2',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid')
        db_accounts = [root, income1, salary]
        accounts = [root, income1_modify, income2]
        to_add, to_delete, to_modify = get_difference_list(accounts, db_accounts)

        self.assertListEqual(to_add, [income2])
        self.assertListEqual(to_delete, [salary])
        self.assertTrue(len(to_modify) == 1)
        self.assertTrue(to_modify[0].equals(income1_modify))

    def test_get_difference_list_without_modifying(self):
        root = Account(
            guid='root_guid',
            name='Root Account',
            account_type_id=AccountTypeEnum.ROOT.value)
        income1 = Account(
            guid='income_guid',
            name='Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid')
        income1_clone = Account(
            guid='income_guid',
            name='Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid')
        db_accounts = [root, income1]
        accounts = [root, income1_clone]
        to_add, to_delete, to_modify = get_difference_list(accounts, db_accounts)

        self.assertEqual(len(to_add), 0)
        self.assertEqual(len(to_delete), 0)
        self.assertEqual(len(to_modify), 0)

    def test_sync_with_different_full_names(self):
        root = Account(
            guid='root_guid',
            name='Root Account',
            account_type_id=AccountTypeEnum.ROOT.value,
            full_name='Root Account')
        income1 = Account(
            guid='income_guid',
            name='Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid',
            full_name='Root Account:Income')
        root_modify = Account(
            guid='root_guid',
            name='Root Account',
            account_type_id=AccountTypeEnum.ROOT.value,
            full_name='')
        income1_modify = Account(
            guid='income_guid',
            name='Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid',
            full_name='Income')
        income2 = Account(
            guid='income 2 guid',
            name='Income 2',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid',
            full_name='Income 2')
        db_accounts = [root, income1]
        accounts = [root_modify, income1_modify, income2]
        to_add, to_delete, to_modify = get_difference_list(accounts, db_accounts)

        self.assertListEqual(to_add, [income2])
        self.assertListEqual(to_delete, [])
        self.assertTrue(len(to_modify) == 2)
        self.assertTrue(to_modify[0].equals(root_modify))
        self.assertTrue(to_modify[1].equals(income1_modify))
