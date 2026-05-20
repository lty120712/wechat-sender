# -*- coding: utf-8 -*-
"""应用入口编排。"""
import sys
import os

_src = os.path.join(os.path.dirname(__file__), "..")
if _src not in sys.path:
    sys.path.insert(0, _src)

from src.config import load_config
from src.utils import setup_logger
from src.sender import SendService


def run(config_path: str = "config.ini") -> int:
    """程序主入口。

    1. 加载配置
    2. 初始化日志
    3. 组装各组件
    4. 等待微信窗口并启动调度循环

    Returns:
        0 正常退出，1 配置错误。
    """
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[错误] {exc}")
        return 1

    logger = setup_logger(config.log_level)
    service = SendService(config, logger)

    try:
        service.start()
    except KeyboardInterrupt:
        logger.info("程序已退出")
    except Exception as exc:
        logger.error(f"程序异常退出: {exc}")
        return 1

    return 0
