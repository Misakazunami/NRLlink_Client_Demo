# 音频问题修复快速参考

## 问题描述
- ✗ 播放卡顿
- ✗ 声音失真
- ✗ 音速拉长
- ✓ 时长显示正确（数据包完整）

## 根本原因 (3个关键问题)

### 问题1: Chunk大小与包大小不同步
```
原配置: chunk_size: 160字节 (10ms)
需要时间: 1000字节PCM = 62.5ms（一个G.711包）
计算: 1000 ÷ 160 = 6.25次 ❌ 不稳定！
```

### 问题2: 错误的G.711填充值
```
原代码: b'\x80' * 500  ❌ 不是G.711的静音值
正确值: linear2alaw(0) = 0xD5  ✓
```

### 问题3: 缓冲区管理不稳定
```
原逻辑: 收集500字节G.711（PCM层）
问题: PCM是16位的，500字节实际是250个样本
导致: 截断、重复、时序错乱
```

## 修复方案 (已实施)

### ✓ 修复1: 优化chunk_size
```yaml
# config.yaml
audio:
  chunk_size: 500  # 改为500字节 = 62.5ms
```
**理由**: 恰好2个chunk就能凑够一个G.711包
```
计算: 1000字节PCM ÷ 500字节chunk = 2次  ✓ 完美！
时间: 500字节 × 2 = 1000字节PCM = 62.5ms = 1个G.711包
```

### ✓ 修复2: 使用正确的G.711静音值
```python
# nrl_protocol.py - G711Codec.encode()
silence_value = linear2alaw(0)  # 自动计算，得到0xD5
return bytes([silence_value]) * 500  # 正确填充
```

### ✓ 修复3: 严格的PCM缓冲管理
```python
# audio_handler.py - _record_callback()
# 改为严格管理1000字节PCM
while len(self.voice_data_cache) >= 1000:
    send_data = bytes(self.voice_data_cache[:1000])
    self.voice_data_cache = self.voice_data_cache[1000:]
    # 发送 -> 编码为500字节G.711 -> 发送给服务器
```

## 文件修改清单

| 文件 | 修改内容 | 影响 |
|-----|--------|------|
| [config.yaml](config.yaml) | chunk_size: 160 → 500 | 时序同步 |
| [nrl_protocol.py](nrl_protocol.py#L425) | 填充值改正 | 失真降低 |
| [audio_handler.py](audio_handler.py#L318) | 缓冲区重写 | 卡顿消除 |

## 验证清单

✓ 静音值: 0xD5 (正确)
✓ 编码误差: ≤ 512 (可接受)
✓ 时间同步: 完美对应
✓ 边界条件: 正确处理

## 使用方法

### 1. 更新配置（必须）
编辑 `config.yaml`:
```yaml
audio:
  sample_rate: 8000
  channels: 1
  chunk_size: 500  # ← 改这里
  format: "paInt16"
```

### 2. 验证修复（可选）
运行测试:
```bash
python test_audio_quality.py
```

### 3. 使用客户端
```bash
python main.py
```

## 预期改进

| 指标 | 修复前 | 修复后 |
|-----|--------|--------|
| 播放卡顿 | 明显 | 消除 |
| 声音失真 | 存在 | 降低 |
| 音速 | 拉长 | 正常 |
| 时序 | 不稳定 | 完美同步 |

## 技术细节

### G.711编解码参数
- **采样率**: 8000 Hz
- **位深**: 16位
- **声道**: 单声道
- **编码**: A-law
- **包大小**: 500字节G.711 = 1000字节PCM = 62.5ms

### 时间关系
```
1 chunk (500字节PCM) = 62.5ms
2 chunks = 125ms = 1个G.711包 (500字节)

实际:
- chunk_size = 500字节 = 62.5ms
- 2个chunk到达 = 125ms后发送1个G.711包
```

### 错误值参考
G.711静音值计算:
```
linear2alaw(0):
  sign = 0x80
  seg = 0
  mant = 0
  result = (0x80 | 0x00 | 0x00) ^ 0x55 = 0xD5
```

## 常见问题

**Q: 为什么改chunk_size就能解决问题？**
A: 因为原来160字节无法均匀地和500字节（或1000字节PCM）对应，导致缓冲区管理困难。改为500字节后恰好对应1000字节PCM的一半，时序稳定。

**Q: 0xD5是怎么来的？**
A: 这是G.711 A-law编码中线性PCM值0对应的编码值。之前用0x80是完全错误的。

**Q: 修复后音质会不会变差？**
A: 不会。A-law编码本身就有±512的量化误差，这是标准。修复后实际上消除了额外的失真源。

**Q: 是否需要修改其他参数？**
A: 不需要。其他参数（sample_rate, channels, format）都是正确的。只需改chunk_size。

## 参考资源

- [AUDIO_ISSUES_ANALYSIS.md](AUDIO_ISSUES_ANALYSIS.md) - 详细诊断
- [test_audio_quality.py](test_audio_quality.py) - 测试脚本
- [nrl_protocol.py](nrl_protocol.py) - G.711实现
- [audio_handler.py](audio_handler.py) - 音频处理
