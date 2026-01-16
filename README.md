# NRL客户端Demo

基于nrllink项目开发的Python客户端，实现基本的无线电网络互联功能。

## 最近更新

**2026年1月16日** - 完整的协议兼容性优化
- ✅ 与nrllink Go服务器完全协议兼容
- ✅ 改进的网络连接稳定性和错误恢复
- ✅ 增强的G.711编解码和错误处理
- ✅ 详见 [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md)

## 功能特性

✅ **基本功能**
- 设备上线注册（与服务器同步的CPUID哈希）
- 心跳维持连接（SSID=200规范格式）
- 配置管理

✅ **语音通信**
- G.711 A-law语音编解码（与nrllink完全一致）
- 实时语音传输（500字节数据包）
- PTT（按键说话）功能
- 音频设备管理
- 网络抖动缓冲

✅ **消息功能**
- 文本消息发送/接收（支持UTF-8，最大1412字节）
- 消息日志记录
- 协议规范验证

✅ **用户界面**
- 图形化界面（GUI模式）
- 命令行界面（CLI模式）
- 实时状态显示
- 音频级别监控

## 项目结构

```
nrl_client_demo/
├── main.py                  # 主程序入口
├── nrl_client.py            # NRL客户端核心类
├── nrl_protocol.py          # NRL协议处理模块
├── audio_handler.py         # 音频处理模块
├── gui_client.py            # 图形化界面
├── config.yaml              # 配置文件
├── requirements.txt         # Python依赖
├── README.md               # 说明文档
└── OPTIMIZATION_REPORT.md  # 优化报告（新增）
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

编辑 `config.yaml` 文件进行配置：

```yaml
# 服务器配置
server:
  host: "127.0.0.1"  # 服务器地址
  port: 60050        # 服务器UDP端口

# 设备配置
device:
  callsign: "TEST01"  # 设备呼号
  ssid: 1            # 设备SSID
  cpuid: "12345678"  # 设备CPUID（用于哈希计算）
  password: "000000" # 设备密码
  model: 1           # 设备型号

# 音频配置
audio:
  sample_rate: 8000  # 采样率
  channels: 1         # 声道数
  chunk_size: 1024   # 音频块大小
  format: "paInt16" # 音频格式

# 网络配置
network:
  buffer_size: 1460  # 网络缓冲区大小（与nrllink一致）
  heartbeat_interval: 30  # 心跳间隔（秒）
```

## 使用方法

### GUI模式（推荐）

```bash
python main.py
```

### 命令行模式

```bash
python main.py --no-gui
```

### 音频设备测试

```bash
# 列出所有音频设备
python main.py --list-audio

# 测试音频设备
python main.py --test-audio
```

## 协议说明

### NRL2协议兼容性
- **版本**: NRL2
- **端口**: UDP 60050
- **包格式**: 48字节头部 + 可变长度数据
- **编码**: G.711 A-law (8000 Hz, mono)

### 数据包类型
| 类型ID | 名称 | 说明 | 数据部分 |
|--------|------|------|---------|
| 1 | TYPE_VOICE | 语音数据 | 500字节G.711 |
| 2 | TYPE_HEARTBEAT | 心跳包 | 无 |
| 3 | TYPE_CONFIG | 设备配置 | 可变 |
| 5 | TYPE_TEXT | 文本消息 | UTF-8文本 |
| 6 | TYPE_CONTROL | 设备控制 | 控制命令 |
| 7 | TYPE_JOIN_GROUP | 加入群组 | 群组ID |
| 9 | TYPE_SERVER_VOICE | 服务器互联语音 | 500字节G.711 |

### 心跳包规范
- SSID: 固定为200
- Type: 2 (TYPE_HEARTBEAT)
- Count: 0
- 无数据部分
- 定期发送维持连接

### 语音包规范
- Type: 1或9 (TYPE_VOICE或TYPE_SERVER_VOICE)
- 数据长度: 恒定500字节
- 编码: G.711 A-law
- 采样率: 8000 Hz
- 通道: 单声道

## API参考

### NRLClient类

```python
# 初始化客户端
client = NRLClient(config_file='config.yaml')

# 连接到服务器
client.connect()

# 发送语音数据
client.send_voice_data(voice_bytes)

# 发送文本消息
client.send_text_message("Hello, World!")

# 启动语音传输
client.start_voice_transmission()

# 停止语音传输
client.stop_voice_transmission()

# 获取设备状态
status = client.get_status()

# 断开连接
client.disconnect()

# 关闭客户端
client.close()
```

### 回调函数

```python
# 设置消息回调
def on_message(msg):
    print(f"收到消息: {msg['data']}")

client.set_message_callback(on_message)

# 设置语音回调
def on_voice(pcm_data, info=None):
    print(f"收到语音: {len(pcm_data)} bytes")

client.set_voice_callback(on_voice)

# 设置状态回调
def on_status(key, value):
    print(f"状态变化: {key} = {value}")

client.set_status_callback(on_status)
```

## 优化特性

### 与nrllink完全兼容
- ✅ CPUID哈希算法一致
- ✅ 心跳包格式规范
- ✅ G.711编解码一致
- ✅ 协议头部格式完全相同

### 错误恢复机制
- ✅ 自动重连
- ✅ 连续错误检测
- ✅ 数据包验证
- ✅ 超时恢复

### 性能优化
- ✅ 缓冲区优化
- ✅ 线程安全
- ✅ 内存管理
- ✅ 网络抖动处理

## 故障排查

### 连接失败
1. 检查服务器地址和端口是否正确
2. 确保网络连接畅通
3. 查看日志中的详细错误信息
4. 尝试使用测试音频验证环境

### 语音质量差
1. 检查网络延迟和丢包率
2. 调整音频设备设置
3. 检查G.711编解码错误率
4. 查看缓冲区是否溢出

### 消息无法发送
1. 确认客户端已连接
2. 检查消息长度是否超过限制
3. 验证文本编码（应为UTF-8）

## 开发指南

### 扩展功能
- 在 `NRLClient` 类中添加新的协议方法
- 在 `NRLProtocol` 类中实现新数据包类型
- 在 `AudioHandler` 中扩展音频处理

### 调试模式
```bash
python main.py --debug
```

### 日志查看
```bash
# 实时日志
tail -f nrl_client.log

# 或在代码中设置日志级别
logging.getLogger().setLevel(logging.DEBUG)
```

## 许可证

基于nrllink项目开发，遵循相同的开源许可证。

## 相关项目

- [nrllink](https://github.com/) - Go语言服务器实现
- [NRL2协议规范](./doc/) - 协议文档

## 更新日志

### v1.1.0 (2026-01-16)
- ✅ 完全的协议兼容性优化
- ✅ 网络连接稳定性改进
- ✅ G.711编解码增强
- ✅ 详细的优化报告

### v1.0.0 (初始版本)
- 基础NRL协议实现
- 语音通信功能
- GUI界面

### 调试模式

```bash
python main.py --debug
```

## 操作说明

### 连接服务器
1. 配置正确的服务器地址和端口
2. 点击"连接"按钮
3. 等待连接成功

### 语音通信
1. 点击"按住说话 (PTT)"按钮开始语音传输
2. 对着麦克风说话
3. 再次点击按钮停止语音传输

### 发送文本消息
1. 在消息输入框中输入文本
2. 点击"发送"按钮

### 音频设备管理
- 点击"测试音频设备"测试麦克风和扬声器
- 使用"开始播放"和"停止播放"控制音频播放

## 协议说明

基于nrllink项目的NRL2协议：

- **协议版本**: NRL2
- **传输协议**: UDP
- **默认端口**: 60050
- **语音编码**: G.711 A-law
- **采样率**: 8000 Hz
- **心跳间隔**: 30秒

### 数据包格式

```
[版本:4字节][长度:2字节][CPUID:4字节][密码:3字节][预留:5字节]
[类型:1字节][状态:1字节][计数器:2字节][呼号:6字节][SSID:1字节][设备模式:1字节]
[原始呼号:6字节][原始SSID:1字节][原始IP:4字节][预留:5字节][数据:变长]
```

### 数据类型

- `0x01`: 语音数据 (G.711)
- `0x02`: 心跳包
- `0x03`: 设备配置
- `0x05`: 文本消息
- `0x06`: 设备控制
- `0x07`: 群组管理
- `0x09`: 服务器互联语音

## 开发说明

### 核心模块

- **NRLProtocol**: 协议编解码
- **NRLClient**: 客户端核心功能
- **AudioHandler**: 音频设备管理
- **VoiceProcessor**: 语音编解码处理

### 扩展开发

1. **添加新消息类型**: 在 `nrl_protocol.py` 中扩展 `NRLPacket.TYPE_*`
2. **自定义音频处理**: 修改 `audio_handler.py` 中的处理逻辑
3. **界面定制**: 修改 `gui_client.py` 中的界面组件

## 注意事项

1. **音频设备**: 确保系统有可用的麦克风和扬声器
2. **网络配置**: 防火墙需要开放UDP端口60050
3. **权限**: 某些系统可能需要管理员权限访问音频设备
4. **兼容性**: 需要与nrllink服务器版本兼容

## 故障排除

### 连接失败
- 检查服务器地址和端口配置
- 确认网络连接正常
- 检查防火墙设置

### 音频问题
- 运行音频设备测试
- 检查系统音频设置
- 确认音频设备权限

### 语音传输问题
- 检查G.711编解码是否正常
- 确认音频数据格式正确
- 查看日志获取详细信息

## 更新日志

### v1.0.0 (2024-01)
- ✨ 初始版本发布
- ✨ 基本连接和心跳功能
- ✨ G.711语音编解码
- ✨ 图形化界面
- ✨ 命令行界面
- ✨ 音频设备管理

## 许可证

本项目基于nrllink项目开发，遵循相应的开源协议。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

---

**注意**: 这是一个演示项目，用于学习和研究目的。在实际部署前，请确保进行充分的测试和安全评估。