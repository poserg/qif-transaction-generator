import logging

from qif_transaction_generator.json_utils import from_string_to_json, \
    parse_receipt

logger = logging.getLogger(__name__)


def enrich_receipt_items_from_json(receipt):
    assert receipt.items is None or len(
        receipt.items) == 0, 'items must be empty'

    try:
        json = from_string_to_json(receipt.raw)
        try:
            parse = parse_receipt(json)
            receipt.ecash_total_sum = parse.ecash_total_sum
            receipt.cash_total_sum = parse.cash_total_sum
            receipt.items = parse.items
        except Exception as e:
            logger.exception('Couldn\'t parse json. It\'s a wrong format: %s, %s',
                         e, json)
    except Exception as e:
        logger.exception('Couldn\'t convert raw to json. %s', receipt.raw)
