# NRLlink客户端Demo

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=for-the-badge&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/Misakazunami/NRLlink_Client_Demo)

基于nrllink开源项目开发的Python客户端，实现业余无线电网络互联功能。

基于项目链接：[hicaoc/nrllink: A radio over network forward server , 通过网络转发无线电信号的程序，支持调度分组](https://github.com/hicaoc/nrllink)

> **当前版本：Beta V1.4.2**

注意：
- 本项目目前仍处于测试阶段，仅为学习和研究目的，不建议在生产环境中使用。
- 目前只在Windows 10/11平台测试通过，其他平台不保证可以正常运行。
- 如果连接到任何业余无线电有关服务器，请确保你有合法的 Amateur Radio License（业余无线电执照）和一个有效的 Callsign（呼号）。
- 本项目基于MIT协议开源，你可以在遵守协议的前提下自由使用、修改和分发本项目的代码。
- 本项目尚在测试阶段，暂不提供任何形式的技术支持，也不承担任何因使用本项目而导致的损失或损害。

## 功能特性

**基本功能**

- 设备上线注册
- 心跳维持连接
- 配置管理
- 多服务器支持（服务器列表动态切换）

**语音通信**

- G.711 A-law语音编解码
- 实时语音传输
- PTT按键说话功能
- 音频设备管理（输入/输出设备选择）

**消息功能**

- 文本消息发送/接收（UTF-8，最大1412字节）
- 消息日志记录

**用户界面**

- CustomTkinter现代化GUI（默认，支持深色/浅色主题）
- Tkinter传统GUI（兼容备选）
- 命令行界面（CLI模式）
- 实时状态显示

## 项目结构

```
NRLlink_Client_Demo-1.4.2/
├── main.py                  # 主程序入口
├── launcher.py              # GUI启动器（可选tk/ctk）
├── nrl_client.py            # NRL客户端核心类
├── nrl_protocol.py          # NRL协议处理模块
├── audio_handler.py         # 音频处理模块
├── gui_client_ctk.py        # CustomTkinter图形化界面（默认）
├── gui_client.py            # Tkinter图形化界面（备选）
├── diagnose.py              # 诊断脚本
├── config.yaml              # 配置文件
├── requirements.txt         # Python依赖
├── .gitignore               # Git忽略规则
└── README.md                # 说明文档
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

依赖列表：
- `pyaudio` — 音频采集与播放
- `pyyaml` — 配置文件解析
- `numpy` — 数据处理
- `customtkinter` — 现代化GUI框架

> 在依赖安装过程中，出现无法编译/安装PyAudio依赖是常见问题，遇到此类问题请参阅：
> [3步解决PyAudio安装失败问题_pyaudio wheel-CSDN博客](https://blog.csdn.net/weixin_43682905/article/details/148874411)

### 运行程序

建议在运行程序前，先检查并配置好 `config.yaml` 文件中的服务器地址、端口、呼号、CPUID等参数。

```bash
# GUI模式（默认使用CustomTkinter现代化界面）
python main.py

# 使用传统Tkinter界面
python main.py --gui tk

# 命令行模式
python main.py --no-gui

# 音频设备测试
python main.py --test-audio

# 列出音频设备
python main.py --list-audio

# 调试模式
python main.py --debug

# 使用启动器选择GUI
python launcher.py --gui ctk
python launcher.py --gui tk
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--config`, `-c` | 指定配置文件路径（默认: config.yaml） |
| `--gui ctk\|tk` | 选择GUI框架（默认: ctk） |
| `--no-gui` | 无GUI模式，使用命令行界面 |
| `--debug` | 启用调试模式 |
| `--test-audio` | 测试音频设备并退出 |
| `--list-audio` | 列出音频设备并退出 |
| `--enable-cpuid-calc` | 启用CPUID计算（默认关闭，直接使用配置文件中的CPUID） |

## 配置说明

编辑 `config.yaml` 文件：

**注意**：
- 配置文件中的参数需要根据实际情况进行修改。
- 服务器地址、端口、呼号、CPUID等参数需要与服务器端配置保持一致。
- 密码参数如果为空字符串，则表示不使用密码认证。
- 建议在修改配置文件后，重新启动程序生效。

```yaml
# 服务器列表（支持多服务器配置，GUI中可动态切换）
servers:
  - name: "示例服务器1"
    host: "example1.com"
    port: 60050
    password: ""           # 服务器连接密码（可选）
  - name: "示例服务器2"
    host: "example2.com"
    port: 60050
    password: ""
  - name: "本地测试服务器"
    host: "127.0.0.1"
    port: 60050
    password: ""

# 当前使用的服务器索引（默认使用第一个）
current_server: 0

# 服务器配置（向后兼容单服务器模式）
server:
  host: "example1.com"  # 服务器地址
  port: 60050           # 服务器UDP端口

device:
  callsign: "TEST01"    # 设备呼号
  ssid: 1               # 设备SSID
  cpuid: "12345678"     # 设备CPUID
  password: ""          # 设备密码
  model: 1              # 设备型号

audio:
  sample_rate: 8000     # 采样率
  channels: 1           # 声道数
  chunk_size: 500       # 音频块大小（500字节G.711包）
  format: "paInt16"     # 音频格式

network:
  buffer_size: 4096     # 网络缓冲区大小
  heartbeat_interval: 2 # 心跳间隔（秒）
```

## API使用

```python
# 初始化客户端
client = NRLClient(config_file='config.yaml')

# 连接服务器
client.connect()

# 发送文本消息
client.send_text_message("Hello, World!")

# 启动语音传输
client.start_voice_transmission()

# 停止语音传输
client.stop_voice_transmission()

# 断开连接
client.disconnect()
```

## 开发说明

**核心模块**

- `NRLProtocol`：协议编解码
- `NRLClient`：客户端核心功能
- `AudioHandler`：音频设备管理

**扩展开发**

1. 在 `nrl_protocol.py` 中添加新消息类型
2. 在 `audio_handler.py` 中自定义音频处理
3. 在 `gui_client_ctk.py` 中定制现代化界面
4. 在 `gui_client.py` 中定制传统界面

## 故障排查

**连接失败**

- 检查服务器地址和端口配置
- 确认网络连接正常
- 检查防火墙设置（开放UDP 60050端口）

**音频问题**

- 运行 `python main.py --test-audio` 测试音频设备
- 运行 `python main.py --list-audio` 列出可用设备
- 检查系统音频设置
- 确认音频设备权限

**语音传输问题**

- 检查G.711编解码是否正常
- 确认网络延迟和丢包率
- 查看日志获取详细信息（`nrl_client.log`）

**界面问题**

- 如CustomTkinter无法启动，可切换到传统Tkinter：`python main.py --gui tk`
- 运行 `python diagnose.py` 进行诊断
- 运行 `python test_customtkinter.py` 验证CustomTkinter环境

## 注意事项

1. 确保系统有可用的麦克风和扬声器
2. 防火墙需要开放UDP端口60050
3. 某些系统可能需要管理员权限访问音频设备
4. 需要与您需要连接的nrllink服务器版本兼容
5. 多服务器配置下，可通过GUI动态切换服务器

## 联系方式

如有问题或建议，请发送邮件至：misakazunami@qq.com。

## 开源协议

本项目基于MIT协议，详情参照LICENSE文件描述。