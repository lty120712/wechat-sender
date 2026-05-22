# -*- coding: utf-8 -*-
import configparser
import os
from dataclasses import dataclass
from typing import List

from src.loader import load_messages, load_timed_messages, load_holiday_messages, MessageItem, TimedMessageItem, HolidayMessageItem


@dataclass
class AppConfig:
    friend_name: str
    window_class: str

    messages: List[MessageItem]
    message_mode: str
    message_source: str

    mode: str
    interval: int

    timed_messages: List[TimedMessageItem]
    holiday_messages: List[HolidayMessageItem]

    char_delay: float
    action_delay: float
    log_level: str


def load_config(config_path: str = "config.ini") -> AppConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在：{config_path}")

    parser = configparser.ConfigParser(delimiters=("=",))
    parser.read(config_path, encoding="utf-8-sig")

    base_dir = os.path.dirname(os.path.abspath(config_path))

    friend_name = parser.get("wechat", "friend_name")
    window_class = parser.get("wechat", "window_class", fallback="")

    message_source = parser.get("message", "source", fallback="").strip()
    messages = load_messages(message_source, base_dir)
    message_mode = parser.get("message", "message_mode", fallback="sequential").strip().lower()

    mode = parser.get("schedule", "mode", fallback="interval")
    interval = parser.getint("schedule", "interval_seconds", fallback=3)

    timed_messages = load_timed_messages(message_source, base_dir)
    holiday_messages = load_holiday_messages(message_source, base_dir)

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
        timed_messages=timed_messages,
        holiday_messages=holiday_messages,
        char_delay=char_delay,
        action_delay=action_delay,
        log_level=log_level,
    )
