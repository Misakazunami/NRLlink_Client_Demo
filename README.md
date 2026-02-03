# NRLLink客户端Demo

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=for-the-badge&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/Misakazunami/NRLlink_Client_Demo)

基于nrllink开源项目开发的Python客户端，实现业余无线电网络互联功能。

基于项目链接：[hicaoc/nrllink: A radio over network forward server , 通过网络转发无线电信号的程序，支持调度分组](https://github.com/hicaoc/nrllink)

注意：
- 本项目目前仍处于测试阶段，仅为学习和研究目的，不建议在生产环境中使用。
- 目前只在windows10/11平台测试通过，其他平台不保证可以正常运行。
- 如果连接到任何业余无线电有关服务器，请确保你有合法的 Amateur Radio License（业余无线电执照）和一个有效的 Callsign（呼号）。
- 本项目基于MIT协议开源，你可以在遵守协议的前提下自由使用、修改和分发本项目的代码。
- 本项目尚在测试阶段，暂不提供任何形式的技术支持，也不承担任何因使用本项目而导致的损失或损害。

## 功能特性

**基本功能**

- 设备上线注册
- 心跳维持连接
- 配置管理

**语音通信**

- G.711 A-law语音编解码
- 实时语音传输
- PTT按键说话功能
- 音频设备管理

**消息功能**

- 文本消息发送/接收（UTF-8，最大1412字节）
- 消息日志记录

**用户界面**

- 图形化界面（GUI模式）
- 命令行界面（CLI模式）
- 实时状态显示

## 项目结构

```
nrl_client_demo/
├── main.py              # 主程序入口
├── nrl_client.py        # NRL客户端核心类
├── nrl_protocol.py      # NRL协议处理模块
├── audio_handler.py     # 音频处理模块
├── gui_client.py        # 图形化界面
├── config.yaml          # 配置文件
├── requirements.txt     # Python依赖
└── README.md           # 说明文档
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

在依赖安装过程中，出现无法编译/安装pyaudio依赖是常见的，遇到此类问题请参阅以下文章：

[3步解决PyAudio安装失败问题_pyaudio wheel-CSDN博客](https://blog.csdn.net/weixin_43682905/article/details/148874411)

### 运行程序
在绝大多数情况下，用户可以直接运行 `main.py` 来启动图形化界面。
如果用户需要在命令行模式下运行程序，或者进行音频设备测试，需要添加相应的参数。
建议在运行程序前，先检查并配置好 `config.yaml` 文件中的服务器地址、端口、呼号、CPUID等参数。

```bash
# GUI模式 （默认）
python main.py

# 命令行模式 （可选）
python main.py --no-gui

# 音频设备测试 （可选）
python main.py --test-audio
```

## 配置说明

编辑 `config.yaml` 文件：

**注意**：
- 配置文件 `config.yaml` 中的参数需要根据实际情况进行修改。
- 服务器地址、端口、呼号、CPUID等参数需要与服务器端配置保持一致。
- 密码参数如果为空字符串，则表示不使用密码认证。
- 建议在修改配置文件后，重新启动程序生效。

```yaml
server:
  host: "127.0.0.1"  # 服务器地址
  port: 60050        # 服务器UDP端口

device:
  callsign: "TEST01"  # 设备呼号
  ssid: 1            # 设备SSID
  cpuid: "12345678"  # 设备CPUID
  password: "000000" # 设备密码
  model: 1           # 设备型号

audio:
  sample_rate: 8000  # 采样率
  channels: 1        # 声道数
  chunk_size: 1024   # 音频块大小

network:
  buffer_size: 1460        # 网络缓冲区大小
  heartbeat_interval: 30   # 心跳间隔（秒）
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

- NRLProtocol：协议编解码
- NRLClient：客户端核心功能
- AudioHandler：音频设备管理

**扩展开发**

1. 在 `nrl_protocol.py` 中添加新消息类型
2. 在 `audio_handler.py` 中自定义音频处理
3. 在 `gui_client.py` 中定制界面

## 故障排查

**连接失败**

- 检查服务器地址和端口配置
- 确认网络连接正常
- 检查防火墙设置（开放UDP 60050端口）

**音频问题**

- 运行音频设备测试
- 检查系统音频设置
- 确认音频设备权限

**语音传输问题**

- 检查G.711编解码是否正常
- 确认网络延迟和丢包率
- 查看日志获取详细信息

## 注意事项

1. 确保系统有可用的麦克风和扬声器
2. 防火墙需要开放UDP端口60050
3. 某些系统可能需要管理员权限访问音频设备
4. 需要与您需要连接的nrllink服务器版本兼容

## 联系方式

如有问题或建议，请发送邮件至：misakazunami@qq.com。

## 开源协议

本项目基于MIT协议，详情参照LICENSE文件描述。


