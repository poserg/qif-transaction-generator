import json as j
import datetime
import logging

from . models import Item, Receipt

logger = logging.getLogger(__name__)


def from_string_to_json(raw):
    assert raw, 'raw mustn\'t be empty'
    # escape_raw = raw.replace('"', '\\"').replace('\'', '"')
    # logger.debug('escape_raw: %s ', escape_raw)
    result = j.loads(raw)
    return result[0] if isinstance(result, list) else result


def parse_receipt(json):
    assert isinstance(json, dict), 'json must be a dict'

    receipt = Receipt()
    r = json
    if r.get('ticket'):
        r = r.get('ticket')
    if r.get('document') and r.get('document').get('receipt'):
        r = r['document']['receipt']
    receipt.ecash_total_sum = r['ecashTotalSum']
    receipt.cash_total_sum = r['cashTotalSum']
    receipt.total_sum = r['totalSum']
    receipt.purchase_date = _parse_datetime(r['dateTime'])

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


def _parse_datetime(dt):
    return datetime.datetime.fromtimestamp(dt) \
        if isinstance(dt, int) \
        else datetime.datetime.fromisoformat(dt)
