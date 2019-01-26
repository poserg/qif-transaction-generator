import json as j
import logging

from qif_transaction_generator.models import Item

logger = logging.getLogger(__name__)


def from_string_to_json(raw):
    assert raw, 'raw mustn\'t be empty'
    return j.loads(raw.replace('"', '\\"').replace('\'', '"'))


def parse_receipt(receipt, json):
    assert receipt.items is None or len(receipt.items) == 0, 'items must be empty'
    if 'document' not in json.keys() or 'receipt' not in json['document'].keys():
        logger.error('json doesn\'t contain document.receipt')
    else:
        r = json['document']['receipt']
        receipt.ecash_total_sum = r['ecashTotalSum']
        receipt.cash_total_sum = r['cashTotalSum']

        if 'items' not in r.keys():
            logger.error('json doesn\t contain document.receipt.items')
        else:
            receipt.items = []
            for i in r['items']:
                logger.debug('process item %s', i)
                item = Item()
                item.name = i['name']
                item.price = i['price']
                item.quantity = i['quantity']
                item.sum = i['sum']

                receipt.items.append(item)
