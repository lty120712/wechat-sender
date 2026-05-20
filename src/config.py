# -*- coding: utf-8 -*-
"""配置读取与数据结构。"""
import configparser
import os
from dataclasses import dataclass
from typing import List, Tuple

from src.loader import load_messages
from src.utils import normalize_time


@dataclass
class AppConfig:
    """程序运行配置，由 load_config() 从 config.ini 加载后填充。"""

    # 微信窗口
    friend_name: str
    window_class: str

    # 消息库
    messages: List[str]
    message_mode: str
    message_source: str

    # 循环调度
    mode: str
    interval: int
    daily_time: str

    # 到点消息
    timed_messages: List[Tuple[str, str]]

    # 高级
    char_delay: float
    action_delay: float
    log_level: str


def load_config(config_path: str = "config.ini") -> AppConfig:
    """加载配置文件，返回 AppConfig。"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在：{config_path}")

    parser = configparser.ConfigParser(delimiters=("=",))
    parser.read(config_path, encoding="utf-8-sig")

    base_dir = os.path.dirname(os.path.abspath(config_path))

    # [wechat]
    friend_name = parser.get("wechat", "friend_name")
    window_class = parser.get("wechat", "window_class", fallback="")

    # [message]
    raw_content = parser.get("message", "content", fallback="").strip()
    message_source = parser.get("message", "source", fallback="").strip()
    messages: List[str] = load_messages(raw_content, message_source, base_dir)
    message_mode = parser.get("message", "message_mode", fallback="sequential").strip().lower()

    # [schedule]
    mode = parser.get("schedule", "mode", fallback="interval")
    interval = parser.getint("schedule", "interval_seconds", fallback=3)
    daily_time = parser.get("schedule", "daily_time", fallback="08:00")

    # [timed_messages]
    timed_messages: List[Tuple[str, str]] = []
    if parser.has_section("timed_messages"):
        for send_time, message in parser.items("timed_messages"):
            normalized = normalize_time(send_time)
            msg = message.strip()
            if normalized and msg:
                timed_messages.append((normalized, msg))

    # [advanced]
    char_delay = parser.getfloat("advanced", "char_delay", fallback=0.01)
    action_delay = parser.getfloat("advanced", "action_delay", fallback=0.1)
    log_level = parser.get("advanced", "log_level", fallback="INFO")

    return AppConfig(
        friend_name=friend_name,
        window_class=window_class,
        messages=messages,
        message_mode=message_mode,
        message_source=message_source,
        mode=mode,
        interval=interval,
        daily_time=daily_time,
        timed_messages=timed_messages,
        char_delay=char_delay,
        action_delay=action_delay,
        log_level=log_level,
    )
