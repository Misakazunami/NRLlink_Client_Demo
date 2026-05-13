# NRLlink客户端Demo

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=for-the-badge&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/Misakazunami/NRLlink_Client_Demo)

基于[nrllink](https://github.com/hicaoc/nrllink)开源项目开发的Python客户端，实现业余无线电网络互联功能。

### 本项目已经并入[78HAM](https://github.com/78ham)计划，作为 [78HAM-Desktop](https://github.com/78ham/78ham-Desktop)维护。
## 关于 78HAM：
78HAM是一个基于NRL协议的跨平台客户端，期望支持Android、Windows、Linux等平台
### 此仓库将会在近期归档

> **当前版本：Beta V1.4.2**

注意：
- 本项目目前仍处于测试阶段，仅为学习和研究目的，不建议在生产环境中使用。
- 目前只在Windows 10/11平台测试通过，其他平台不保证可以正常运行。
- 如果连接到任何业余无线电有关服务器，请确保你有合法的 Amateur Radio License（业余无线电执照）和一个有效的 Callsign（呼号）。
- 本项目基于MIT协议开源，你可以在遵守协议的前提下自由使用、修改和分发本项目的代码。

## 功能特性

**基本功能**

- 设备上线注册（NRL2协议，UDP 48字节头部 + 数据载荷）
- 心跳维持连接（可配置间隔）
- 多服务器支持（服务器列表配置，GUI中可动态切换）
- 自动重连机制（连续接收失败后自动重试）

**语音通信**

- G.711 A-law 语音编解码（500字节G.711帧 = 1000字节PCM = 62.5ms）
- 实时语音传输与接收
- PTT按键说话功能
- 语音播放超时自动停止（接收端无数据后自动释放播放流）
- 网络抖动缓冲（可配置缓冲深度）

**消息功能**

- 文本消息发送/接收（UTF-8编码，最大1412字节）

**位置功能**

- 多级定位：Windows Location API（GPS/基站/WiFi）→ IP 地理定位 → 配置文件默认坐标
- 手动发送位置（GUI按钮触发，定位失败时弹出手动输入对话框）
- 自动上报位置（连接后按配置间隔定时上报，可开关）
- 位置消息解析与高德地图链接生成

**用户界面**

- CustomTkinter现代化GUI（默认，暗色主题，支持深色/浅色切换）
- Tkinter传统GUI（兼容备选，无需安装customtkinter）
- 命令行界面（CLI模式）
- 实时状态显示（连接状态、包计数、设备信息）

## 项目结构

```
NRLlink_Client_Demo-1.4.2/
├── main.py                  # 主程序入口（含CLI参数解析和GUI回退逻辑）
├── launcher.py              # GUI启动器（可选 --gui tk|ctk）
├── nrl_client.py            # NRL客户端核心类（连接、收发、语音传输）
├── nrl_protocol.py          # NRL2协议编解码（NRLPacket、G711Codec）
├── audio_handler.py         # 音频处理（PyAudio录音/播放、G.711编解码、抖动缓冲）
├── gui_client_ctk.py        # CustomTkinter图形化界面（默认）
├── gui_client.py            # Tkinter图形化界面（备选）
├── diagnose.py              # 诊断脚本
├── config.yaml              # 配置文件（服务器、设备、音频、网络参数）
├── requirements.txt         # Python依赖
└── README.md                # 本文件
```

## 快速开始

### 环境要求

- Python 3.8+
- 可用的麦克风和扬声器
- UDP端口60050未被防火墙拦截

### 安装依赖

```bash
pip install -r requirements.txt
```

| 依赖 | 说明 |
|------|------|
| `pyaudio` | 音频采集与播放（底层依赖PortAudio） |
| `pyyaml` | 配置文件解析 |
| `numpy` | 音频数据处理（RMS音量计算等） |
| `customtkinter` | 现代化GUI框架（可选，未安装时自动回退到Tkinter） |
| `requests` | IP地理定位回退方案（位置消息功能） |
| `winrt-Windows-Devices-Geolocation` | Windows Location API，用于GPS定位（可选，仅Windows） |

> **PyAudio安装问题**：Windows下可能需要先安装预编译的wheel文件，请参阅：
> [3步解决PyAudio安装失败问题_pyaudio wheel-CSDN博客](https://blog.csdn.net/weixin_43682905/article/details/148874411)

### 配置

运行前请编辑 `config.yaml`：

```yaml
# 服务器列表（支持多服务器，GUI中可动态切换）
servers:
  - name: "示例服务器1"
    host: "example1.com"
    port: 60050
    password: ""
  - name: "本地测试服务器"
    host: "127.0.0.1"
    port: 60050
    password: ""

current_server: 0   # 当前使用的服务器索引

# 服务器配置（向后兼容单服务器模式）
server:
  host: "example1.com"
  port: 60050

device:
  callsign: "TEST01"    # 呼号
  ssid: 1               # SSID
  dmr_id: "1234567"     # DMRID
  password: ""          # 密码（空=不认证）
  model: 1              # 设备型号（1-99硬件，100-199软件）

audio:
  sample_rate: 8000     # 采样率（Hz）
  channels: 1           # 声道数（单声道）
  tx_codec: "g711"      # 发射编码格式（"g711" 或 "opus"，opus自动切换16kHz）
  format: "paInt16"     # 音频格式

# 位置配置
location:
  default_lat: 0.0      # 默认纬度（GPS和IP定位均不可用时使用）
  default_lng: 0.0      # 默认经度
  auto_report: false     # 是否开启连接后自动上报位置
  report_interval: 600   # 自动上报间隔（秒），auto_report 为 true 时生效

network:
  buffer_size: 4096     # 网络缓冲区大小（字节）
  heartbeat_interval: 2 # 心跳间隔（秒）
```

### 运行程序

```bash
# GUI模式（默认CustomTkinter，不可用时自动回退到Tkinter）
python main.py

# 强制使用传统Tkinter界面
python main.py --gui tk

# 命令行模式
python main.py --no-gui

# 调试模式（详细日志）
python main.py --debug

# 音频设备工具
python main.py --test-audio     # 测试音频设备
python main.py --list-audio     # 列出所有音频设备

# 使用启动器
python launcher.py --gui ctk
python launcher.py --gui tk
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--config`, `-c` | 指定配置文件路径（默认: `config.yaml`） |
| `--gui ctk\|tk` | 选择GUI框架（默认: ctk） |
| `--no-gui` | 命令行界面模式 |
| `--debug` | 启用调试模式（DEBUG级别日志） |
| `--test-audio` | 测试音频设备并退出 |
| `--list-audio` | 列出音频设备并退出 |

## 协议说明

基于NRL2协议，UDP通信，数据包结构：

| 偏移 | 长度 | 字段 | 说明 |
|------|------|------|------|
| 0-3 | 4 | Version | 协议标识 `NRL2` |
| 4-5 | 2 | Length | 数据包总长度（头部+数据，大端序） |
| 6-8 | 3 | DMRID | 设备唯一标识 |
| 9-19 | 11 | Password | 认证密码 |
| 20 | 1 | Type | 数据类型（1=语音, 2=心跳, 5=文本, 9=服务器语音） |
| 21 | 1 | Status | 状态标志（bit0=DCD/PTT） |
| 22-23 | 2 | Count | 包计数器（大端序） |
| 24-29 | 6 | Callsign | 呼号 |
| 30 | 1 | SSID | 子站号 |
| 31 | 1 | DevMode | 设备模式 |
| 32-37 | 6 | OrigCallsign | 原始呼号（服务器互联用） |
| 38 | 1 | OrigSSID | 原始SSID |
| 39-42 | 4 | OrigIP | 原始IP地址 |
| 43-47 | 5 | Reserved | 保留 |
| 48+ | N | Data | 数据载荷 |

## API使用

```python
from nrl_client import NRLClient

# 初始化并连接
client = NRLClient(config_file='config.yaml')
client.connect()

# 发送文本消息
client.send_text_message("Hello, World!")

# 发送位置消息（手动指定坐标）
client.send_location_message(31.8612, 117.2839)

# 获取位置（多级回退：GPS → IP → 默认配置）
lat, lng, source = client.resolve_location()

# 启动/停止语音传输
client.start_voice_transmission()   # PTT按下
client.stop_voice_transmission()    # PTT释放

# 关闭
client.close()
```

## 技术细节

**音频流程**

```
麦克风 -> PyAudio录音回调 -> 1000字节PCM缓冲 -> G.711编码(500字节) -> UDP发送
UDP接收 -> G.711解码(1000字节PCM) -> 抖动缓冲 -> PyAudio播放回调 -> 扬声器
```

**线程模型**

| 线程 | 职责 |
|------|------|
| 主线程 (GUI) | tkinter事件循环、用户交互 |
| 接收线程 | UDP数据包接收与分发 |
| 心跳线程 | 定期发送心跳维持连接 |
| 播放超时线程 | 检测语音播放是否需要自动停止 |
| PyAudio回调线程 | 音频录音/播放回调（PortAudio管理） |

## 作者

- 作者: BH6ERO
- 反馈: 3087040097@qq.com

## 许可证

MIT License

## 联系方式

如有问题或建议，请发送邮件至：misakazunami@qq.com。

## 开源协议

本项目基于MIT协议，详情参照LICENSE文件描述。
