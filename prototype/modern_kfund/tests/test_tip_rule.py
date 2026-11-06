"""Boundary and review checks for the illustrative tip comparison."""
import unittest
import server

class TipRuleTests(unittest.TestCase):
    def check(self, **values):
        return server.tip_check(server.TipCheckRequest(**values))

    def test_exact_boundary_and_unrounded_excess(self):
        self.assertEqual(self.check(subtotal='100', charge_amount='20', charge_kind='tip')['status'], 'within_limit')
        self.assertEqual(self.check(subtotal='999.99', charge_amount='200', charge_kind='tip')['status'], 'over_limit')

    def test_service_charge_requires_confirmation(self):
        result = self.check(subtotal='100', charge_amount='12.50', charge_kind='service_charge')
        self.assertEqual(result['status'], 'within_limit')
        self.assertTrue(result['requires_confirmation'])
        self.assertTrue(any('service charge' in w.lower() for w in result['warnings']))

    def test_missing_or_conflicting_information_needs_review(self):
        self.assertEqual(self.check(subtotal='0', charge_amount='1', charge_kind='tip')['status'], 'needs_review')
        self.assertEqual(self.check(subtotal='100', charge_amount='20', charge_kind='unknown')['status'], 'needs_review')
        self.assertEqual(self.check(subtotal='100', charge_amount='20', charge_kind='tip', printed_percent='10')['status'], 'needs_review')

if __name__ == '__main__':
    unittest.main()
