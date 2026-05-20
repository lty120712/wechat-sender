# -*- coding: utf-8 -*-
"""调度器：注册并运行间隔 / 定时 / 到点任务。"""
import logging
import time

import schedule

from src.config import AppConfig
from src.loader import MessagePicker
from src.wechat import WeChatWindow


class Scheduler:
    """消息调度器：根据配置注册并循环执行任务。"""

    def __init__(
        self,
        config: AppConfig,
        wechat: WeChatWindow,
        picker: MessagePicker,
        logger: logging.Logger,
    ):
        self.config = config
        self.wechat = wechat
        self.picker = picker
        self.log = logger

    # ── 任务定义 ──

    def _job_interval(self) -> None:
        """间隔 / 每日发送任务。"""
        message = self.picker.pick()
        self.wechat.send_message(message, self.config.char_delay, self.config.action_delay)

    def _job_timed(self, message: str):
        """到点发送任务（工厂函数）。"""
        def _do():
            self.wechat.send_message(message, self.config.char_delay, self.config.action_delay)
        return _do

    # ── 启动 ──

    def setup(self) -> None:
        """根据配置注册所有任务。"""
        schedule.clear()
        mode = self.config.mode.lower()

        if mode == "interval":
            schedule.every(self.config.interval).seconds.do(self._job_interval)
            self.log.info(f"间隔模式：每 {self.config.interval} 秒发送一次")
        elif mode == "daily":
            schedule.every().day.at(self.config.daily_time).do(self._job_interval)
            self.log.info(f"每日模式：每天 {self.config.daily_time} 发送循环消息")
        else:
            raise ValueError(f"未知的调度模式：{mode}")

        for send_time, message in self.config.timed_messages:
            schedule.every().day.at(send_time).do(self._job_timed(message))
            self.log.info(f"到点发送：每天 {send_time} 发送：{message[:30]}")

    def run(self) -> None:
        """进入主循环。"""
        self.setup()
        self.log.info("=" * 55)

        # 启动后立即发送一次
        self._job_interval()

        while True:
            schedule.run_pending()
            time.sleep(1)
