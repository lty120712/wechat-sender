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


# ── 日期条件匹配 ──

def validate_day_condition(value: str) -> str:
    """校验发送条件格式，合法返回清洗后的值，非法抛出 ValueError。"""
    c = (value or "").strip()
    if not c or c == "*":
        return c
    seen = set()
    for part in c.split(","):
        p = part.strip()
        if not p:
            raise ValueError(f"发送条件 '{value}' 含空段，格式应为: * 或 1-7 或 1,3,5")
        try:
            n = int(p)
        except ValueError:
            raise ValueError(f"发送条件 '{value}' 含非法字符 '{p}'，只接受数字和逗号")
        if n < 1 or n > 7:
            raise ValueError(f"发送条件 '{value}' 中 {n} 超出范围(1-7)")
        seen.add(n)
    return ",".join(str(d) for d in sorted(seen))


def match_day_condition(condition: str) -> bool:
    if not condition:
        return True
    c = condition.strip()
    if c == "*":
        return True
    from datetime import datetime
    today = datetime.now().weekday() + 1
    if "," in c:
        days = {int(x.strip()) for x in c.split(",") if x.strip()}
        return today in days
    try:
        return int(c) == today
    except ValueError:
        return False
