import json as j
import logging

from qif_transaction_generator.models import Item, Receipt

logger = logging.getLogger(__name__)


def from_string_to_json(raw):
    assert raw, 'raw mustn\'t be empty'
    # escape_raw = raw.replace('"', '\\"').replace('\'', '"')
    # logger.debug('escape_raw: %s ', escape_raw)
    return j.loads(raw)


def parse_receipt(json):
    assert isinstance(json, dict), 'json must be a dict'

    receipt = Receipt()
    if json.get('document') and json.get('document').get('receipt'):
        r = json['document']['receipt']
    else:
        r = json
    receipt.ecash_total_sum = r['ecashTotalSum']
    receipt.cash_total_sum = r['cashTotalSum']

    receipt.items = []
    for i in r['items']:
        logger.debug('process item %s', i)
        item = Item()
        item.name = i['name']
        item.price = i['price']
        item.quantity = i['quantity']
        item.sum = i['sum']

        receipt.items.append(item)

    return receipt
