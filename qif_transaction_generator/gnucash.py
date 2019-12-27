import logging
import xml.etree.ElementTree as ET

from qif_transaction_generator.models import Account, AccountTypeEnum

logger = logging.getLogger(__name__)

account_xpath = '{http://www.gnucash.org/XML/gnc}account'
name_xpath = '{http://www.gnucash.org/XML/act}name'
id_xpath = '{http://www.gnucash.org/XML/act}id'
type_xpath = '{http://www.gnucash.org/XML/act}type'
parent_xpath = '{http://www.gnucash.org/XML/act}parent'
description_xpath = '{http://www.gnucash.org/XML/act}description'


def parse_accounts(file_path):
    tree = ET.parse(file_path)

    accounts = []
    for account in tree.iterfind(account_xpath):
        logger.debug('process account')

        a = Account()
        for item in account:
            if id_xpath == item.tag:
                a.guid = item.text
            elif name_xpath == item.tag:
                a.name = item.text
            elif description_xpath == item.tag:
                a.description = item.text
            elif parent_xpath == item.tag:
                a.parent_guid = item.text
            elif type_xpath == item.tag:
                a.account_type_id = AccountTypeEnum[item.text].value
        logger.debug('new account: %s', a)
        accounts.append(a)

    return accounts


def set_up_account_names(accounts):
    '''
    В имя счёта добавляется имя родительского счёта
    '''
    d = {}
    for a in accounts:
        d[a.guid] = a
    for a in accounts:
        a.full_name = _get_full_account_name(d, a.guid)


def _get_full_account_name(d, guid):
    # import pdb; pdb.set_trace()
    logger.debug('start _get_full_account_name(%s)', guid)
    account = d[guid]
    logger.debug('account\'s name is %s; parent guid is %s',
                 account.name, account.parent_guid)
    name = account.name
    if AccountTypeEnum.ROOT.value == account.account_type_id:
        logger.debug('account type is ROOT. Will be used empty name')
        name = ''
    if account.parent_guid:
        logger.debug('has parent')
        parent_name = _get_full_account_name(d, account.parent_guid)
        if len(parent_name) == 0:
            return name
        else:
            return parent_name + ':' + name
    else:
        logger.debug('hasn\'t parent')
        return name


def get_difference_list(accounts, db_accounts):
    to_delete = []
    to_add = []
    to_modify = []
    for a in accounts:
        is_exist = False
        for db_a in db_accounts:
            if a.guid == db_a.guid:
                is_exist = True
                if not a.equals(db_a):
                    db_a.update_value(a)
                    to_modify.append(db_a)
                break
        if not is_exist:
            to_add.append(a)

    for db_a in db_accounts:
        is_exist = False
        for a in accounts:
            if db_a.guid == a.guid:
                is_exist = True
                break
        if not is_exist:
            to_delete.append(db_a)

    return to_add, to_delete, to_modify
