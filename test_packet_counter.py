
"""
测试代码
数据包计数器测试脚本
验证数据包计数器是否与Go服务器兼容
"""

import struct
from nrl_protocol import NRLProtocol, NRLPacket

def test_packet_counter():
    """测试数据包计数器的正常工作"""
    
    print("=" * 60)
    print("NRL数据包计数器测试")
    print("=" * 60)
    
    protocol = NRLProtocol()
    
    # 测试1: 创建多个语音包，验证计数器递增
    print("\n测试1: 语音包计数器递增")
    print("-" * 60)
    
    voice_packets = []
    for i in range(5):
        packet = protocol.create_voice_packet("TEST", 1, "test", b'\x80' * 500, 1)
        voice_packets.append(packet)
        print(f"语音包{i}: 计数器 = {packet.count} (期望: {i})")
    
    # 验证计数器是否正确递增
    expected_count = 0
    for i, packet in enumerate(voice_packets):
        if packet.count != expected_count % 0x10000:
            print(f"✗ 语音包{i}计数器错误: 期望 {expected_count % 0x10000}, 实际 {packet.count}")
            return False
        expected_count += 1
    print("✓ 语音包计数器递增正确")
    
    # 测试2: 创建心跳包，验证计数器为固定值
    print("\n测试2: 心跳包计数器固定值")
    print("-" * 60)
    
    # 重置协议计数器
    protocol.packet_count = 0
    
    heartbeat = protocol.create_heartbeat_packet("TEST", 200, "test", 0x10)
    print(f"心跳包: 计数器 = {heartbeat.count} (期望: 1)")
    
    if heartbeat.count != 1:
        print(f"✗ 心跳包计数器错误: 期望 1, 实际 {heartbeat.count}")
        return False
    print("✓ 心跳包计数器正确")
    
    # 测试3: 验证编码/解码计数器
    print("\n测试3: 数据包编码/解码计数器")
    print("-" * 60)
    
    # 重置计数器
    protocol.packet_count = 0
    
    # 创建一个测试数据包
    original_packet = protocol.create_voice_packet("TEST", 1, "test", b'\x80' * 500, 1)
    original_count = original_packet.count
    print(f"原始数据包计数器: {original_count}")
    
    # 编码数据包
    encoded_data = original_packet.encode()
    print(f"编码后数据包大小: {len(encoded_data)} 字节")
    
    # 验证计数器在数据包中的位置
    # 计数器应该在偏移21-22（与Go版本一致）
    encoded_count = struct.unpack(">H", encoded_data[21:23])[0]
    print(f"编码中的计数器值（偏移21-22）: {encoded_count}")
    
    if encoded_count != original_count:
        print(f"✗ 编码的计数器错误: 期望 {original_count}, 实际 {encoded_count}")
        return False
    print("✓ 编码的计数器正确")
    
    # 解码数据包
    decoded_packet = NRLPacket()
    if decoded_packet.decode(encoded_data):
        print(f"解码后的计数器值: {decoded_packet.count}")
        
        if decoded_packet.count != original_count:
            print(f"✗ 解码的计数器错误: 期望 {original_count}, 实际 {decoded_packet.count}")
            return False
        print("✓ 解码的计数器正确")
    else:
        print("✗ 解码失败")
        return False
    
    # 测试4: 验证16位计数器溢出
    print("\n测试4: 16位计数器溢出处理")
    print("-" * 60)
    
    protocol.packet_count = 0xFFFF  # 设置为最大值
    
    # 创建一个数据包，应该导致溢出
    packet1 = protocol.create_voice_packet("TEST", 1, "test", b'\x80' * 500, 1)
    packet2 = protocol.create_voice_packet("TEST", 1, "test", b'\x80' * 500, 1)
    
    print(f"溢出前的计数器: {packet1.count} (期望: 65535)")
    print(f"溢出后的计数器: {packet2.count} (期望: 0)")
    
    if packet1.count != 0xFFFF:
        print(f"✗ 溢出前计数器错误: 期望 {0xFFFF}, 实际 {packet1.count}")
        return False
    
    if packet2.count != 0:
        print(f"✗ 溢出后计数器错误: 期望 0, 实际 {packet2.count}")
        return False
    
    print("✓ 16位计数器溢出处理正确")
    
    # 测试5: 验证协议头部结构
    print("\n测试5: 协议头部结构验证")
    print("-" * 60)
    
    packet = protocol.create_voice_packet("TEST", 1, "test", b'\x80' * 500, 1)
    encoded = packet.encode()
    
    # 验证头部字段位置
    print(f"版本 (0-3)      : {encoded[0:4]} (期望: b'NRL2')")
    print(f"长度 (4-5)      : {struct.unpack('>H', encoded[4:6])[0]} (期望: {48+500})")
    print(f"Type (20)       : {encoded[20]} (期望: 1)")
    print(f"Status (21)     : {encoded[21]} (期望: 1)")
    print(f"计数器 (21-22)  : {struct.unpack('>H', encoded[21:23])[0]}")
    print(f"呼号 (24-29)    : {encoded[24:30]}")
    print(f"SSID (30)       : {encoded[30]}")
    
    if encoded[0:4] != b'NRL2':
        print("✗ 版本字段错误")
        return False
    
    if struct.unpack('>H', encoded[4:6])[0] != 548:
        print("✗ 长度字段错误")
        return False
    
    if encoded[20] != 1:  # TYPE_VOICE
        print("✗ Type字段错误")
        return False
    
    print("✓ 协议头部结构正确")
    
    print("\n" + "=" * 60)
    print("所有测试通过！✓")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_packet_counter()
    exit(0 if success else 1)
