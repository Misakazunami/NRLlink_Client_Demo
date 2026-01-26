# NRL客户端Demo

基于nrllink项目开发的Python客户端，实现无线电网络互联功能。

## 功能特性

**基本功能**
- 设备上线注册（CPUID哈希同步）
- 心跳维持连接（SSID=200规范）
- 配置管理

**语音通信**
- G.711 A-law语音编解码
- 实时语音传输（500字节数据包）
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

### 运行程序
```bash
# GUI模式
python main.py

# 命令行模式
python main.py --no-gui

# 音频设备测试
python main.py --test-audio
```

## 配置说明

编辑 `config.yaml` 文件：

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

## 协议规范

**NRL2协议**
- 传输协议：UDP
- 默认端口：60050
- 包格式：48字节头部 + 可变长度数据
- 语音编码：G.711 A-law（8000Hz，单声道）

**数据包类型**
- TYPE_VOICE (1)：语音数据（500字节G.711）
- TYPE_HEARTBEAT (2)：心跳包
- TYPE_TEXT (5)：文本消息（UTF-8）
- TYPE_SERVER_VOICE (9)：服务器互联语音

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
4. 需要与nrllink服务器版本兼容

## 联系方式

如有问题或建议，请发送邮件至：misakazunami@qq.com