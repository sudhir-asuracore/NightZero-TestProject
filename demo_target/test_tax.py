import unittest
from demo_target.tax import calculate_tax_and_fees


class CalculateTaxTest(unittest.TestCase):
    def test_calculates_standard_eight_percent_tax(self) -> None:
        # 00.00 at 825 bps (8.25%) = .25 (825 cents)
        self.assertEqual(825, calculate_tax_and_fees(10000, 825))

    def test_calculates_zero_tax(self) -> None:
        self.assertEqual(0, calculate_tax_and_fees(5000, 0))


if __name__ == '__main__':
    unittest.main()
