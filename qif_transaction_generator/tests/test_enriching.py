import unittest
import unittest.mock as mock

from qif_transaction_generator.enriching import enrich_receipt_items_from_json
from qif_transaction_generator.models import Item, Receipt


@mock.patch('qif_transaction_generator.enriching.from_string_to_json')
@mock.patch('qif_transaction_generator.enriching.parse_receipt')
class TestEnrichingItemsFromJson(unittest.TestCase):
    def test_items_empty(self, mock_parse_receipt, mock_from_string_to_json):
        r = Receipt()
        r.items = [Item()]

        self.assertRaises(AssertionError, enrich_receipt_items_from_json, r)

    def test_right_case(self, mock_parse_receipt, mock_from_string_to_json):
        test_receipt = Receipt()
        test_receipt.ecash_total_sum = 2
        test_receipt.cash_total_sum = 30
        test_receipt.items = [
            Item(name='item_name', price=13, quantity=10, sum=130)
        ]
        mock_parse_receipt.return_value = test_receipt
        r = Receipt()
        r.raw = 'test_raw'

        enrich_receipt_items_from_json(r)

        mock_from_string_to_json.assert_called_once_with('test_raw')
        self.assertEqual(r.ecash_total_sum, 2)
        self.assertEqual(r.cash_total_sum, 30)
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

        enrich_receipt_items_from_json(r)

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

        enrich_receipt_items_from_json(r)

        mock_from_string_to_json.assert_called_once_with('test_raw')
        mock_parse_receipt.assert_called_once_with('test_json')
        self.assertIsNone(r.ecash_total_sum)
        self.assertIsNone(r.cash_total_sum)
        self.assertTrue(
            r.items is None or isinstance(r.items, list) and len(r.items) == 0)
