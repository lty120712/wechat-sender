# -*- coding: utf-8 -*-
"""消息库读取与选取。"""
import os
import random
from typing import List


# ── 读取 ──

def _decode(text: str) -> str:
    """解码 \n 等转义。"""
    return text.replace("\r\n", "\n").replace("\n", "\n")


def load_messages(raw_content: str, source: str, base_dir: str) -> List[str]:
    """加载循环发送的消息列表。

    优先从 source 指定的外部文本文件读取（推荐）。
    降级从 raw_content 中用 | 分隔读取（旧格式兼容）。

    messages.txt 支持的格式：
      1. 普通格式：一行一条消息。
      2. 分块格式：用 --- 分隔，每块是一条多行消息。

    Returns:
        消息字符串列表，非空。
    Raises:
        FileNotFoundError / ValueError
    """
    messages: List[str] = []

    if source:
        source_path = source if os.path.isabs(source) else os.path.join(base_dir, source)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"消息文件不存在：{source_path}")

        with open(source_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()

        has_block = any(line.strip() == "---" for line in lines)

        if has_block:
            block: List[str] = []
            for line in lines:
                stripped = line.strip()
                if stripped == "---":
                    msg = "\n".join(block).strip()
                    if msg:
                        messages.append(_decode(msg))
                    block = []
                    continue
                if stripped.startswith("#") or stripped.startswith(";"):
                    continue
                block.append(line.rstrip("\r\n"))
            msg = "\n".join(block).strip()
            if msg:
                messages.append(_decode(msg))
        else:
            for line in lines:
                msg = line.strip()
                if not msg or msg.startswith("#") or msg.startswith(";"):
                    continue
                messages.append(_decode(msg))
    else:
        messages = [_decode(m.strip()) for m in raw_content.split("|") if m.strip()]

    if not messages:
        raise ValueError(
            "循环消息为空：请在 [message] content 中填写内容，"
            "或配置 source = data/messages.txt"
        )

    return messages


# ── 选取 ──

class MessagePicker:
    """按配置从消息列表中选取下一条要发送的消息。"""

    def __init__(self, messages: List[str], mode: str = "sequential"):
        """
        Args:
            messages: 消息列表。
            mode: sequential（轮流）或 random（随机）。
        """
        if not messages:
            raise ValueError("消息列表不能为空")
        self._messages = messages
        self._mode = mode.lower()
        self._index = 0

    @property
    def count(self) -> int:
        return len(self._messages)

    def pick(self) -> str:
        """选取一条消息。"""
        if self._mode == "random":
            return random.choice(self._messages)
        msg = self._messages[self._index % len(self._messages)]
        self._index += 1
        return msg

    def reset(self) -> None:
        """重置索引。"""
        self._index = 0
