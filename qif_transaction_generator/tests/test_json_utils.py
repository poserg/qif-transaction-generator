import unittest
import unittest.mock as mock

from qif_transaction_generator.json_utils import from_string_to_json, \
    parse_receipt
from qif_transaction_generator.models import Receipt, Item


class TestJsonUtilsFromStringToJson(unittest.TestCase):
    def test_empty_raw(self):
        self.assertRaises(AssertionError, from_string_to_json, '')

    # @mock.patch('qif_transaction_generator.json_utils.j.loads')
    # def test_replacing(self, mock_j_loads):
    #     from_string_to_json('"te\'st"')

    #     mock_j_loads.assert_called_once_with('\\"te"st\\"')

    def test_right_case(self):
        test_string = "{\"test_attribute\":\"test_value\"}"
        result = from_string_to_json(test_string)

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 1)
        self.assertEqual(result['test_attribute'], 'test_value')


class TestJsonUtilsParseReceipt(unittest.TestCase):

    def test_empty_items(self):
        r = Receipt()
        r.items = [Item()]

        self.assertRaises(AssertionError, parse_receipt, None)

    def test_empty_json(self):
        self.assertRaises(AssertionError, parse_receipt, '')

    def test_key_error_documnent(self):
        s = {'test': 1}
        self.assertRaises(KeyError, parse_receipt, s)

    def test_type_error(self):
        s = {'document': 1}
        self.assertRaises(Exception, parse_receipt, s)

    def test_key_error_empty_receipt(self):
        s = {'document': {'receipt': {}}}
        self.assertRaises(KeyError, parse_receipt, s)

    def test_receipt_with_one_item(self):
        s = {
            'document': {
                'receipt': {
                    'ecashTotalSum':
                    1211,
                    'cashTotalSum':
                    33,
                    'items': [{
                        'name': 'item_name',
                        'price': 2,
                        'quantity': 31,
                        'sum': 62
                    }]
                }
            }
        }
        r = parse_receipt(s)

        self.assertEqual(r.ecash_total_sum, 1211)
        self.assertEqual(r.cash_total_sum, 33)
        self.assertEqual(len(r.items), 1)
        self.assertEqual(r.items[0].name, 'item_name')
        self.assertEqual(r.items[0].price, 2)
        self.assertEqual(r.items[0].quantity, 31)
        self.assertEqual(r.items[0].sum, 62)

    def test_parse_receipt_with_two_items(self):
        s = {
            'document': {
                'receipt': {
                    'ecashTotalSum':
                    1211,
                    'cashTotalSum':
                    33,
                    'items': [{
                        'name': 'item_name_1',
                        'price': 2,
                        'quantity': 31,
                        'sum': 62
                    }, {
                        'name': 'item_name_2',
                        'price': 1,
                        'quantity': 33,
                        'sum': 34
                    }]
                }
            }
        }
        r = parse_receipt(s)

        self.assertEqual(r.ecash_total_sum, 1211)
        self.assertEqual(r.cash_total_sum, 33)
        self.assertEqual(len(r.items), 2)
        self.assertEqual(r.items[0].name, 'item_name_1')
        self.assertEqual(r.items[0].price, 2)
        self.assertEqual(r.items[0].quantity, 31)
        self.assertEqual(r.items[0].sum, 62)
        self.assertEqual(r.items[1].name, 'item_name_2')
        self.assertEqual(r.items[1].price, 1)
        self.assertEqual(r.items[1].quantity, 33)
        self.assertEqual(r.items[1].sum, 34)
