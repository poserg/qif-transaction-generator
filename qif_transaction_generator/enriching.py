import logging
import re

from . json_utils import from_string_to_json, parse_receipt
from . models import StatusEnum

logger = logging.getLogger(__name__)


def enrich_receipt(db_util, receipt_id):
    assert db_util
    assert receipt_id
    logger.info('process receipt(%s)', receipt_id)
    session = db_util.begin_session()
    try:
        receipt = db_util.get_receipt_by_id(session, [receipt_id])[0]
        if receipt.raw is None:
            logger.error('raw is empty for receipt(%s)', receipt.id)
        else:
            if not receipt.items or len(receipt.items) == 0:
                _enrich_receipt_items_from_json(receipt)
            if not receipt.items or len(receipt.items) == 0:
                logger.warning('receipt doesn\'t have any items')
                return

            undefined_items = _bind_items_to_categories(
                db_util, receipt)
            if len(undefined_items) == 0:
                logger.info(
                    'all items were found for receipt(%d)',
                    receipt.id)
                receipt.status_id = StatusEnum.DONE.value
                session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def _enrich_receipt_items_from_json(receipt):
    logger.debug('start enrich receipt items from json for %s', receipt.id)
    # assert receipt.items is None or len(
    #    receipt.items) == 0, 'items must be empty'

    try:
        json = from_string_to_json(receipt.raw)
        try:
            parse = parse_receipt(json)
            receipt.ecash_total_sum = parse.ecash_total_sum
            receipt.cash_total_sum = parse.cash_total_sum
            receipt.total = parse.total_sum
            receipt.purchase_date = parse.purchase_date
            receipt.items = parse.items
        except Exception as e:
            logger.exception(
                'Couldn\'t parse json. It\'s a wrong format: %s, %s',
                e, json)
    except Exception as e:
        logger.exception(
            'Couldn\'t convert raw to json. %s : %s', e, receipt.raw)


def _bind_items_to_categories(db_util, receipt):
    logger.debug('start bind_items_to_categories')
    undefined_items = []
    for item in receipt.items:
        logger.debug('item\'s name is \'%s\'', item.name)
        if item.account_guid:
            logger.debug('item\'s had being bound \'%s\'', item.account_guid)
            continue
        if item.price == 0:
            logger.debug('item is free')
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
            logger.warning(
                'dictionaries weren\'t found for item: %s', item.name)
            undefined_items.append(item)

    logger.debug('finish bind_items_to_categories')
    return undefined_items


def _get_phrases(value):
    v = value.lower()
    v = re.sub('^\\d+', '', v)
    v = v.strip()
    result = []
    result.append(v)

    split = v.split(' ')
    if len(split) > 3:
        result.append(' '.join(split[:3]))
    if len(split) > 1:
        result.extend(split[:3])
    return result
