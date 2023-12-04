import unittest
from app.view.view import format_bytes


class TestView(unittest.TestCase):

    # Tests for view.format_bytes
    def test_format_bytes_for_view_bytes(self):
        self.assertEqual(format_bytes(500), "500 B")

    def test_format_bytes_for_view_kilobytes(self):
        self.assertEqual(format_bytes(1500), "1.46 KB")

    def test_format_bytes_for_view_megabytes(self):
        self.assertEqual(format_bytes(3 * 1024 * 1024), "3.0 MB")

    def test_format_bytes_for_view_zero_bytes(self):
        self.assertEqual(format_bytes(0), "0 B")

    def test_format_bytes_for_view_negative_bytes(self):
        with self.assertRaises(ValueError):
            format_bytes(-100)
