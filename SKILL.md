# WeChat Sender Development Guide

## Overview

Windows 桌面端微信定时消息发送器。通过 `pywin32` 的 `FindWindow` + `PostMessage` 操作微信 PC 独立聊天窗口，模拟键盘输入文本后回车发送。**纯桌面端，无服务端/Web 依赖。**

## Stack

- Python 3.10+
- `pywin32==306` — Windows API 查找窗口、模拟键盘
- `schedule==1.2.0` — 定时任务调度
- unittest — 测试框架

## Architecture

```
main.py                          # 入口：将 src/ 加入 sys.path 后调用 app.run()
src/
  app.py                         # 编排：加载配置 → 初始化日志 → 组装组件 → 启动
  config.py                      # 读取 config.ini → dataclass AppConfig
  loader.py                      # 读取 data/messages.txt + MessagePicker（顺序/随机选消息）
  wechat.py                      # FindWindow 找窗口 + PostMessage WM_CHAR 逐字符 + WM_KEYDOWN/UP 回车
  scheduler.py                   # 基于 schedule 库注册 interval/daily/timed_messages 任务
  sender.py                      # SendService 组装以上组件
  utils.py                       # setup_logger() + normalize_time()
tests/
  test_config.py, test_loader.py, test_utils.py
```

## Development Setup

```bat
setup.bat                        # 首次：创建 venv + pip install -r requirements.txt
run.bat                          # 运行：activate venv → python main.py
```

手动：
```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Testing

```bat
venv\Scripts\activate
python -m unittest discover tests -v
```

测试文件置于 `tests/`，每个模块对应一个 `test_<module>.py`，使用 `unittest.TestCase`。**NOT** pytest。

`tests/__init__.py` 为空文件。

## Code Conventions

### General
- 文件头 `# -*- coding: utf-8 -*-`
- **不删不写注释**（README 中已声明）
- 字符串用双引号
- EOL：`.py` / `.ini` / `.txt` / `.md` 用 LF；`.bat` 用 CRLF
- 日志用 `logger.info/warning/error`，不用 print（启动阶段的致命错误除外）

### Imports
标准库在前，第三方库在后，空行分隔：
```python
import logging
import time

import win32api
import win32con

from src.config import AppConfig
```

### Naming
- 类：`PascalCase` — `WeChatWindow`, `SendService`, `MessagePicker`, `Scheduler`
- 函数/变量：`snake_case` — `load_config`, `find_hwnd`, `char_delay`
- 私有/内部：`_` 前缀 — `_job_interval`, `_decode`, `_index`

### Config
`config.ini` 使用 `configparser` 读取，`delimiters=("=",)`。新功能添加配置项时在 `AppConfig` dataclass 中补充字段，`load_config()` 中解析，默认值保持一致。

### Messages (Excel 为主，TXT 兼容)

**Excel 文件 `data/messages.xlsx`**（主格式）：

| 工作表 | 列 |
|--------|-----|
| `循环消息` | 消息标题 \| 消息体 |
| `到点消息` | 时间 \| 消息标题 \| 消息体 |

`loader.py` 自动根据扩展名分派：
- `.xlsx` → 用 `openpyxl` 读取对应工作表
- `.txt` → 按行或 `---` 分块读取（兼容旧格式）

行首 `#` / `;` 在 txt 中为注释。

关键 dataclass：
- `MessageItem(title, body)` — 循环消息，`MessagePicker.pick()` 返回
- `TimedMessageItem(time, title, body)` — 到点消息，`config.timed_messages` 承载

## Key Patterns

### 微信窗口操作（`src/wechat.py`）
- 只依赖 `FindWindow` + `PostMessage`，**不引入** UIA / 剪贴板 / 坐标点击
- `find_hwnd()` → 返回 0 表示未找到
- `wait_for_popup()` → 阻塞轮询等待窗口出现
- `send_text()` → `PostMessage(hwnd, WM_CHAR, ord(ch), 0)`
- `press_enter()` → `PostMessage(WM_KEYDOWN + WM_KEYUP, VK_RETURN)`
- `ensure_visible()` → `ShowWindow(SW_SHOWNOACTIVATE)` 恢复不抢焦点

### 调度器（`src/scheduler.py`）
- 使用 `schedule` 库，不是 `threading.Timer` 或 `asyncio`
- `setup()` → 清空已有任务，按配置注册
- `run()` → 启动后立即发一次，然后 `while True: schedule.run_pending(); time.sleep(1)`
- `timed_messages` 通过 closure 捕获每条消息

### 消息选取（`src/loader.py`）
- `MessagePicker` 有内部 `_index`，sequential 模式下循环递增，**不是线程安全**的
- random 模式用 `random.choice()`
- `pick()` 返回 `MessageItem`，调用方取 `.body` 获取实际文本

### 消息来源（Excel）
- `load_messages(source, base_dir)` → 读取 `[循环消息]` 工作表，返回 `List[MessageItem]`
- `load_timed_messages(source, base_dir)` → 读取 `[到点消息]` 工作表，返回 `List[TimedMessageItem]`
- 仅 `.xlsx` 支持到点消息；`.txt` 的 `load_timed_messages()` 返回空列表

### Config
- `timed_messages` 已从 `config.ini` 的 `[timed_messages]` 节迁移到 Excel 的 `[到点消息]` 工作表
- `config.py` 中 `AppConfig.timed_messages` 类型变为 `List[TimedMessageItem]`

## Adding Features

### 添加新配置项
1. `AppConfig` dataclass 加字段
2. `load_config()` 中解析
3. `config.ini` 加说明

### 添加新调度任务
1. `Scheduler` 定义 `_job_*` 方法
2. `setup()` 中用 `schedule.every()....do(...)` 注册

### 添加新发送渠道
当前只支持文本。如需支持图片/文件：
- 用 `win32clipboard` + `CF_DIB` / `CF_HDROP` 设置剪贴板
- `PostMessage(hwnd, WM_PASTE)` 粘贴
- 或模拟拖拽（复杂度更高，不建议）

### 添加新模块
1. `src/<name>.py` 中编写
2. 确认 `src/__init__.py` 导出（空文件也可，用 `from src.<name> import ...`）

## Known Gotchas

- **窗口类名不稳定**：微信更新可能改 `window_class`，此时需用 `spy++` 重新抓取
- **`PostMessage` 可靠性**：WM_CHAR 不保证微信一定处理，发送后无 ACK
- **焦点问题**：如果微信窗口最小化，`ShowWindow(SW_SHOWNOACTIVATE)` 恢复但不抢焦点，发送可能失败
- **好友昵称变更**：微信昵称改了但窗口标题没及时更新，`FindWindow` 会找不到
- **`schedule` 空闲循环**：`while True + sleep(1)` 会阻塞主线程，如需并行任务需引入 `threading`

## Changelog Convention

直接用 git commit message，格式：`<type>: <简短描述>`

- `feat:` — 新功能
- `fix:` — 修 bug
- `refactor:` — 重构
- `test:` — 测试
- `docs:` — 文档
