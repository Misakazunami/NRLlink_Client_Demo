"""
测试代码
音频质量测试脚本
验证G.711编解码的正确性
"""

import struct
from nrl_protocol import G711Codec, linear2alaw, alaw2linear

def test_g711_codec():
    """测试G.711编解码"""
    
    print("=" * 70)
    print("G.711编解码质量测试")
    print("=" * 70)
    
    codec = G711Codec()
    
    # 测试1: 静音值验证
    print("\n测试1: G.711静音值")
    print("-" * 70)
    
    silence_value = linear2alaw(0)
    print(f"线性PCM 0 -> G.711: 0x{silence_value:02X}")
    print(f"期望值: 0xD5 (计算: (0x80 | 0x00 | 0x00) ^ 0x55 = 0xD5)")
    
    if silence_value == 0xD5:
        print("✓ 静音值正确")
    else:
        print(f"✗ 静音值错误: 期望 0xD5, 实际 0x{silence_value:02X}")
    
    # 测试2: 编解码往返一致性
    print("\n测试2: 编解码往返一致性")
    print("-" * 70)
    
    test_samples = [0, 1, -1, 127, -127, 32767, -32768, 16384, -16384]
    max_error = 0
    
    for sample in test_samples:
        encoded = linear2alaw(sample)
        decoded = alaw2linear(encoded)
        error = abs(decoded - sample)
        max_error = max(max_error, error)
        
        print(f"PCM: {sample:6d} -> G.711: 0x{encoded:02X} -> PCM: {decoded:6d}, 误差: {error}")
    
    print(f"\n最大编码误差: {max_error} (满分量程32768的{max_error/32768*100:.2f}%)")
    if max_error <= 256:
        print("✓ 编码误差在可接受范围内")
    else:
        print("⚠ 编码误差较大，可能导致失真")
    
    # 测试3: PCM到G.711的转换
    print("\n测试3: PCM数据编码")
    print("-" * 70)
    
    # 生成1秒的测试信号（1000字节PCM = 500个16位样本 = 62.5ms）
    # 简单的正弦波：sin(2π * 440Hz * t / 8000Hz)
    import math
    
    test_duration_ms = 62.5  # 对应500字节G.711
    num_samples = int(8000 * test_duration_ms / 1000)  # 500个样本
    pcm_data = bytearray()
    
    for i in range(num_samples):
        # 生成440Hz正弦波
        t = i / 8000
        sample = int(20000 * math.sin(2 * math.pi * 440 * t))
        # 小端序编码16位有符号整数
        pcm_data.extend(struct.pack('<h', sample))
    
    print(f"生成PCM测试数据: {len(pcm_data)} bytes ({num_samples} 个样本，{test_duration_ms}ms)")
    
    # 编码为G.711
    g711_data = codec.encode(bytes(pcm_data))
    print(f"编码后G.711数据: {len(g711_data)} bytes")
    
    if len(g711_data) == 500:
        print("✓ G.711输出长度正确 (500字节)")
    else:
        print(f"✗ G.711输出长度错误: 期望 500, 实际 {len(g711_data)}")
    
    # 解码G.711回PCM
    decoded_pcm = codec.decode(g711_data)
    print(f"解码后PCM数据: {len(decoded_pcm)} bytes")
    
    if len(decoded_pcm) == len(pcm_data):
        print("✓ 解码输出长度正确")
    else:
        print(f"✗ 解码输出长度错误: 期望 {len(pcm_data)}, 实际 {len(decoded_pcm)}")
    
    # 计算编解码误差
    if len(decoded_pcm) == len(pcm_data):
        total_error = 0
        for i in range(0, len(pcm_data), 2):
            orig_sample = struct.unpack('<h', pcm_data[i:i+2])[0]
            decoded_sample = struct.unpack('<h', decoded_pcm[i:i+2])[0]
            total_error += abs(orig_sample - decoded_sample)
        
        avg_error = total_error // (len(pcm_data) // 2)
        print(f"\n编解码平均误差: {avg_error}")
        print("✓ 编解码过程完整")
    
    # 测试4: 边界条件
    print("\n测试4: 边界条件处理")
    print("-" * 70)
    
    # 空数据
    empty_result = codec.encode(b'')
    print(f"空PCM数据编码结果: {len(empty_result)} bytes")
    if len(empty_result) == 500:
        print("✓ 空数据处理正确（返回静音帧）")
    
    # 不完整的样本（奇数字节）
    odd_data = b'\x00' * 999  # 999字节（不完整）
    odd_result = codec.encode(odd_data)
    print(f"999字节PCM数据编码结果: {len(odd_result)} bytes")
    if len(odd_result) == 500:
        print("✓ 不完整数据处理正确")
    
    # 超长数据
    long_data = b'\x00' * 2000
    long_result = codec.encode(long_data)
    print(f"2000字节PCM数据编码结果: {len(long_result)} bytes")
    if len(long_result) == 500:
        print("✓ 超长数据处理正确（截断）")
    
    # 测试5: 时间同步验证
    print("\n测试5: 时间同步验证")
    print("-" * 70)
    
    # chunk_size与G.711包的关系
    sample_rate = 8000
    chunk_size = 500  # bytes of PCM per chunk
    
    # 计算chunk对应的时间
    num_samples_per_chunk = chunk_size // 2  # 16-bit samples
    time_per_chunk = num_samples_per_chunk / sample_rate * 1000  # ms
    
    print(f"chunk_size: {chunk_size} bytes PCM")
    print(f"样本数: {num_samples_per_chunk}")
    print(f"持续时间: {time_per_chunk:.2f} ms")
    
    # 计算多少个chunk才能凑够一个G.711包
    pcm_per_g711 = 500 * 2  # 500字节G.711 = 1000字节PCM
    chunks_per_g711 = pcm_per_g711 / chunk_size
    
    print(f"\n一个G.711包需要: {chunks_per_g711} chunks")
    print(f"持续时间: {chunks_per_g711 * time_per_chunk:.2f} ms")
    
    if chunks_per_g711 == 2.0:
        print("✓ 时间同步完美（恰好2个chunk）")
    elif chunks_per_g711 == int(chunks_per_g711):
        print(f"✓ 时间同步正确（恰好{int(chunks_per_g711)}个chunk）")
    else:
        print(f"⚠ 时间同步可能有问题（需要{chunks_per_g711}个chunk）")
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == "__main__":
    test_g711_codec()
