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


def bind_items_to_categories(db_util, receipt):
    logger.debug('start bind_items_to_categories')
    result = []
    for item in receipt.items:
        logger.debug('item\'s name is \'%s\'', item.name)
        if item.account_guid:
            logger.debug('item\'s had being bound \'%s\'', itme.account_guid)
            continue
        phrases = _get_phrases(item.name)
        logger.debug('phrases: %s', phrases)
        d = db_util.get_dictionaries_by_phrases(phrases)
        logger.debug('dictionaries: %s', d)

        if d:
            item.account_guid = d[0].account_guid
            d[0].weight = d[0].weight + 1
            logger.debug('set weight %d for dictionary %s', d[0].weight, d[0])
        else:
            logger.warn('dictionaries weren\'t found for item: %s', item.name)
            result.append(item)

    logger.debug('finish bind_items_to_categories')
    return result


def _get_phrases(value):
    v = value.lower()
    result = []
    result.append(v)

    split = v.split(' ')
    if len(split) > 3:
        result.append(' '.join(split[:3]))
    result.extend(split)
    return result
