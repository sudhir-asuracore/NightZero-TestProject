import unittest
from demo_target.currency import convert_currency


class ConvertCurrencyTest(unittest.TestCase):
    def test_converts_usd_to_eur(self) -> None:
        # 0.00 at 0.92 rate = 920 cents
        self.assertEqual(920, convert_currency(1000, 0.92))

    def test_converts_fractional_rate(self) -> None:
        # 2.34 at 1.15 rate = 1419 cents
        self.assertEqual(1419, convert_currency(1234, 1.15))


if __name__ == '__main__':
    unittest.main()
