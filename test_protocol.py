#!/usr/bin/env python3
"""
NRL协议测试脚本
用于验证协议数据包的正确性
"""

import struct
from nrl_protocol import NRLProtocol, NRLPacket, calculate_cpuid

def test_heartbeat_packet():
    """测试心跳包"""
    print("=== 测试心跳包 ===")
    
    protocol = NRLProtocol()
    packet = protocol.create_heartbeat_packet("BH6ERO", 200, None, 200)
    encoded = packet.encode()
    
    print(f"心跳包总长度: {len(encoded)} 字节")
    print(f"协议标识: {encoded[0:4]}")
    print(f"总长度字段: {struct.unpack('>H', encoded[4:6])[0]}")
    print(f"CPUID: {encoded[6:11].hex()}")
    print(f"密码: {encoded[10:13].hex()}")
    print(f"类型: {encoded[20]}")
    print(f"状态: {encoded[21]}")
    print(f"计数器: {struct.unpack('>H', encoded[22:24])[0]}")
    print(f"呼号: {encoded[24:30]}")
    print(f"SSID: {encoded[30]}")
    print(f"设备模式: {encoded[31]}")
    
    # 验证解码
    decoded_packet = NRLPacket()
    success = decoded_packet.decode(encoded)
    print(f"解码成功: {success}")
    if success:
        print(f"解码后呼号: {decoded_packet.callsign}")
        print(f"解码后SSID: {decoded_packet.ssid}")
        print(f"解码后类型: {decoded_packet.packet_type}")
    
    print()

def test_voice_packet():
    """测试语音包"""
    print("=== 测试语音包 ===")
    
    # 创建500字节的测试语音数据
    voice_data = b'\x80' * 500  # G.711静音值
    
    protocol = NRLProtocol()
    packet = protocol.create_voice_packet("BH6ERO", 1, "12345678", voice_data, 1)
    encoded = packet.encode()
    
    print(f"语音包总长度: {len(encoded)} 字节")
    print(f"协议标识: {encoded[0:4]}")
    print(f"总长度字段: {struct.unpack('>H', encoded[4:6])[0]}")
    print(f"CPUID: {encoded[6:11].hex()}")
    print(f"密码: {encoded[10:13].hex()}")
    print(f"类型: {encoded[20]}")
    print(f"状态: {encoded[21]}")
    print(f"计数器: {struct.unpack('>H', encoded[22:24])[0]}")
    print(f"呼号: {encoded[24:30]}")
    print(f"SSID: {encoded[30]}")
    print(f"设备模式: {encoded[31]}")
    print(f"语音数据长度: {len(encoded[48:])}")
    
    # 验证解码
    decoded_packet = NRLPacket()
    success = decoded_packet.decode(encoded)
    print(f"解码成功: {success}")
    if success:
        print(f"解码后呼号: {decoded_packet.callsign}")
        print(f"解码后类型: {decoded_packet.packet_type}")
        print(f"解码后数据长度: {len(decoded_packet.data)}")
    
    print()

def test_text_packet():
    """测试文本包"""
    print("=== 测试文本包 ===")
    
    text_message = "Hello, NRL!"
    
    protocol = NRLProtocol()
    packet = protocol.create_text_packet("BH6ERO", 1, "12345678", text_message.encode('utf-8'), 1)
    encoded = packet.encode()
    
    print(f"文本包总长度: {len(encoded)} 字节")
    print(f"协议标识: {encoded[0:4]}")
    print(f"总长度字段: {struct.unpack('>H', encoded[4:6])[0]}")
    print(f"CPUID: {encoded[6:11].hex()}")
    print(f"密码: {encoded[10:13].hex()}")
    print(f"类型: {encoded[20]}")
    print(f"状态: {encoded[21]}")
    print(f"计数器: {struct.unpack('>H', encoded[22:24])[0]}")
    print(f"呼号: {encoded[24:30]}")
    print(f"SSID: {encoded[30]}")
    print(f"设备模式: {encoded[31]}")
    print(f"文本数据: {encoded[48:].decode('utf-8')}")
    
    # 验证解码
    decoded_packet = NRLPacket()
    success = decoded_packet.decode(encoded)
    print(f"解码成功: {success}")
    if success:
        print(f"解码后呼号: {decoded_packet.callsign}")
        print(f"解码后类型: {decoded_packet.packet_type}")
        print(f"解码后文本: {decoded_packet.data.decode('utf-8')}")
    
    print()

def test_server_voice_packet():
    """测试服务器互联语音包"""
    print("=== 测试服务器互联语音包 ===")
    
    # 创建500字节的测试语音数据
    voice_data = b'\x80' * 500  # G.711静音值
    original_ip = b'\xc0\xa8\x01\x01'  # 192.168.1.1
    
    protocol = NRLProtocol()
    packet = protocol.create_server_voice_packet(
        "BH6ERO", 200, "12345678", voice_data, "BH6ABC", 1, original_ip, 200
    )
    encoded = packet.encode()
    
    print(f"服务器语音包总长度: {len(encoded)} 字节")
    print(f"协议标识: {encoded[0:4]}")
    print(f"总长度字段: {struct.unpack('>H', encoded[4:6])[0]}")
    print(f"CPUID: {encoded[6:11].hex()}")
    print(f"密码: {encoded[10:13].hex()}")
    print(f"类型: {encoded[20]}")
    print(f"状态: {encoded[21]}")
    print(f"计数器: {struct.unpack('>H', encoded[22:24])[0]}")
    print(f"呼号: {encoded[24:30]}")
    print(f"SSID: {encoded[30]}")
    print(f"设备模式: {encoded[31]}")
    print(f"原始呼号: {encoded[32:38]}")
    print(f"原始SSID: {encoded[38]}")
    print(f"原始IP: {encoded[39:43].hex()}")
    print(f"语音数据长度: {len(encoded[48:])}")
    
    # 验证解码
    decoded_packet = NRLPacket()
    success = decoded_packet.decode(encoded)
    print(f"解码成功: {success}")
    if success:
        print(f"解码后呼号: {decoded_packet.callsign}")
        print(f"解码后类型: {decoded_packet.packet_type}")
        print(f"解码后原始呼号: {decoded_packet.original_callsign}")
        print(f"解码后原始IP: {decoded_packet.original_ip.hex()}")
    
    print()

def test_cpuid_calculation():
    """测试CPUID计算"""
    print("=== 测试CPUID计算 ===")
    
    callsign = "BH6ERO-200"
    cpuid = calculate_cpuid(callsign)
    print(f"呼号: {callsign}")
    print(f"CPUID: {cpuid.hex()}")
    print(f"CPUID长度: {len(cpuid)} 字节")
    
    # 验证与Go版本的一致性
    # Go版本的calculateCpuId函数使用相同的算法
    print(f"CPUID数值: {int.from_bytes(cpuid, 'big')}")
    
    print()

def test_protocol_compliance():
    """测试协议合规性"""
    print("=== 测试协议合规性 ===")
    
    # 测试心跳包合规性
    protocol = NRLProtocol()
    heartbeat = protocol.create_heartbeat_packet("BH6ERO", 200, None, 200)
    heartbeat_data = heartbeat.encode()
    
    print(f"心跳包合规性检查:")
    print(f"  总长度: {len(heartbeat_data)} 字节 (应为48字节)")
    print(f"  协议标识: {heartbeat_data[0:4]} (应为b'NRL2')")
    print(f"  长度字段: {struct.unpack('>H', heartbeat_data[4:6])[0]} (应为48)")
    print(f"  类型字段: {heartbeat_data[20]} (应为2)")
    print(f"  状态字段: {heartbeat_data[21]} (应为1)")
    print(f"  SSID: {heartbeat_data[30]} (应为200)")
    print(f"  设备模式: {heartbeat_data[31]} (应为200)")
    
    # 测试语音包合规性
    voice_data = b'\x80' * 500
    voice = protocol.create_voice_packet("BH6ERO", 1, "12345678", voice_data, 1)
    voice_encoded = voice.encode()
    
    print(f"\n语音包合规性检查:")
    print(f"  总长度: {len(voice_encoded)} 字节 (应为548字节)")
    print(f"  长度字段: {struct.unpack('>H', voice_encoded[4:6])[0]} (应为548)")
    print(f"  类型字段: {voice_encoded[20]} (应为1)")
    print(f"  语音数据长度: {len(voice_encoded[48:])} 字节 (应为500字节)")
    
    print()

def main():
    """主测试函数"""
    print("NRL协议测试开始...\n")
    
    test_cpuid_calculation()
    test_heartbeat_packet()
    test_voice_packet()
    test_text_packet()
    test_server_voice_packet()
    test_protocol_compliance()
    
    print("NRL协议测试完成！")

if __name__ == "__main__":
    main()