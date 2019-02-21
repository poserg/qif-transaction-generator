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
