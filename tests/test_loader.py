# -*- coding: utf-8 -*-
"""消息库加载与选取测试。"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.loader import load_messages, MessagePicker


class TestLoadMessages(unittest.TestCase):

    def _write_tmp(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
        f.write(content)
        f.close()
        return f.name

    def test_single_line(self):
        fname = self._write_tmp("msg1\nmsg2\nmsg3\n")
        try:
            msgs = load_messages("", fname, "")
            self.assertEqual(msgs, ["msg1", "msg2", "msg3"])
        finally:
            os.unlink(fname)

    def test_block_format(self):
        fname = self._write_tmp("---\nline1\nline2\n---\nblock2\n---\nblock3\nline4\n")
        try:
            msgs = load_messages("", fname, "")
            self.assertEqual(len(msgs), 3)
            self.assertEqual(msgs[0], "line1\nline2")
            self.assertEqual(msgs[1], "block2")
            self.assertEqual(msgs[2], "block3\nline4")
        finally:
            os.unlink(fname)

    def test_comment_lines(self):
        fname = self._write_tmp("#comment\nmsg1\n;also comment\nmsg2\n")
        try:
            msgs = load_messages("", fname, "")
            self.assertEqual(msgs, ["msg1", "msg2"])
        finally:
            os.unlink(fname)


class TestMessagePicker(unittest.TestCase):

    def test_random(self):
        msgs = ["a", "b", "c"]
        p = MessagePicker(msgs, "random")
        picked = {p.pick() for _ in range(100)}
        self.assertTrue(picked.issubset(set(msgs)))

    def test_sequential(self):
        msgs = ["a", "b", "c"]
        p = MessagePicker(msgs, "sequential")
        self.assertEqual(p.pick(), "a")
        self.assertEqual(p.pick(), "b")
        self.assertEqual(p.pick(), "c")
        self.assertEqual(p.pick(), "a")


if __name__ == "__main__":
    unittest.main()
