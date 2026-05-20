# -*- coding: utf-8 -*-
"""微信独立窗口查找与消息发送（v1.0 稳定策略）。

仅使用 FindWindow + PostMessage，不引入 UIA / 剪贴板 / 坐标点击。
"""
import logging
import time

import win32api
import win32con
import win32gui


class WeChatWindow:
    """微信独立聊天窗口封装。"""

    def __init__(self, friend_name: str, window_class: str, logger: logging.Logger):
        """
        Args:
            friend_name: 窗口标题（好友昵称）。
            window_class: 窗口类名（可为空字符串）。
            logger: 日志记录器。
        """
        self.friend_name = friend_name
        self.window_class = window_class
        self.log = logger

    # ── 窗口查找 ──

    def find_hwnd(self) -> int:
        """查找独立聊天窗口句柄，未找到返回 0。"""
        if self.window_class:
            hwnd = win32gui.FindWindow(self.window_class, self.friend_name)
        else:
            hwnd = win32gui.FindWindow(None, self.friend_name)
        if hwnd and win32gui.IsWindow(hwnd):
            return hwnd
        return 0

    def wait_for_popup(self, interval: float = 1.0) -> None:
        """阻塞等待独立窗口出现。"""
        if self.find_hwnd():
            self.log.info("独立窗口已就绪")
            return
        self.log.info(f"请在微信中右键 [{self.friend_name}] -> 独立窗口显示")
        self.log.info("正在等待独立窗口...")
        while not self.find_hwnd():
            time.sleep(interval)
        self.log.info("独立窗口已检测到")

    def ensure_visible(self, hwnd: int) -> None:
        """最小化时静默恢复（不抢焦点）。"""
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
            time.sleep(0.2)

    # ── 发送操作 ──

    @staticmethod
    def send_text(hwnd: int, text: str, char_delay: float = 0.01) -> None:
        """逐字符发送文本到输入框。"""
        for ch in text:
            win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(ch), 0)
            time.sleep(char_delay)

    @staticmethod
    def press_enter(hwnd: int) -> None:
        """按下并释放回车键。"""
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

    def send_message(self, message: str, char_delay: float, action_delay: float) -> bool:
        """发送一条消息到独立窗口。

        Returns:
            True 表示操作完成（不保证微信真实收到）。
        """
        hwnd = self.find_hwnd()
        if not hwnd:
            self.log.warning(f"独立窗口未打开（请右键 [{self.friend_name}] -> 独立窗口显示）")
            return False

        try:
            self.ensure_visible(hwnd)
            self.send_text(hwnd, message, char_delay)
            time.sleep(action_delay)
            self.press_enter(hwnd)
            preview = message.replace("\n", " / ")
            self.log.info(f"已发送给 [{self.friend_name}]: {preview[:60]}")
            return True
        except Exception as exc:
            self.log.error(f"发送失败: {exc}")
            return False
