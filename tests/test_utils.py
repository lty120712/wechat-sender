# -*- coding: utf-8 -*-
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import normalize_time, match_day_condition, validate_day_condition


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


class TestMatchDayCondition(unittest.TestCase):

    def test_empty_returns_true(self):
        self.assertTrue(match_day_condition(""))

    def test_star_returns_true(self):
        self.assertTrue(match_day_condition("*"))

    def test_today(self):
        from datetime import datetime
        self.assertTrue(match_day_condition(str(datetime.now().weekday() + 1)))

    def test_not_today_returns_false(self):
        from datetime import datetime
        other = str((datetime.now().weekday() + 1) % 7 + 1)
        self.assertFalse(match_day_condition(other))

    def test_out_of_range_returns_false(self):
        self.assertFalse(match_day_condition("99"))

    def test_comma_list_includes_today(self):
        from datetime import datetime
        t = datetime.now().weekday() + 1
        self.assertTrue(match_day_condition(f"1,3,{t}"))

    def test_comma_list_excludes_today(self):
        from datetime import datetime
        today = datetime.now().weekday() + 1
        others = [d for d in range(1, 8) if d != today][:3]
        self.assertFalse(match_day_condition(",".join(str(d) for d in others)))

    def test_validate_empty_ok(self):
        self.assertEqual(validate_day_condition(""), "")
        self.assertEqual(validate_day_condition(None), "")

    def test_validate_star_ok(self):
        self.assertEqual(validate_day_condition("*"), "*")

    def test_validate_single_ok(self):
        self.assertEqual(validate_day_condition("3"), "3")

    def test_validate_comma_ok(self):
        self.assertEqual(validate_day_condition("6,7"), "6,7")

    def test_validate_comma_sorts(self):
        self.assertEqual(validate_day_condition("7,3,5"), "3,5,7")

    def test_validate_bad_char(self):
        with self.assertRaises(ValueError):
            validate_day_condition("abc")

    def test_validate_out_of_range(self):
        with self.assertRaises(ValueError):
            validate_day_condition("8")

    def test_validate_zero(self):
        with self.assertRaises(ValueError):
            validate_day_condition("0")


if __name__ == "__main__":
    unittest.main()
