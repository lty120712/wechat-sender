# -*- coding: utf-8 -*-
"""配置读取测试。"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import load_config, AppConfig


class TestLoadConfig(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".ini", delete=False, encoding="utf-8"
        )
        self.tmp.write("""
[wechat]
friend_name = test_user

[message]
source = data/messages.txt
message_mode = random

[schedule]
mode = interval
interval_seconds = 5

[timed_messages]
14:00 = test_msg1
18:30 = test_msg2
""")
        self.tmp.close()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_load(self):
        cfg = load_config(self.tmp.name)
        self.assertIsInstance(cfg, AppConfig)
        self.assertEqual(cfg.friend_name, "test_user")
        self.assertEqual(cfg.interval, 5)
        self.assertEqual(len(cfg.timed_messages), 2)
        self.assertEqual(cfg.timed_messages[0], ("14:00", "test_msg1"))


if __name__ == "__main__":
    unittest.main()
