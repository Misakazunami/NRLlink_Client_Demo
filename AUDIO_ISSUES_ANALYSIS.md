# 音频失真、卡顿和拉长问题诊断报告

## 问题症状
- ✗ 语音时长显示正确（说明数据包完整）
- ✗ 播放有卡顿（缓冲区管理问题）
- ✗ 失真（编码或解码问题）
- ✗ 拉长（采样率或时序问题）

## 根本原因分析

### 🔴 问题1: chunk_size配置错误
**位置**: `config.yaml`
```yaml
chunk_size: 160  # ← 这是关键问题！
```

**分析**:
- 160字节是PCM数据（16位采样，单声道）
- 160字节 ÷ 2（16位）= 80个样本
- 采样率8000Hz：80个样本 = **10ms**
- 语音包需要**500字节G.711** = **500个样本** = **62.5ms**

**问题**:
```
需要采集: 500字节G.711 (62.5ms) = 1000字节PCM (62.5ms)
实际采集: 160字节PCM (10ms)

需要迭代: 1000 ÷ 160 = 6.25次
这导致有时需要7个chunk才能凑够500字节，有时只需6个
→ 时长计算不稳定，导致卡顿和失真
```

**正确的计算**:
```
目标: 500字节G.711每包 = 500个样本 = 62.5ms
采样率: 8000 Hz
正确的chunk_size: 160字节 (10ms) ✓ 实际可行，但需要缓冲

更好的chunk_size: 320字节 (20ms) 
或最优: 500字节 (62.5ms)
```

---

### 🔴 问题2: 音频编码逻辑错误
**位置**: `_record_callback()` 函数

**当前逻辑**:
```python
# 当cache >= 500字节时，立即发送
# 当超过20ms且cache有数据时，用0x80填充至500字节

# 问题: 
# - 如果160字节一次，需要凑够500字节
# - 6 × 160 = 960字节 (>500)
# - 第一个500字节发送，剩余460字节
# - 然后新数据来临...可能会被截断或重复
```

**导致的问题**:
- 音频断裂和卡顿
- 不稳定的语音包大小

---

### 🔴 问题3: 填充值错误
**位置**: `_record_callback()` 和 `G711Codec.encode()`

**当前实现**:
```python
voice_data = voice_data.ljust(500, b'\x80')  # G.711静音值
```

**问题**:
1. `b'\x80'` 是编码后的G.711值（表示约0），**不是PCM值**
2. 在PCM层面填充应该用 `b'\x00\x00'`（2字节，little-endian零值）
3. 在G.711层面填充应该是经过编码的0

**正确做法**:
```
PCM层填充: b'\x00\x00' × 250 (250个16位样本) = 500字节
G.711层填充: linear2alaw(0) = 0xD5 (经过XOR 0x55后的值)
            实际应该用: struct.pack('B', linear2alaw(0)) × 500
```

---

### 🔴 问题4: 字节序问题
**位置**: `_record_callback()` 的PCM数据处理

**PyAudio的数据格式**:
- `paInt16`: 小端序（little-endian）
- 每个样本: 2字节

**当前代码**:
```python
self.voice_data_cache.extend(in_data)  # 直接添加原始字节
```

**问题**:
- 直接累积字节没有问题，但计算时长时需要注意
- 500字节G.711 = 500个样本 = 62.5ms
- 对应的PCM = 1000字节 (500个16位样本)

---

### 🔴 问题5: 时序问题
**位置**: `_record_callback()` 的20ms间隔逻辑

**当前逻辑**:
```python
elif (current_time - self.last_voice_send_time) >= 0.020:
    # 发送并填充至500字节
```

**问题**:
1. 如果chunk到达不均匀，20ms的间隔不稳定
2. 填充的静音值可能导致接收端解码错误
3. 500字节包应该是恒定间隔的（62.5ms），不是20ms

---

### 🔴 问题6: G.711编码的样本处理
**位置**: `G711Codec.encode()`

**当前代码**:
```python
for i in range(0, len(pcm_data), 2):
    if i + 1 < len(pcm_data):
        sample = int.from_bytes(pcm_data[i:i+2], 'little', signed=True)
        encoded.append(linear2alaw(sample))
```

**问题**:
- 假设输入的PCM数据长度总是偶数
- 如果数据长度为奇数，最后一个字节会被忽略
- 解码时假设输出长度正好是500字节，这可能导致长度不匹配

---

## 解决方案

### ✓ 修复方案1: 优化chunk_size
**建议配置**:
```yaml
audio:
  sample_rate: 8000
  channels: 1
  chunk_size: 320    # 改为320 (20ms)
  # 或者 chunk_size: 500 (62.5ms) - 最优
```

**理由**:
- 320字节 = 160个样本 = 20ms（2倍的理想最小间隔）
- 1000字节PCM（62.5ms语音） = 160字节chunk × 6.25
- 仍然需要缓冲，但更稳定

---

### ✓ 修复方案2: 完全重写_record_callback
**新思路**:
```python
def _record_callback(self, in_data, frame_count, time_info, status):
    """改进的录音回调 - 严格按照500字节/包的要求"""
    if not self.is_recording:
        return (None, pyaudio.paContinue)
    
    self.record_buffer.append(in_data)
    
    with self.voice_cache_lock:
        self.voice_data_cache.extend(in_data)
        
        # 严格管理: 只在数据恰好达到1000字节PCM时编码和发送
        while len(self.voice_data_cache) >= 1000:  # 1000字节PCM
            pcm_chunk = bytes(self.voice_data_cache[:1000])
            self.voice_data_cache = self.voice_data_cache[1000:]
            self.last_voice_send_time = time.time()
            
            if self.audio_callback:
                self.audio_callback(pcm_chunk)
    
    return (None, pyaudio.paContinue)
```

**优势**:
- 每次发送恰好1000字节PCM = 500字节G.711
- 无需填充或截断
- 时序稳定

---

### ✓ 修复方案3: 正确的填充逻辑
**如果需要填充，应该这样做**:
```python
def pad_pcm_data(pcm_data: bytes, target_size: int = 1000) -> bytes:
    """使用静音值填充PCM数据"""
    if len(pcm_data) >= target_size:
        return pcm_data[:target_size]
    
    # 填充静音（小端序16位有符号零）
    silence = b'\x00\x00'  # 16位零值
    padding = silence * ((target_size - len(pcm_data)) // 2)
    
    return pcm_data + padding

def pad_g711_data(g711_data: bytes, target_size: int = 500) -> bytes:
    """使用静音值填充G.711数据"""
    if len(g711_data) >= target_size:
        return g711_data[:target_size]
    
    # 计算正确的G.711静音值
    silence_sample = linear2alaw(0)  # 应该是某个值
    # 但由于有XOR 0x55，需要验证
    silence_byte = bytes([silence_sample])
    padding = silence_byte * (target_size - len(g711_data))
    
    return g711_data + padding
```

---

### ✓ 修复方案4: 验证G.711静音值
```python
# 正确的G.711静音值验证：
# 在Go版本中：linear2alawTable[0] = ?
# 需要通过linear2alaw(0)计算得出

def calculate_silence_value():
    """计算G.711静音值"""
    sample = 0  # PCM零值
    if sample < 0:
        sample = -sample
        sign = 0x00
    else:
        sign = 0x80
    
    pcm = sample >> 3  # = 0
    seg = 0
    mant = (pcm >> 1) & 0x0F  # = 0
    
    return (sign | (seg << 4) | mant) ^ 0x55
    # = (0x80 | 0x00 | 0x00) ^ 0x55
    # = 0x80 ^ 0x55 = 0xD5
```

**所以G.711静音值应该是 0xD5（不是 0x80）**

---

## 推荐修复顺序

### 优先级1（立即修复）
1. ✓ 修改chunk_size为320或500
2. ✓ 修改_record_callback为严格的1000字节管理
3. ✓ 修正G.711静音值为0xD5

### 优先级2（改进）
4. ✓ 添加长度验证和错误检查
5. ✓ 添加音频质量统计信息
6. ✓ 添加测试脚本验证修复

### 优先级3（优化）
7. ✓ 性能优化
8. ✓ 抖动缓冲改进
9. ✓ 错误恢复机制

---

## 影响范围
- `config.yaml` - chunk_size参数
- `audio_handler.py` - _record_callback函数
- `nrl_protocol.py` - G711Codec.encode填充逻辑
- `nrl_client.py` - 语音传输回调

---

**预期效果**:
- ✓ 语音不再卡顿
- ✓ 失真显著降低
- ✓ 播放速度正确（不拉长）
- ✓ 音质接近原始PCM
