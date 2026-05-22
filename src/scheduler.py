# -*- coding: utf-8 -*-
"""调度器：注册并运行间隔 / 定时 / 到点任务。"""
import logging
import time

import schedule

from src.config import AppConfig
from src.loader import MessagePicker, TimedMessageItem, HolidayMessageItem
from src.utils import match_day_condition
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
        message = self.picker.pick()
        if message is None:
            return
        self.wechat.send_message(message.body, self.config.char_delay, self.config.action_delay)

    def _job_timed(self, item: TimedMessageItem):
        def _do():
            if not item.enabled:
                return
            if not match_day_condition(item.day_condition):
                return
            self.wechat.send_message(item.body, self.config.char_delay, self.config.action_delay)
        return _do

    def _job_holiday(self, item: HolidayMessageItem):
        def _do():
            if not item.enabled:
                return
            from datetime import datetime
            if datetime.now().strftime("%m-%d") != item.month_day:
                return
            self.wechat.send_message(item.body, self.config.char_delay, self.config.action_delay)
            self.log.info(f"节日消息 [{item.name}] 已发送")
        return _do

    # ── 启动 ──

    def setup(self) -> None:
        """根据配置注册所有任务。"""
        schedule.clear()
        mode = self.config.mode.lower()

        if mode == "interval":
            schedule.every(self.config.interval).seconds.do(self._job_interval)
            self.log.info(f"间隔模式：每 {self.config.interval} 秒发送一次")
        else:
            raise ValueError(f"未知的调度模式：{mode}")

        for tm in self.config.timed_messages:
            schedule.every().day.at(tm.time).do(self._job_timed(tm))
            label = f"[{tm.title}] " if tm.title else ""
            flag = "" if tm.enabled else " [已禁用]"
            self.log.info(f"到点发送：每天 {tm.time} {label}{tm.body[:30]}{flag}")

        for hm in self.config.holiday_messages:
            schedule.every().day.at(hm.time).do(self._job_holiday(hm))
            flag = "" if hm.enabled else " [已禁用]"
            self.log.info(f"节日消息：{hm.name}（{hm.month_day} {hm.time}）{flag}")

    def run(self) -> None:
        """进入主循环。"""
        self.setup()
        self.log.info("=" * 55)

        # 启动后立即发送一次
        self._job_interval()

        while True:
            schedule.run_pending()
            time.sleep(1)
