import unittest
from demo_target.billing import calculate_proration


class CalculateProrationTest(unittest.TestCase):
    def test_half_month_proration(self) -> None:
        self.assertEqual(1500, calculate_proration(3000, 15, 30))

    def test_ten_days_proration(self) -> None:
        self.assertEqual(1000, calculate_proration(3000, 10, 30))


if __name__ == '__main__':
    unittest.main()
