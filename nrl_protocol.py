"""
NRL协议处理模块
基于nrllink项目的协议格式实现
"""
import struct
import time
import socket
from typing import Optional, Tuple

class NRLPacket:
    """NRL协议数据包类"""
    
    # 协议常量
    PROTOCOL_VERSION = b"NRL2"
    HEADER_SIZE = 48
    
    # 数据类型
    TYPE_VOICE = 1      # G.711语音数据
    TYPE_HEARTBEAT = 2  # 心跳包
    TYPE_CONFIG = 3     # 设备配置
    TYPE_TEXT = 5       # 文本消息
    TYPE_CONTROL = 6    # 设备控制
    TYPE_JOIN_GROUP = 7 # 加入群组
    TYPE_SERVER_VOICE = 9 # 服务器互联语音
    
    def __init__(self):
        self.timestamp = time.time()
        self.udp_addr = None
        self.version = self.PROTOCOL_VERSION
        self.length = 0
        self.cpuid = b"\x00" * 5  # CPUID (5字节)
        self.password = b"\x00" * 3
        self.packet_type = 0
        self.status = 0x01  # 状态 (0x01表示在线)
        self.count = 0
        self.callsign = b"" * 6
        self.ssid = 0
        self.dev_mode = 0x10  # 设备模式 (0x10表示正常模式)
        self.original_callsign = b"" * 6
        self.original_ssid = 0
        self.original_ip = b"\x00" * 4
        self.data = b""
    
    def encode(self) -> bytes:
        """编码数据包 - 严格按照NRL21协议规范"""
        # 计算总长度
        data_len = len(self.data) if self.data else 0
        total_length = 48 + data_len
        
        # 构建头部
        header = bytearray(48)
        
        # 协议版本 (4字节) - 固定为NRL2
        header[0:4] = b'NRL2'
        
        # 总长度（2字节，大端序）
        struct.pack_into(">H", header, 4, total_length)
        
        # CPUID（5字节）- 根据协议规范，使用4字节哈希值，第5字节为0
        if len(self.cpuid) >= 4:
            header[6:10] = self.cpuid[:4]  # 只使用前4字节
            header[10] = 0  # 第5字节固定为0
        else:
            header[6:11] = self.cpuid.ljust(5, b'\x00')[:5]
        
        # 密码（3字节） - 默认填充为0
        header[10:13] = b'\x00' * 3  # 根据协议规范，密码在偏移10-12
        
        # 数据包类型（1字节）
        header[20] = self.packet_type
        
        # 状态（1字节）- 根据协议规范，bit0用作DCD/PTT标志
        header[21] = self.status if self.status else 0x01
        
        # 计数器（2字节，大端序）- 根据协议规范，计数器在偏移21-22（与Go版本一致）
        struct.pack_into(">H", header, 21, self.count)
        
        # 呼号（6字节）
        if isinstance(self.callsign, str):
            callsign_bytes = self.callsign.encode('utf-8').ljust(6, b'\x00')[:6]
        else:
            callsign_bytes = self.callsign.ljust(6, b'\x00')[:6]
        header[24:30] = callsign_bytes
        
        # SSID（1字节）
        header[30] = self.ssid
        
        # 设备模式（1字节）
        header[31] = self.dev_mode if self.dev_mode else 0x10
        
        # 服务器互联语音包（Type=9）的额外字段
        if self.packet_type == NRLPacket.TYPE_SERVER_VOICE:
            # 原始呼号（6字节）
            if isinstance(self.original_callsign, str):
                orig_callsign_bytes = self.original_callsign.encode('utf-8').ljust(6, b'\x00')[:6]
            else:
                orig_callsign_bytes = self.original_callsign.ljust(6, b'\x00')[:6]
            header[32:38] = orig_callsign_bytes
            
            # 原始SSID（1字节）
            header[38] = self.original_ssid
            
            # 原始IP（4字节）
            if len(self.original_ip) >= 4:
                header[39:43] = self.original_ip[:4]
            else:
                header[39:43] = b'\x00' * 4
        else:
            # 其他类型包，这些字段填充为0
            header[32:38] = b'\x00' * 6
            header[38] = 0
            header[39:43] = b'\x00' * 4
        
        # 数据部分
        if data_len > 0:
            return bytes(header) + self.data
        else:
            return bytes(header)
    
    def decode(self, data: bytes) -> bool:
        """解码数据包 - 严格按照NRL21协议规范"""
        if len(data) < self.HEADER_SIZE:
            return False
        
        try:
            # 检查版本
            self.version = data[0:4]
            if self.version != self.PROTOCOL_VERSION:
                return False
            
            # 解析长度
            self.length = struct.unpack(">H", data[4:6])[0]
            
            # 检查数据长度
            if len(data) < self.length:
                # 报文不完整，无法解析
                return False
            
            # CPUID (5字节) - 根据协议规范，实际使用4字节
            self.cpuid = data[6:11]
            
            # 密码 (3字节) - 根据协议规范，密码在偏移10-12
            self.password = data[10:13]
            
            # 类型
            self.packet_type = data[20]
            
            # 状态 - 根据协议规范，bit0用作DCD/PTT标志
            self.status = data[21]
            
            # 计数器 - 根据协议规范，计数器在偏移21-22（与Go版本一致）
            self.count = struct.unpack(">H", data[21:23])[0]
            
            # 呼号
            callsign_bytes = data[24:30]
            self.callsign = callsign_bytes.rstrip(b'\x00').rstrip(b'\r')
            
            # SSID
            self.ssid = data[30]
            
            # 设备模式
            self.dev_mode = data[31]
            
            # 服务器互联语音包（Type=9）的额外字段
            if self.packet_type == NRLPacket.TYPE_SERVER_VOICE:
                # 原始呼号
                orig_callsign_bytes = data[32:38]
                self.original_callsign = orig_callsign_bytes.rstrip(b'\x00').rstrip(b'\r')
                
                # 原始SSID
                self.original_ssid = data[38]
                
                # 原始IP
                self.original_ip = data[39:43]
            else:
                # 其他类型包，这些字段填充为0
                self.original_callsign = b""
                self.original_ssid = 0
                self.original_ip = b"\x00" * 4
            
            # 数据部分
            # 兼容性处理：部分Go实现（转发/替换头部）可能未正确更新长度字段
            # 如果长度字段恰好等于头部长度但实际上报文尾部包含数据，则回退使用原始报文尾部数据
            if self.length == self.HEADER_SIZE and len(data) > self.HEADER_SIZE:
                # 长度字段标记为仅头部，但实际报文包含数据，使用报文尾部所有数据
                self.data = data[self.HEADER_SIZE:]
            else:
                # 正常使用长度字段指定的数据范围
                self.data = data[self.HEADER_SIZE:self.length]
            
            return True
            
        except (struct.error, IndexError) as e:
            print(f"解码错误: {e}")
            return False
    
    def get_callsign_ssid(self) -> str:
        """获取呼号和SSID组合字符串"""
        try:
            callsign_str = self.callsign.decode('utf-8', errors='ignore').strip()
            return f"{callsign_str}-{self.ssid}"
        except:
            return f"UNKNOWN-{self.ssid}"
    
    def __str__(self) -> str:
        return (f"NRLPacket(version={self.version}, type={self.packet_type}, "
                f"callsign={self.get_callsign_ssid()}, cpuid={self.cpuid.hex()})")


class NRLProtocol:
    """NRL协议处理类"""
    
    def __init__(self):
        self.packet_count = 0
    
    def create_voice_packet(self, callsign: str, ssid: int, cpuid: str, 
                          voice_data: bytes, dev_mode: int = 1) -> NRLPacket:
        """创建语音数据包 - 根据协议规范，语音包包含500字节G.711数据
        
        参考nrllink的encodeNRL21函数
        语音包格式：48字节头部 + 500字节G.711数据
        """
        packet = NRLPacket()
        packet.packet_type = NRLPacket.TYPE_VOICE
        packet.callsign = callsign.encode('utf-8').ljust(6, b'\x00')[:6]
        packet.ssid = ssid
        
        # 根据协议规范，使用4字节CPUID哈希值
        if cpuid and isinstance(cpuid, str):
            # 如果提供的是字符串，检查是否需要计算哈希值
            if len(cpuid) == 8 and all(c in '0123456789abcdefABCDEF' for c in cpuid):
                # 8位十六进制字符串，直接转换为字节
                cpuid_bytes = bytes.fromhex(cpuid)
            elif '-' in cpuid:
                # 呼号-SSID格式，计算哈希值
                cpuid_bytes = calculate_cpuid(cpuid)
            else:
                # 其他字符串，计算哈希值
                cpuid_bytes = calculate_cpuid(cpuid)
        else:
            # 否则假设已经是字节
            cpuid_bytes = cpuid.encode('utf-8').ljust(4, b'\x00')[:4] if isinstance(cpuid, str) else cpuid[:4]
        
        packet.cpuid = cpuid_bytes.ljust(5, b'\x00')  # 扩展到5字节，第5字节为0
        
        packet.dev_mode = dev_mode if dev_mode else 0x01  # 默认设备模式
        packet.status = 0x01  # 根据协议规范，bit0用作DCD/PTT标志
        
        # 确保语音数据正好是500字节
        if not voice_data or len(voice_data) == 0:
            voice_data = b'\x80' * 500  # 静音数据
        elif len(voice_data) < 500:
            voice_data = voice_data.ljust(500, b'\x80')  # G.711静音值
        elif len(voice_data) > 500:
            voice_data = voice_data[:500]
        
        packet.data = voice_data
        packet.count = self.packet_count
        self.packet_count = (self.packet_count + 1) & 0xFFFF  # 确保16位计数器
        return packet
    
    def create_heartbeat_packet(self, callsign: str, ssid: int, cpuid: str = None, 
                               dev_mode: int = 0x10) -> NRLPacket:
        """创建心跳包 - 根据协议规范，心跳包只有头部，没有数据部分
        
        参考nrllink的encodeNRL21函数
        心跳包特点：
        - Type字段为2（TYPE_HEARTBEAT）
        - 没有数据部分（长度为48字节）
        - SSID通常为200表示服务器连接
        - 计数器通常为1（作为协议的一部分）
        """
        packet = NRLPacket()
        packet.packet_type = NRLPacket.TYPE_HEARTBEAT
        packet.callsign = callsign.encode('utf-8').ljust(6, b'\x00')[:6]
        packet.ssid = ssid  # 通常为200
        
        # 根据协议规范，心跳包使用4字节CPUID哈希值
        if cpuid is None:
            # 使用callsign-SSID生成哈希值（与Go版本一致）
            cpuid_bytes = calculate_cpuid(f"{callsign}-{ssid}")
        else:
            # 如果提供了CPUID，检查是否需要计算哈希值
            # 如果cpuid是8位十六进制字符串（如配置文件中的CPUID），直接使用
            # 如果cpuid是呼号-SSID格式，计算哈希值
            if isinstance(cpuid, str):
                if len(cpuid) == 8 and all(c in '0123456789abcdefABCDEF' for c in cpuid):
                    # 8位十六进制字符串，直接转换为字节
                    cpuid_bytes = bytes.fromhex(cpuid)
                elif '-' in cpuid:
                    # 呼号-SSID格式，计算哈希值
                    cpuid_bytes = calculate_cpuid(cpuid)
                else:
                    # 其他字符串，计算哈希值
                    cpuid_bytes = calculate_cpuid(cpuid)
            else:
                cpuid_bytes = cpuid[:4]
            
        packet.cpuid = cpuid_bytes.ljust(5, b'\x00')  # 扩展到5字节，第5字节为0
        packet.dev_mode = dev_mode if dev_mode else 0x10  # 默认0x10表示正常模式
        packet.status = 0x01  # 根据协议规范，状态为0x01
        packet.count = 1  # 心跳包计数器通常为1（与Go版本一致）
        packet.data = b""  # 心跳包没有数据部分
        return packet
    
    def create_config_packet(self, callsign: str, ssid: int, cpuid: str, 
                           config_data: bytes, dev_mode: int = 1) -> NRLPacket:
        """创建配置数据包"""
        packet = NRLPacket()
        packet.packet_type = NRLPacket.TYPE_CONFIG
        packet.callsign = callsign.encode('utf-8').ljust(6, b'\x00')[:6]
        packet.ssid = ssid
        packet.cpuid = cpuid.encode('utf-8').ljust(4, b'\x00')[:4]
        packet.dev_mode = dev_mode
        packet.data = config_data
        packet.count = self.packet_count
        self.packet_count = (self.packet_count + 1) & 0xFFFF  # 确保16位计数器
        return packet

    def create_text_packet(self, callsign: str, ssid: int, cpuid: str, text_data: bytes, dev_mode: int = 1) -> NRLPacket:
        """创建文本数据包 - 根据协议规范，文本包长度=48+文本长度"""
        packet = NRLPacket()
        packet.packet_type = NRLPacket.TYPE_TEXT
        packet.callsign = callsign.encode('utf-8').ljust(6, b'\x00')[:6]
        packet.ssid = ssid
        
        # 根据协议规范，使用4字节CPUID哈希值
        if isinstance(cpuid, str):
            if len(cpuid) == 8 and all(c in '0123456789abcdefABCDEF' for c in cpuid):
                # 8位十六进制字符串，直接转换为字节
                cpuid_bytes = bytes.fromhex(cpuid)
            elif '-' in cpuid:
                # 呼号-SSID格式，计算哈希值
                cpuid_bytes = calculate_cpuid(cpuid)
            else:
                # 其他字符串，计算哈希值
                cpuid_bytes = calculate_cpuid(cpuid)
        else:
            cpuid_bytes = cpuid[:4]
        packet.cpuid = cpuid_bytes.ljust(5, b'\x00')  # 扩展到5字节，第5字节为0
        
        packet.dev_mode = dev_mode if dev_mode else 0x01  # 默认设备模式
        packet.status = 0x01  # 根据协议规范，状态为0x01
        packet.data = text_data
        packet.count = self.packet_count
        self.packet_count = (self.packet_count + 1) & 0xFFFF  # 确保16位计数器
        return packet
    
    def create_server_voice_packet(self, callsign: str, ssid: int, cpuid: str, 
                                 voice_data: bytes, original_callsign: str, 
                                 original_ssid: int, original_ip: bytes, 
                                 dev_mode: int = 1) -> NRLPacket:
        """创建服务器互联语音包 - Type=9，包含原始呼号/IP信息"""
        packet = NRLPacket()
        packet.packet_type = NRLPacket.TYPE_SERVER_VOICE
        packet.callsign = callsign.encode('utf-8').ljust(6, b'\x00')[:6]
        packet.ssid = ssid
        
        # 根据协议规范，使用4字节CPUID哈希值
        cpuid_bytes = cpuid.encode('utf-8').ljust(4, b'\x00')[:4]
        packet.cpuid = cpuid_bytes.ljust(5, b'\x00')  # 扩展到5字节，第5字节为0
        
        packet.dev_mode = dev_mode if dev_mode else 0x01  # 默认设备模式
        packet.status = 0x01  # 根据协议规范，bit0用作DCD/PTT标志
        
        # 设置原始设备信息
        packet.original_callsign = original_callsign.encode('utf-8').ljust(6, b'\x00')[:6]
        packet.original_ssid = original_ssid
        packet.original_ip = original_ip.ljust(4, b'\x00')[:4] if len(original_ip) >= 4 else b'\x00' * 4
        
        # 确保语音数据正好是500字节
        if len(voice_data) != 500:
            # 填充或截断到500字节
            if len(voice_data) < 500:
                voice_data = voice_data.ljust(500, b'\x80')  # G.711静音值
            else:
                voice_data = voice_data[:500]
        
        packet.data = voice_data
        packet.count = self.packet_count
        self.packet_count = (self.packet_count + 1) & 0xFFFF  # 确保16位计数器
        return packet
    



def calculate_cpuid(callsign: str) -> bytes:
    """计算CPUID，与Go服务器保持一致
    
    参考nrllink的calculateCpuId函数：
    将字符串生成32位哈希值，哈希算法为: hash = (hash*31 + char) & 0xFFFFFFFF
    返回4字节大端序的二进制数据
    """
    # 将字符串生成32位哈希值，与Go版本的calculateCpuId函数一致
    hash_val = 0
    for char in callsign:
        hash_val = (hash_val * 31 + ord(char)) & 0xFFFFFFFF  # 确保32位
    
    # 转换为4字节大端序
    return struct.pack(">I", hash_val)

# G.711编解码相关常量（与Go版本保持一致）
SEG_MASK = 0x70
QUANT_MASK = 0x0F
SEG_SHIFT = 4
BIAS = 0x84

def alaw2linear(code: int) -> int:
    """A-law解码到线性PCM"""
    code ^= 0x55
    
    sign = code & 0x80
    seg = (code & 0x70) >> 4
    quant = code & 0x0F
    
    if seg == 0:
        sample = (quant << 1) | 0x01
    else:
        sample = ((quant << 1) | 0x21) << (seg - 1)
    
    if sign != 0:
        return sample << 3
    else:
        return -(sample << 3)

def linear2alaw(sample: int) -> int:
    """线性PCM编码到A-law"""
    if sample < 0:
        if sample == -32768:
            sample = -32767
        sample = -sample
        sign = 0x00
    else:
        sign = 0x80
    
    # 13位绝对值用于A-law
    pcm = sample >> 3
    
    seg = 0
    if pcm >= 32:
        seg = 1
        t = 64
        while seg < 7 and pcm >= t:
            t <<= 1
            seg += 1
    
    if seg == 0:
        mant = (pcm >> 1) & 0x0F
    else:
        mant = (pcm >> seg) & 0x0F
    
    return (sign | (seg << 4) | mant) ^ 0x55

class G711Codec:
    """G.711编解码器 - 与nrllink的Go实现保持一致
    
    参考nrllink的g711.go实现，支持A-law编解码
    A-law是用于欧洲、非洲和亚洲大部分地区的标准语音压缩算法
    """
    
    @staticmethod
    def encode(pcm_data: bytes) -> bytes:
        """PCM数据编码为G.711 A-law
        
        将16位线性PCM样本编码为8位A-law样本
        输出总是500字节（用于NRL协议的语音包）
        """
        if not pcm_data:
            # 返回静音帧
            return b'\x80' * 500
        
        encoded = bytearray()
        
        try:
            # 处理所有可用的PCM样本（每个样本2字节，小端序）
            for i in range(0, len(pcm_data), 2):
                if i + 1 < len(pcm_data):
                    # 小端序读取16位有符号整数
                    sample = int.from_bytes(pcm_data[i:i+2], 'little', signed=True)
                    encoded.append(linear2alaw(sample))
        except Exception as e:
            print(f"G.711编码错误: {e}")
            return bytes([linear2alaw(0)]) * 500
        
        # 确保输出正好是500字节
        if len(encoded) > 500:
            # 如果超过500字节，截断
            return bytes(encoded[:500])
        elif len(encoded) < 500:
            # 如果不足500字节，用G.711静音值填充
            # 正确的G.711静音值: linear2alaw(0) = 0xD5
            silence_value = linear2alaw(0)
            encoded.extend([silence_value] * (500 - len(encoded)))
        
        return bytes(encoded)
    
    @staticmethod
    def decode(alaw_data: bytes) -> bytes:
        """G.711 A-law数据解码为PCM
        
        将8位A-law样本解码为16位线性PCM样本
        输出为小端序的16位有符号整数对
        """
        # 检查输入数据
        if not alaw_data or len(alaw_data) == 0:
            print(f"G.711解码警告: 输入数据为空")
            return b""
        
        decoded = bytearray()
        
        try:
            # 处理所有G.711样本（每个样本1字节）
            for byte in alaw_data:
                sample = alaw2linear(byte)
                # 小端序编码16位有符号整数
                decoded.extend(sample.to_bytes(2, 'little', signed=True))
                
        except Exception as e:
            print(f"G.711解码错误: {e}, 数据长度: {len(alaw_data)}")
            return b""
        
        return bytes(decoded)