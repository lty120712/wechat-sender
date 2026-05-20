# WeChat Sender v1.0

微信定时消息发送器。向指定好友独立窗口循环定时发送自定义消息。

## 项目结构

```
wechat-sender/
├── main.py              # 程序入口
├── config.ini           # 用户配置
├── run.bat              # 启动脚本
├── setup.bat            # 首次安装脚本
├── requirements.txt     # Python 依赖
├── README.md            # 本文件
│
├── data/                # 用户数据
│   └── messages.txt     # 消息库（一行一条）
│
├── src/                 # 核心代码
│   ├── app.py           # 应用启动编排
│   ├── config/          # 配置读取
│   ├── message/         # 消息库管理
│   ├── scheduler/       # 调度器
│   ├── service/         # 发送业务编排
│   ├── transport/       # 微信窗口操作
│   └── utils/           # 工具函数
│
├── tests/               # 单元测试
│
└── venv/                # Python 虚拟环境
```

## 解压后首次运行

```bat
cd /d D:\owns\code\wechat-sender
setup.bat
```

## 运行

```bat
run.bat
```

## 配置说明 (`config.ini`)

### 微信窗口

```ini
[wechat]
friend_name = 好友昵称
window_class = Qt51514QWindowIcon
```

### 循环发送消息

```ini
[message]
source = data/messages.txt
message_mode = sequential  # 或 random
```

### 间隔模式

```ini
[schedule]
mode = interval
interval_seconds = 3
```

### 每日定时模式

```ini
[schedule]
mode = daily
daily_time = 08:00
```

### 到点发送（和循环发送不冲突）

```ini
[timed_messages]
14:00 = 下午好
18:00 = 下班啦
```

## 消息库 (`data/messages.txt`)

一行一条消息：

```
早上好！
下午好！
晚上好！
```

暂不支持多行区块（以下配置仍然会被拼接为一行）：

```
---
第一行
第二行
---
另一条消息
---
```

## 开发

### 运行测试

```bat
cd /d D:\owns\code\wechat-sender
venv\Scripts\activate
python -m unittest discover tests
```

### 添加新功能

在 `src/` 下对应的子目录中添加新模块，确保 `__init__.py` 导出即可。
