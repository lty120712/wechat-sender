# -*- coding: utf-8 -*-
"""发送服务：编排完整发送流程。"""
import logging

from src.config import AppConfig
from src.loader import MessagePicker
from src.wechat import WeChatWindow
from src.scheduler import Scheduler


class SendService:
    """发送服务，组装配置、窗口、选取器、调度器并启动。"""

    def __init__(self, config: AppConfig, logger: logging.Logger):
        self.config = config
        self.log = logger
        self.wechat = WeChatWindow(config.friend_name, config.window_class, logger)
        self.picker = MessagePicker(config.messages, config.message_mode)
        self.scheduler = Scheduler(config, self.wechat, self.picker, logger)

    def start(self) -> None:
        """启动完整发送流程。"""
        self._log_startup_info()
        self.wechat.wait_for_popup()
        self.scheduler.run()

    def _log_startup_info(self) -> None:
        """输出启动配置摘要。"""
        cfg = self.config
        self.log.info("=" * 55)
        self.log.info("微信定时消息发送器 v1.0")
        self.log.info(f"   好友：{cfg.friend_name}")

        if cfg.message_source:
            self.log.info(f"   消息来源：{cfg.message_source}")

        if len(cfg.messages) == 1:
            self.log.info(f"   消息：{cfg.messages[0][:50]}")
        else:
            self.log.info(f"   消息：{len(cfg.messages)} 条 ({cfg.message_mode})")
            for i, msg in enumerate(cfg.messages, 1):
                preview = msg.replace("\n", " / ")
                self.log.info(f"      [{i}] {preview[:50]}")

        self.log.info(f"   模式：{cfg.mode}")

        if cfg.timed_messages:
            self.log.info(f"   到点消息：{len(cfg.timed_messages)} 条")
            for send_time, msg in cfg.timed_messages:
                self.log.info(f"      {send_time} -> {msg[:30]}")

        self.log.info("=" * 55)
