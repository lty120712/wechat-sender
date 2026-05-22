# -*- coding: utf-8 -*-
import os
import sys
import tempfile
import unittest
import configparser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import load_config, AppConfig


def _make_xlsx(dirpath: str) -> str:
    import openpyxl
    path = os.path.join(dirpath, "messages.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "循环消息"
    ws.append(["消息标题", "消息体", "发送条件"])
    ws.append(["msg1", "hello", "*"])
    ws.append(["msg2", "world", "2,4"])
    ws2 = wb.create_sheet("到点消息")
    ws2.append(["时间", "消息标题", "消息体", "发送条件"])
    ws2.append(["14:00", "test", "test_msg1", "*"])
    ws2.append(["18:30", "", "test_msg2", "6,7"])
    wb.save(path)
    return path


class TestLoadConfig(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        xlsx_path = _make_xlsx(self.tmpdir)
        self.tmp_ini = os.path.join(self.tmpdir, "config.ini")
        with open(self.tmp_ini, "w", encoding="utf-8") as f:
            f.write(f"""
[wechat]
friend_name = test_user

[message]
source = {xlsx_path}
message_mode = random

[schedule]
mode = interval
interval_seconds = 5

[advanced]
char_interval = 0.1
""")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_load_basic(self):
        cfg = load_config(self.tmp_ini)
        self.assertIsInstance(cfg, AppConfig)
        self.assertEqual(cfg.friend_name, "test_user")
        self.assertEqual(cfg.interval, 5)

    def test_load_messages(self):
        cfg = load_config(self.tmp_ini)
        self.assertEqual(len(cfg.messages), 2)
        self.assertEqual(cfg.messages[0].title, "msg1")
        self.assertEqual(cfg.messages[0].body, "hello")
        self.assertEqual(cfg.messages[0].day_condition, "*")
        self.assertEqual(cfg.messages[1].title, "msg2")
        self.assertEqual(cfg.messages[1].body, "world")
        self.assertEqual(cfg.messages[1].day_condition, "2,4")

    def test_load_timed_messages(self):
        cfg = load_config(self.tmp_ini)
        self.assertEqual(len(cfg.timed_messages), 2)
        self.assertEqual(cfg.timed_messages[0].time, "14:00")
        self.assertEqual(cfg.timed_messages[0].title, "test")
        self.assertEqual(cfg.timed_messages[0].body, "test_msg1")
        self.assertEqual(cfg.timed_messages[0].day_condition, "*")
        self.assertEqual(cfg.timed_messages[1].time, "18:30")
        self.assertEqual(cfg.timed_messages[1].body, "test_msg2")
        self.assertEqual(cfg.timed_messages[1].day_condition, "6,7")

    def test_message_mode(self):
        cfg = load_config(self.tmp_ini)
        self.assertEqual(cfg.message_mode, "random")


if __name__ == "__main__":
    unittest.main()
