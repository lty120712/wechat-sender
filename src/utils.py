# -*- coding: utf-8 -*-
"""工具函数：日志初始化 + 时间格式处理。"""
import logging
import re


# ── 日志 ──

def setup_logger(level: str = "INFO") -> logging.Logger:
    """初始化全局日志（控制台 + log.txt）。"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("log.txt", encoding="utf-8", mode="a"),
        ],
    )
    return logging.getLogger("wechat_sender")


# ── 时间 ──

def normalize_time(value: str) -> str:
    """规范化到点消息的时间格式。

    支持输入：
      14:00  14-00  14.00  14_00  14 00  14：00  14:00:05

    返回：
      "14:00" 或 "14:00:05"

    异常：
      ValueError 格式无法解析或值超出范围。
    """
    text = str(value).strip().replace("\uff1a", ":")
    match = re.match(
        r"^(\d{1,2})\s*[:._\s-]\s*(\d{1,2})(?:\s*[:._\s-]\s*(\d{1,2}))?$",
        text,
    )
    if not match:
        raise ValueError(
            f"到点发送时间格式错误：{value}，请使用 HH:MM，例如 14:00"
        )

    hour = int(match.group(1))
    minute = int(match.group(2))
    second = int(match.group(3) or 0)

    if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
        raise ValueError(f"到点发送时间超出范围：{value}")

    if match.group(3) is not None:
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    return f"{hour:02d}:{minute:02d}"
