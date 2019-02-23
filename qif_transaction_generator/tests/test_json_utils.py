import unittest
import unittest.mock as mock

from qif_transaction_generator.json_utils import from_string_to_json, \
    parse_receipt
from qif_transaction_generator.models import Receipt, Item


class TestJsonUtils(unittest.TestCase):

    def test_from_string_to_json_empty_raw(self):
        self.assertRaises(AssertionError, from_string_to_json, '')

    @mock.patch('qif_transaction_generator.json_utils.j.loads')
    def test_from_string_to_json_replacing(self, mock_j_loads):
        from_string_to_json('"te\'st"')

        mock_j_loads.assert_called_once_with('\\"te"st\\"')

    def test_from_string_to_json(self):
        test_string = "{'test_attribute':'test_value'}"
        result = from_string_to_json(test_string)

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 1)
        self.assertEqual(result['test_attribute'], 'test_value')

    def test_parse_receipt_empty_items(self):
        r = Receipt()
        r.items = [Item()]

        self.assertRaises(AssertionError, parse_receipt, None)

    def test_parse_receipt_empty_json(self):
        self.assertRaises(AssertionError, parse_receipt, '')
