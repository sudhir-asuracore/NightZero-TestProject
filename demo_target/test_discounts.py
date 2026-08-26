import unittest
from demo_target.discounts import apply_discount


class ApplyDiscountTest(unittest.TestCase):
    def test_applies_twenty_percent_discount(self) -> None:
        self.assertEqual(800, apply_discount(1000, 20.0))

    def test_zero_discount(self) -> None:
        self.assertEqual(1234, apply_discount(1234, 0.0))

    def test_full_discount(self) -> None:
        self.assertEqual(0, apply_discount(5000, 100.0))


if __name__ == '__main__':
    unittest.main()
