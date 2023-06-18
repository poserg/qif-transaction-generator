import unittest
import unittest.mock as mock

from qif_transaction_generator.enriching import enrich_receipt,\
    _enrich_receipt_items_from_json, _bind_items_to_categories, \
    _get_phrases
from qif_transaction_generator.models import Item, Receipt, Dictionary


@mock.patch('qif_transaction_generator.enriching.from_string_to_json')
@mock.patch('qif_transaction_generator.enriching.parse_receipt')
class TestEnrichingItemsFromJson(unittest.TestCase):

    # def test_items_empty(self, mock_parse_receipt, mock_from_string_to_json):
    #     r = Receipt()
    #     r.items = [Item()]

    #     self.assertRaises(AssertionError, _enrich_receipt_items_from_json, r)

    def test_right_case(self, mock_parse_receipt, mock_from_string_to_json):
        test_receipt = Receipt()
        test_receipt.ecash_total_sum = 2
        test_receipt.cash_total_sum = 30
        test_receipt.total_sum = 32
        test_receipt.purchase_date = 'my_date'
        test_receipt.items = [
            Item(name='item_name', price=13, quantity=10, sum=130)
        ]
        mock_parse_receipt.return_value = test_receipt
        r = Receipt()
        r.raw = 'test_raw'

        _enrich_receipt_items_from_json(r)

        mock_from_string_to_json.assert_called_once_with('test_raw')
        self.assertEqual(r.ecash_total_sum, 2)
        self.assertEqual(r.cash_total_sum, 30)
        self.assertEqual(r.total, 32)
        self.assertEqual(r.purchase_date, 'my_date')
        self.assertEqual(len(r.items), 1)
        self.assertEqual(r.items[0].name, 'item_name')
        self.assertEqual(r.items[0].price, 13)
        self.assertEqual(r.items[0].quantity, 10)
        self.assertEqual(r.items[0].sum, 130)

    def test_wrong_case_from_string_to_json(self, mock_parse_receipt,
                                            mock_from_string_to_json):
        mock_from_string_to_json.side_effect = AssertionError
        r = Receipt()
        r.raw = 'test_raw'

        _enrich_receipt_items_from_json(r)

        mock_from_string_to_json.assert_called_once_with('test_raw')
        mock_parse_receipt.assert_not_called()

    def test_wrong_case_parse_receipt(self, mock_parse_receipt,
                                      mock_from_string_to_json):
        test_receipt = Receipt()
        test_receipt.ecash_total_sum = 2
        test_receipt.cash_total_sum = 30
        test_receipt.items = [
            Item(name='item_name', price=13, quantity=10, sum=130)
        ]
        mock_parse_receipt.return_value = test_receipt
        mock_from_string_to_json.return_value = 'test_json'
        mock_parse_receipt.side_effect = AssertionError
        r = Receipt()
        r.raw = 'test_raw'

        _enrich_receipt_items_from_json(r)

        mock_from_string_to_json.assert_called_once_with('test_raw')
        mock_parse_receipt.assert_called_once_with('test_json')
        self.assertIsNone(r.ecash_total_sum)
        self.assertIsNone(r.cash_total_sum)
        self.assertTrue(
            r.items is None or isinstance(r.items, list) and len(r.items) == 0)


class TestEnrichingReceipts(unittest.TestCase):

    def setUp(self):
        self.db_util = mock.Mock()
        self.session = mock.Mock()
        self.db_util.begin_session.return_value = self.session

    def test_enrich_for_empty_receipt(self):
        empty_receipt = Receipt(id='test_id')
        self.db_util.get_receipt_by_id.return_value = [empty_receipt]
        enrich_receipt(self.db_util, 1)

        self.db_util.begin_session.assert_called_once()
        self.session.commit.assert_not_called()
        self.session.rollback.assert_not_called()
        self.session.close.assert_called_once()
        self.db_util.get_receipt_by_id.assert_called_once_with(
            self.session, [1])

    @mock.patch(
        'qif_transaction_generator.enriching._enrich_receipt_items_from_json')
    @mock.patch(
        'qif_transaction_generator.enriching._bind_items_to_categories')
    def test_enrich_one_receipt(self, mock_bind_items_to_categories,
                                mock_enrich_receipt_items_from_json):
        r = Receipt(id='test_id', raw='test_raw')
        r.items = [Item()]
        self.db_util.get_receipt_by_id.return_value = [r]
        enrich_receipt(self.db_util, 2)

        self.db_util.begin_session.assert_called_once()
        self.db_util.get_receipt_by_id.assert_called_once_with(
            self.session, [2])
        self.session.commit.assert_called_once()
        self.session.rollback.assert_not_called()
        self.session.close.assert_called_once()
        mock_enrich_receipt_items_from_json.assert_not_called()
        mock_bind_items_to_categories.assert_called_once_with(self.db_util, r)
        self.assertEqual(r.status_id, 5)

    @mock.patch('qif_transaction_generator.enriching.from_string_to_json')
    @mock.patch('qif_transaction_generator.enriching.parse_receipt')
    @mock.patch(
        'qif_transaction_generator.enriching._bind_items_to_categories')
    def test_enrich_receipt_without_items(self, mock_bind_items_to_categories,
                                          mock_parse_receipt,
                                          mock_from_string_to_json):
        r = Receipt(id='test_id', raw='test_raw')
        self.db_util.get_receipt_by_id.return_value = [r]
        mock_parse_receipt.return_value.items = [Item()]
        # mock_enrich_receipt_items_from_json.return_value = [Item()]
        enrich_receipt(self.db_util, 3)

        self.db_util.begin_session.assert_called_once()
        self.db_util.get_receipt_by_id.assert_called_once_with(
            self.session, [3])
        self.session.commit.assert_called_once()
        self.session.rollback.assert_not_called()
        self.session.close.assert_called_once()
        mock_parse_receipt.assert_called_once()
        mock_bind_items_to_categories.assert_called_once_with(self.db_util, r)
        self.assertEqual(r.status_id, 5)

    @mock.patch('qif_transaction_generator.enriching.from_string_to_json')
    @mock.patch('qif_transaction_generator.enriching.parse_receipt')
    @mock.patch(
        'qif_transaction_generator.enriching._bind_items_to_categories')
    def test_enrich_without_items_after_parsing(self,
                                                mock_bind_items_to_categories,
                                                mock_parse_receipt,
                                                mock_from_string_to_json):
        r = Receipt(id='test_id', raw='test_raw', status_id=4)
        self.db_util.get_receipt_by_id.return_value = [r]
        mock_parse_receipt.return_value.items = []
        # mock_enrich_receipt_items_from_json.return_value = [Item()]
        enrich_receipt(self.db_util, 6)

        self.db_util.begin_session.assert_called_once()
        self.db_util.get_receipt_by_id.assert_called_once_with(
            self.session, [6])
        self.session.commit.assert_not_called()
        self.session.rollback.assert_not_called()
        self.session.close.assert_called_once()
        mock_parse_receipt.assert_called_once()
        mock_bind_items_to_categories.assert_not_called()
        self.assertEqual(r.status_id, 4)

    @mock.patch(
        'qif_transaction_generator.enriching._enrich_receipt_items_from_json')
    @mock.patch(
        'qif_transaction_generator.enriching._bind_items_to_categories')
    def test_enrich_receipt_with_undefined_items(self,
                                                 mock_bind_items_to_categories,
                                                 mock_enrich_items_from_json):
        r = Receipt(id='test_id', raw='test_raw', status_id=4)
        item1 = Item()
        item2 = Item()
        r.items = [item1, item2]
        self.db_util.get_receipt_by_id.return_value = [r]
        mock_bind_items_to_categories.return_value = [item1]
        enrich_receipt(self.db_util, 4)

        self.db_util.begin_session.assert_called_once()
        self.db_util.get_receipt_by_id.assert_called_once_with(
            self.session, [4])
        self.session.commit.assert_not_called()
        self.session.rollback.assert_not_called()
        self.session.close.assert_called_once()
        mock_enrich_items_from_json.assert_not_called()
        mock_bind_items_to_categories.assert_called_once_with(self.db_util, r)
        self.assertEqual(r.status_id, 4)

    def test_enrich_with_rollback(self):
        self.db_util.get_receipt_by_id.side_effect = Exception(
            'test_exception')

        with self.assertRaises(Exception):
            enrich_receipt(self.db_util, 5)

        self.session.commit.assert_not_called()
        self.session.rollback.assert_called_once()
        self.session.close.assert_called_once()


class TestBindingItems(unittest.TestCase):

    def setUp(self):
        self.db_util = mock.Mock()

    @mock.patch('qif_transaction_generator.enriching._get_phrases')
    def test_bind_items_from_category(self, mock_get_phrases):
        mock_get_phrases.return_value = 'test_phrase'
        d1 = Dictionary(account_guid='test_guid1', weight=2)
        d2 = Dictionary(account_guid='test_guid2', weight=5)
        self.db_util.get_dictionaries_by_phrases.return_value = [d1, d2]

        r = Receipt()
        item = Item()
        r.items = [item]
        result = _bind_items_to_categories(self.db_util, r)

        self.db_util.get_dictionaries_by_phrases.assert_called_once_with(
            'test_phrase')
        self.assertEqual(d1.account_guid, 'test_guid1')
        self.assertEqual(d1.weight, 3)
        self.assertEqual(d2.account_guid, 'test_guid2')
        self.assertEqual(d2.weight, 5)
        self.assertEqual(item.account_guid, 'test_guid1')
        self.assertListEqual(result, [])

    @mock.patch('qif_transaction_generator.enriching._get_phrases')
    def test_bind_items_with_binded_item_yet(self, mock_get_phrases):
        r = Receipt()
        item = Item(account_guid='test_account_guid')
        r.items = [item]
        result = _bind_items_to_categories(self.db_util, r)

        self.db_util.get_dictionaries_by_phrases.assert_not_called()
        mock_get_phrases.assert_not_called()
        self.assertEqual(item.account_guid, 'test_account_guid')
        self.assertListEqual(result, [])

    @mock.patch('qif_transaction_generator.enriching._get_phrases')
    def test_bind_items_with_undefined_(self, mock_get_phrases):
        mock_get_phrases.return_value = 'test_phrase'
        d1 = Dictionary(account_guid='test_guid1', weight=2)
        d2 = Dictionary(account_guid='test_guid2', weight=5)
        self.db_util.get_dictionaries_by_phrases.side_effect = [[d1, d2], []]

        r = Receipt()
        item1 = Item(name='item with exist phrase')
        item2 = Item(name='item wasn\'t existed')
        r.items = [item1, item2]
        result = _bind_items_to_categories(self.db_util, r)

        self.assertEqual(d1.account_guid, 'test_guid1')
        self.assertEqual(d1.weight, 3)
        self.assertEqual(d2.account_guid, 'test_guid2')
        self.assertEqual(d2.weight, 5)
        self.assertEqual(item1.account_guid, 'test_guid1')
        self.assertListEqual(result, [item2])

    @mock.patch('qif_transaction_generator.enriching._get_phrases')
    def test_bind_free_items(self, mock_get_phrases):
        mock_get_phrases.return_value = 'test_phrase'
        d1 = Dictionary(account_guid='test_guid1', weight=2)
        d2 = Dictionary(account_guid='test_guid2', weight=5)
        self.db_util.get_dictionaries_by_phrases.side_effect = [[d1, d2], []]

        r = Receipt()
        item1 = Item(name='item with exist phrase')
        item2 = Item(name='item wasn\'t existed')
        item2.price = 0
        r.items = [item1, item2]
        result = _bind_items_to_categories(self.db_util, r)

        self.assertListEqual(result, [])


class TestGePhrases(unittest.TestCase):

    def test_get_phrases(self):
        result = _get_phrases('test')
        self.assertEqual(result, ['test'])

        result = _get_phrases('TeSt 2')
        self.assertEqual(result, ['test 2', 'test'])

        result = _get_phrases('The third tesT')
        self.assertEqual(result, ['the third test', 'the third', 'the'])

        result = _get_phrases('Very long long string')
        self.assertEqual(result, ['very long long string',
                                  'very long long',
                                  'very long',
                                  'very'])

        result = _get_phrases('сыр раненбургъ качокавалло 45% 300г')
        self.assertEqual(result, ['сыр раненбургъ качокавалло 45% 300г',
                                  'сыр раненбургъ качокавалло',
                                  'сыр раненбургъ',
                                  'сыр'])
