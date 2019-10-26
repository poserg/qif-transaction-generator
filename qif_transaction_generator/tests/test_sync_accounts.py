import unittest
from qif_transaction_generator.gnucash import get_difference_list, \
    set_up_account_names
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
        db_accounts = [root, income1]
        accounts = [root, income1_modify, income2]
        to_add, to_delete, to_modify = get_difference_list(accounts, db_accounts)

        self.assertListEqual(to_add, [income2])
        self.assertListEqual(to_delete, [])
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
        print (accounts)
        set_up_account_names(accounts)

        print (accounts)
        self.assertTrue(accounts[0].equals(Account(
            guid='sub_income_guid',
            full_name='Root Account:Income:Sub Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Sub Income',
            parent_guid='income_guid',
            name='Sub Income')))
        self.assertTrue(accounts[1].equals(Account(
            guid='root_guid',
            name='Root Account',
            account_type_id=AccountTypeEnum.ROOT.value,
            full_name='Root Account')))
        self.assertTrue(accounts[2].equals(Account(
            guid='income_guid',
            full_name='Root Account:Income',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Income',
            parent_guid='root_guid',
            name='Income')))
        self.assertTrue(accounts[3].equals(Account(
            guid='sub_income_guid2',
            full_name='Root Account:Income:Sub Income2',
            account_type_id=AccountTypeEnum.INCOME.value,
            description='Sub Income',
            parent_guid='income_guid',
            name='Sub Income2')))
