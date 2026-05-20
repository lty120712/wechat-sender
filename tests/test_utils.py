# -*- coding: utf-8 -*-
"""时间工具测试。"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import normalize_time


class TestNormalizeTime(unittest.TestCase):

    def test_standard(self):
        self.assertEqual(normalize_time("14:00"), "14:00")

    def test_dash(self):
        self.assertEqual(normalize_time("14-00"), "14:00")

    def test_dot(self):
        self.assertEqual(normalize_time("14.00"), "14:00")

    def test_fullwidth_colon(self):
        self.assertEqual(normalize_time("14：00"), "14:00")

    def test_with_seconds(self):
        self.assertEqual(normalize_time("14:00:05"), "14:00:05")

    def test_single_digit_hour(self):
        self.assertEqual(normalize_time("9:00"), "09:00")

    def test_invalid(self):
        with self.assertRaises(ValueError):
            normalize_time("abc")


if __name__ == "__main__":
    unittest.main()
