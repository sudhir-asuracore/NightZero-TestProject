import unittest

from demo_target.pricing import format_total


class FormatTotalTest(unittest.TestCase):
    def test_preserves_cents(self) -> None:
        self.assertEqual("$12.34", format_total(1234))


if __name__ == "__main__":
    unittest.main()