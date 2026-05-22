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
            m = cfg.messages[0]
            label = f"[{m.title}] " if m.title else ""
            cond = f" ({m.day_condition})" if m.day_condition else ""
            flag = "" if m.enabled else " [已禁用]"
            self.log.info(f"   消息：{label}{m.body[:50]}{cond}{flag}")
        else:
            enabled = sum(1 for m in cfg.messages if m.enabled)
            self.log.info(f"   消息：{enabled}/{len(cfg.messages)} 条启用 ({cfg.message_mode})")
            for i, m in enumerate(cfg.messages, 1):
                preview = m.body.replace("\n", " / ")
                label = f"[{m.title}] " if m.title else ""
                cond = f" ({m.day_condition})" if m.day_condition else ""
                flag = "" if m.enabled else " [已禁用]"
                self.log.info(f"      [{i}] {label}{preview[:50]}{cond}{flag}")

        self.log.info(f"   模式：{cfg.mode}")

        if cfg.timed_messages:
            self.log.info(f"   到点消息：{len(cfg.timed_messages)} 条")
            for tm in cfg.timed_messages:
                label = f"[{tm.title}] " if tm.title else ""
                self.log.info(f"      {tm.time} -> {label}{tm.body[:30]}")

        if cfg.holiday_messages:
            self.log.info(f"   节日消息：{len(cfg.holiday_messages)} 条")
            for hm in cfg.holiday_messages:
                flag = "" if hm.enabled else " [已禁用]"
                self.log.info(f"      {hm.name}（{hm.month_day} {hm.time}）{flag}")

        self.log.info("=" * 55)
