"""
NRL客户端主类
实现与服务器的UDP通信，设备管理，语音处理等功能
"""
import socket
import threading
import time
import logging
import yaml #type: ignore
import json
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

from nrl_protocol import NRLProtocol, NRLPacket, calculate_cpuid
from audio_handler import AudioHandler, VoiceProcessor

@dataclass
class DeviceConfig:
    """设备配置"""
    callsign: str
    ssid: int
    cpuid: str
    password: str
    model: int

@dataclass
class ServerConfig:
    """服务器配置"""
    host: str
    port: int

@dataclass
class ServerInfo:
    """服务器信息"""
    name: str
    host: str
    port: int

@dataclass
class AudioConfig:
    """音频配置"""
    sample_rate: int
    channels: int
    chunk_size: int
    format: str

@dataclass
class NetworkConfig:
    """网络配置"""
    buffer_size: int
    heartbeat_interval: int

class NRLClient:
    """NRL客户端主类"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.logger = logging.getLogger(__name__)
        
        # 配置
        self.device_config: Optional[DeviceConfig] = None
        self.server_config: Optional[ServerConfig] = None
        self.audio_config: Optional[AudioConfig] = None
        self.network_config: Optional[NetworkConfig] = None
        
        # 服务器列表
        self.servers_list: list[ServerInfo] = []
        self.current_server_index: int = 0
        
        # 网络
        self.socket = None
        self.is_connected = False
        self.receive_thread = None
        self.heartbeat_thread = None
        self.running = False
        
        # 协议处理
        self.protocol = NRLProtocol()
        
        # 音频处理
        self.audio_handler = None
        self.voice_processor = None
        
        # 状态
        self.device_status = {
            'online': False,
            'last_heartbeat': 0,
            'packets_sent': 0,
            'packets_received': 0,
            'voice_packets_sent': 0,
            'voice_packets_received': 0
        }
        
        # 回调函数
        self.message_callback: Optional[Callable[[Dict], None]] = None
        self.voice_callback: Optional[Callable[[bytes], None]] = None
        self.status_callback: Optional[Callable[[str, Any], None]] = None
        
        # 调试选项：绕过空包检查，强制解码所有包
        self.debug_force_decode = False
        
        # 加载配置
        self.load_config(config_file)
        
        # 初始化音频
        self.init_audio()
    
    def load_config(self, config_file: str):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 设备配置
            device_cfg = config_data.get('device', {})
            self.device_config = DeviceConfig(
                callsign=device_cfg.get('callsign', 'BH6ERO'),
                ssid=device_cfg.get('ssid', 1),
                cpuid=device_cfg.get('cpuid', '12345678'),
                password=device_cfg.get('password', '000000'),
                model=device_cfg.get('model', 1)
            )
            
            # 服务器配置
            server_cfg = config_data.get('server', {})
            self.server_config = ServerConfig(
                host=server_cfg.get('host', '43.143.14.24'),
                port=server_cfg.get('port', 60050)
            )
            
            # 加载服务器列表
            servers_cfg = config_data.get('servers', [])
            current_server_idx = config_data.get('current_server', 0)
            
            if servers_cfg:
                self.servers_list = []
                for server in servers_cfg:
                    server_info = ServerInfo(
                        name=server.get('name', f"服务器{len(self.servers_list) + 1}"),
                        host=server.get('host', '127.0.0.1'),
                        port=server.get('port', 60050)
                    )
                    self.servers_list.append(server_info)
                
                # 设置当前服务器索引
                if 0 <= current_server_idx < len(self.servers_list):
                    self.current_server_index = current_server_idx
                else:
                    self.current_server_index = 0
                
                # 使用当前选择的服务器配置
                if self.servers_list:
                    current_server = self.servers_list[self.current_server_index]
                    self.server_config.host = current_server.host
                    self.server_config.port = current_server.port
                    
                self.logger.info(f"已加载 {len(self.servers_list)} 个服务器配置，当前使用: {self.servers_list[self.current_server_index].name if self.servers_list else '无'}")
            else:
                # 如果没有服务器列表，使用单个服务器配置
                self.servers_list = [ServerInfo(
                    name="默认服务器",
                    host=self.server_config.host,
                    port=self.server_config.port
                )]
                self.current_server_index = 0
            
            # 音频配置
            audio_cfg = config_data.get('audio', {})
            self.audio_config = AudioConfig(
                sample_rate=audio_cfg.get('sample_rate', 8000),
                channels=audio_cfg.get('channels', 1),
                chunk_size=audio_cfg.get('chunk_size', 1024),
                format=audio_cfg.get('format', 'paInt16')
            )
            
            # 网络配置
            network_cfg = config_data.get('network', {})
            self.network_config = NetworkConfig(
                buffer_size=network_cfg.get('buffer_size', 1460),
                heartbeat_interval=network_cfg.get('heartbeat_interval', 30)
            )
            
            self.logger.info("配置加载成功")
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            raise
    
    def init_audio(self):
        """初始化音频处理"""
        try:
            self.audio_handler = AudioHandler(
                sample_rate=self.audio_config.sample_rate,
                channels=self.audio_config.channels,
                chunk_size=self.audio_config.chunk_size,
                format_str=self.audio_config.format
            )
            
            self.voice_processor = VoiceProcessor()
            
            self.logger.info("音频处理初始化成功")
            
        except Exception as e:
            self.logger.error(f"音频处理初始化失败: {e}")
            raise
    
    def connect(self) -> bool:
        """连接到服务器
        
        参考nrllink的udpServer函数的连接流程：
        1. 创建UDP套接字
        2. 发送初始心跳包进行设备注册
        3. 启动接收线程处理来自服务器的数据
        4. 启动心跳线程维持连接
        """
        try:
            # 关闭已有的连接
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            
            # 创建UDP套接字
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)  # 5秒超时
            
            # 设置接收缓冲区大小（参考nrllink配置）
            try:
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 
                                     self.network_config.buffer_size)
            except:
                self.logger.warning("设置接收缓冲区失败，使用默认配置")
            
            # 测试连接 - 发送初始心跳包进行设备注册
            # 使用设备配置的SSID
            test_packet = self.protocol.create_heartbeat_packet(
                self.device_config.callsign,
                self.device_config.ssid,  # 使用设备配置的SSID
                self.device_config.cpuid,  # 使用配置中的CPUID
                self.device_config.model   # 设备模式
            )
            
            self.socket.sendto(test_packet.encode(), 
                             (self.server_config.host, self.server_config.port))
            
            self.logger.info(f"已发送初始连接包到 {self.server_config.host}:{self.server_config.port}")
            
            self.is_connected = True
            self.running = True
            
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            # 启动心跳线程
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.heartbeat_thread.start()
            
            self._update_status('connected', True)
            self.logger.info(f"连接到服务器成功: {self.server_config.host}:{self.server_config.port}")
            self.logger.info(f"NRL_Link Client Beta V1.3")
            self.logger.info(f"------------------------------------")
            self.logger.info(f"N     N  RRRRRR   L      ")
            self.logger.info(f"N N   N  R     R  L      ")
            self.logger.info(f"N  N  N  RRRRRR   L      ")
            self.logger.info(f"N   N N  R   R    L      ")
            self.logger.info(f"N     N  R     R  LLLLLL ")
            self.logger.info(f"------------------------------------")
            self.logger.info(f"欢迎使用NRL客户端,本客户端目前为测试版本")
            self.logger.info(f"当前连接到服务器的设备呼号: {self.device_config.callsign}")
            self.logger.info(f"当前连接到服务器的设备SSID: {self.device_config.ssid}")
            self.logger.info(f"------------------------------------")

            return True
            
        except socket.error as e:
            self.logger.error(f"套接字错误: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            self.logger.error(f"连接服务器失败: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开连接"""
        self.running = False
        self.is_connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self._update_status('connected', False)
        self.logger.info("已断开服务器连接")
    
    def _receive_loop(self):
        """接收数据循环
        
        参考nrllink的udpProcess函数
        主要功能：
        1. 循环接收UDP数据包
        2. 解析NRL协议数据包
        3. 路由处理不同类型的数据包
        4. 统计数据包计数
        """
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                if not self.socket:
                    time.sleep(0.1)
                    continue
                
                # 接收数据
                data, addr = self.socket.recvfrom(self.network_config.buffer_size)
                
                if not data or len(data) < 48:
                    self.logger.warning(f"接收到无效数据包（长度: {len(data)}）")
                    continue
                
                # 解析数据包
                packet = NRLPacket()
                if not packet.decode(data):
                    self.logger.warning(f"数据包解析失败: {addr}")
                    continue
                
                # 处理数据包
                self._handle_packet(packet, addr)
                self.device_status['packets_received'] += 1
                
                # 重置错误计数
                consecutive_errors = 0
                
            except socket.timeout:
                # 超时是正常的，不计为错误
                continue
            except ConnectionError as e:
                self.logger.error(f"连接错误: {e}")
                consecutive_errors += 1
            except Exception as e:
                if self.running:
                    self.logger.error(f"接收数据错误: {e}")
                    consecutive_errors += 1
            
            # 检查连续错误
            if consecutive_errors >= max_consecutive_errors:
                self.logger.error(f"连续接收错误达到{max_consecutive_errors}次，尝试重新连接")
                self.is_connected = False
                # 可选：自动重新连接
                time.sleep(2)
                consecutive_errors = 0
    
    def _heartbeat_loop(self):
        """心跳循环
        
        参考nrllink的设备在线检查机制
        主要功能：
        1. 定期发送心跳包维持连接
        2. 检测心跳响应超时
        3. 在连接丢失时自动重连
        """
        heartbeat_failures = 0
        max_failures = 3
        
        while self.running:
            try:
                if self.is_connected:
                    if not self.send_heartbeat():
                        heartbeat_failures += 1
                        if heartbeat_failures >= max_failures:
                            self.logger.warning("心跳失败次数过多，标记为离线")
                            self.is_connected = False
                            heartbeat_failures = 0
                    else:
                        heartbeat_failures = 0
                
                time.sleep(self.network_config.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"心跳错误: {e}")
                heartbeat_failures += 1
                if heartbeat_failures >= max_failures:
                    self.is_connected = False
                    heartbeat_failures = 0
    
    def _handle_packet(self, packet: NRLPacket, addr: tuple):
        """处理接收到的数据包"""
        self.logger.debug(f"收到数据包: {packet}")
        
        # 根据协议规范，检查状态位的DCD/PTT标志
        if packet.packet_type == NRLPacket.TYPE_VOICE or packet.packet_type == NRLPacket.TYPE_SERVER_VOICE:
            # 如果状态位bit0为0，表示监听/非发送模式，应丢弃包
            if packet.status & 0x01 == 0:
                self.logger.debug(f"丢弃语音包: 状态位表示非发送模式 from {packet.get_callsign_ssid()}")
                return
        
        if packet.packet_type == NRLPacket.TYPE_VOICE:
            self._handle_voice_packet(packet)
            self.device_status['voice_packets_received'] += 1
            
        elif packet.packet_type == NRLPacket.TYPE_HEARTBEAT:
            self._handle_heartbeat_packet(packet)
            
        elif packet.packet_type == NRLPacket.TYPE_TEXT:
            self._handle_text_packet(packet)
            
        elif packet.packet_type == NRLPacket.TYPE_SERVER_VOICE:
            self._handle_server_voice_packet(packet)
            self.device_status['voice_packets_received'] += 1
            
        else:
            self.logger.info(f"收到未知类型数据包: type={packet.packet_type}")
    
    def _handle_voice_packet(self, packet: NRLPacket):
        """处理语音数据包 - 使用抖动缓冲机制"""
        try:
            # 验证语音数据
            if not packet.data or len(packet.data) == 0:
                if not self.debug_force_decode:
                    self.logger.warning(f"收到空语音数据包 from {packet.get_callsign_ssid()}")
                    return
                else:
                    self.logger.info(f"[调试模式] 收到空语音数据包，强制解码 from {packet.get_callsign_ssid()}")
                    # 创建空数据包以供解码
                    packet.data = b'\x80' * 500
            elif self.debug_force_decode and len(packet.data) != 500:
                # 调试模式：忽略长度检查，直接使用最后 500 字节
                if len(packet.data) > 500:
                    original_len = len(packet.data)
                    packet.data = packet.data[-500:]  # 提取最后 500 字节
                    self.logger.info(f"[调试模式] 语音包长度异常 ({original_len} bytes)，提取最后 500 字节解码")
                elif len(packet.data) < 500:
                    # 如果小于 500 字节，前面补静音数据
                    original_len = len(packet.data)
                    packet.data = b'\x80' * (500 - len(packet.data)) + packet.data
                    self.logger.info(f"[调试模式] 语音包长度不足 ({original_len} bytes)，补充静音数据至 500 字节")
            
            # 解码语音数据
            pcm_data = self.voice_processor.decode_voice(packet.data)
            
            if not pcm_data:
                self.logger.error(f"语音解码失败，返回空数据 from {packet.get_callsign_ssid()}")
                return
                
            # 播放语音（使用抖动缓冲）
            if self.audio_handler and self.audio_handler.is_playback_active():
                self.audio_handler.add_playback_data(pcm_data)
            
            # 调用语音回调
            if self.voice_callback:
                self.voice_callback(pcm_data)
            
            self.logger.debug(f"处理语音数据包成功: {len(packet.data)} bytes from {packet.get_callsign_ssid()}")
            
        except Exception as e:
            self.logger.error(f"处理语音数据包失败: {e}")
            self.logger.error(f"数据包信息: type={packet.packet_type}, callsign={packet.get_callsign_ssid()}, data_len={len(packet.data)}")
    
    def _handle_heartbeat_packet(self, packet: NRLPacket):
        """处理心跳数据包 - 根据协议规范，心跳包只有头部，没有数据"""
        self.device_status['last_heartbeat'] = time.time()
        self.logger.debug(f"收到心跳包: {packet.get_callsign_ssid()}, CPUID: {packet.cpuid.hex()}")
        
        # 验证心跳包格式
        if packet.data:
            self.logger.warning(f"心跳包包含数据: {len(packet.data)} 字节，不符合协议规范")
        
        if len(packet.cpuid) != 5:
            self.logger.warning(f"心跳包CPUID长度异常: {len(packet.cpuid)} 字节")
    
    def _handle_text_packet(self, packet: NRLPacket):
        """处理文本数据包 - 根据协议规范，文本包长度=48+文本长度"""
        try:
            # 验证文本包格式
            if not packet.data:
                if not self.debug_force_decode:
                    self.logger.warning(f"收到空文本数据包 from {packet.get_callsign_ssid()}")
                    return
                else:
                    self.logger.info(f"[调试模式] 收到空文本数据包，强制解码 from {packet.get_callsign_ssid()}")
                    packet.data = b'[EmptyTXTPak]'
            elif self.debug_force_decode:
                # 调试模式：忽略长度检查，直接使用原始数据解码
                self.logger.debug(f"[调试模式] 文本包长度: {len(packet.data)} bytes，直接解码")
            
            text_data = packet.data.decode('utf-8', errors='ignore')
            message = {
                'type': 'text',
                'from': packet.get_callsign_ssid(),
                'data': text_data,
                'timestamp': time.time(),
                'length': len(packet.data)
            }
            
            if self.message_callback:
                self.message_callback(message)
            
            self.logger.info(f"收到文本消息: {text_data} (长度: {len(packet.data)} 字节)")
            
        except Exception as e:
            self.logger.error(f"处理文本数据包失败: {e}")
            self.logger.error(f"数据包信息: type={packet.packet_type}, callsign={packet.get_callsign_ssid()}, data_len={len(packet.data)}")
    
    def _handle_server_voice_packet(self, packet: NRLPacket):
        """处理服务器互联语音包 - Type=9，包含原始呼号/IP信息"""
        try:
            self.logger.debug(f"收到服务器互联语音包: {packet.get_callsign_ssid()}")
            self.logger.debug(f"原始设备: {packet.original_callsign.decode('utf-8', errors='ignore')}-{packet.original_ssid}")
            self.logger.debug(f"原始IP: {'.'.join(str(b) for b in packet.original_ip)}")
            
            # 检查语音数据包长度
            if not packet.data:
                if not self.debug_force_decode:
                    self.logger.warning(f"收到空服务器互联语音数据包 from {packet.get_callsign_ssid()}")
                    return
                else:
                    self.logger.info(f"[调试模式] 收到空服务器互联语音数据包，强制解码 from {packet.get_callsign_ssid()}")
                    packet.data = b'\x80' * 500
            
            if len(packet.data) == 0:
                if not self.debug_force_decode:
                    self.logger.warning(f"服务器互联语音数据包长度为0 from {packet.get_callsign_ssid()}")
                    return
                else:
                    packet.data = b'\x80' * 500
            elif self.debug_force_decode and len(packet.data) != 500:
                # 调试模式：忽略长度检查，直接使用最后 500 字节
                if len(packet.data) > 500:
                    original_len = len(packet.data)
                    packet.data = packet.data[-500:]  # 提取最后 500 字节
                    self.logger.info(f"[调试模式] 服务器互联语音包长度异常 ({original_len} bytes)，提取最后 500 字节解码")
                elif len(packet.data) < 500:
                    # 如果小于 500 字节，前面补静音数据
                    original_len = len(packet.data)
                    packet.data = b'\x80' * (500 - len(packet.data)) + packet.data
                    self.logger.info(f"[调试模式] 服务器互联语音包长度不足 ({original_len} bytes)，补充静音数据至 500 字节")
            elif not self.debug_force_decode and len(packet.data) != 500:
                self.logger.warning(f"服务器互联语音数据包长度不是500字节: {len(packet.data)} from {packet.get_callsign_ssid()}")
                # 仍然尝试处理非标准长度的数据
            
            # 解码G.711语音数据
            pcm_data = self.voice_processor.decode_voice(packet.data)
            
            if not pcm_data:
                self.logger.error(f"服务器互联语音解码失败，返回空数据 from {packet.get_callsign_ssid()}")
                return
                
            # 播放语音
            if self.audio_handler and self.audio_handler.is_playback_active():
                self.audio_handler.add_playback_data(pcm_data)
            
            # 调用语音回调，包含原始设备信息
            if self.voice_callback:
                # 添加原始设备信息到回调数据
                original_info = {
                    'original_callsign': packet.original_callsign.decode('utf-8', errors='ignore').strip(),
                    'original_ssid': packet.original_ssid,
                    'original_ip': '.'.join(str(b) for b in packet.original_ip),
                    'relay_callsign': packet.get_callsign_ssid()
                }
                self.voice_callback(pcm_data, original_info)
            
            self.logger.debug(f"处理服务器互联语音数据包成功: {len(packet.data)} bytes from {packet.get_callsign_ssid()}")
            
        except Exception as e:
            self.logger.error(f"处理服务器互联语音数据包失败: {e}")
            self.logger.error(f"数据包信息: type={packet.packet_type}, callsign={packet.get_callsign_ssid()}, data_len={len(packet.data)}")
    
    def send_voice_data(self, voice_data: bytes) -> bool:
        """发送语音数据 - 参考nrllink的语音转发机制
        
        参考nrllink的语音转发特点：
        1. 每个语音包包含500字节G.711数据
        2. 使用状态位的bit0作为发送/接收标志
        3. 计数器用于包排序
        """
        try:
            if not self.is_connected:
                self.logger.warning("未连接到服务器，无法发送语音")
                return False
            
            if not voice_data:
                self.logger.warning("语音数据为空")
                return False
            
            # 确保数据长度正好是500字节
            if len(voice_data) < 500:
                # 填充静音数据（G.711的0值编码）
                voice_data = voice_data + (b'\x80' * (500 - len(voice_data)))
            elif len(voice_data) > 500:
                # 截断超长数据
                self.logger.warning(f"语音数据超长（{len(voice_data)}字节），截断为500字节")
                voice_data = voice_data[:500]
            
            # 创建语音数据包
            packet = self.protocol.create_voice_packet(
                self.device_config.callsign,
                self.device_config.ssid,
                self.device_config.cpuid,
                voice_data,
                self.device_config.model
            )
            
            if not packet:
                self.logger.error("语音包创建失败")
                return False
            
            # 发送数据包
            packet_data = packet.encode()
            
            if not packet_data or len(packet_data) == 0:
                self.logger.error("语音包编码失败")
                return False
            
            self.socket.sendto(packet_data, 
                             (self.server_config.host, self.server_config.port))
            
            self.device_status['voice_packets_sent'] += 1
            self.device_status['packets_sent'] += 1
            
            self.logger.debug(f"语音包已发送: {len(voice_data)} bytes, 总长度: {len(packet_data)} bytes")
            return True
            
        except socket.error as e:
            self.logger.error(f"语音数据发送失败（套接字错误）: {e}")
            return False
        except Exception as e:
            self.logger.error(f"发送语音数据失败: {e}")
            return False
    
    def send_text_message(self, message: str) -> bool:
        """发送文本消息 - 根据协议规范，文本包长度=48+文本长度
        
        参考nrllink的文本消息处理（TYPE_TEXT = 5）
        """
        try:
            if not self.is_connected:
                self.logger.warning("未连接到服务器，无法发送文本消息")
                return False
            
            if not message or len(message) == 0:
                self.logger.warning("文本消息为空")
                return False
            
            # 编码文本消息（UTF-8）
            text_bytes = message.encode('utf-8')
            
            # 限制文本长度（参考nrllink的缓冲区大小1460字节）
            max_text_length = 1460 - 48  # 减去头部长度
            if len(text_bytes) > max_text_length:
                self.logger.warning(f"文本消息过长（{len(text_bytes)}字节），截断为{max_text_length}字节")
                text_bytes = text_bytes[:max_text_length]
            
            # 创建文本数据包
            packet = self.protocol.create_text_packet(
                self.device_config.callsign,
                self.device_config.ssid,
                self.device_config.cpuid,
                text_bytes,
                self.device_config.model
            )
            
            # 发送数据包
            packet_data = packet.encode()
            self.socket.sendto(packet_data, 
                             (self.server_config.host, self.server_config.port))
            
            self.device_status['packets_sent'] += 1
            self.logger.info(f"文本消息已发送: {message} (长度: {len(text_bytes)} 字节)")
            return True
            
        except socket.error as e:
            self.logger.error(f"文本消息发送失败（套接字错误）: {e}")
            return False
        except Exception as e:
            self.logger.error(f"发送文本消息失败: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """发送心跳包 - 根据协议规范，心跳包只有头部，没有数据
        
        参考nrllink的设备心跳机制
        心跳包参数：
        - SSID: 200（服务器连接标记）
        - Type: 2（TYPE_HEARTBEAT）
        - 无数据部分
        """
        try:
            if not self.is_connected or not self.socket:
                return False
            
            # 创建心跳包
            packet = self.protocol.create_heartbeat_packet(
                self.device_config.callsign,
                self.device_config.ssid,  # 使用设备配置的SSID
                self.device_config.cpuid,  # 使用配置的CPUID
                self.device_config.model   # 设备模式
            )
            
            if not packet:
                self.logger.error("心跳包创建失败")
                return False
            
            packet_data = packet.encode()
            
            if not packet_data or len(packet_data) == 0:
                self.logger.error("心跳包编码失败")
                return False
            
            # 发送心跳包
            self.socket.sendto(packet_data, 
                             (self.server_config.host, self.server_config.port))
            
            self.device_status['packets_sent'] += 1
            self.logger.debug(f"心跳包已发送: {packet.get_callsign_ssid()}, "
                            f"CPUID: {packet.cpuid.hex()}, 长度: {len(packet_data)} bytes")
            return True
            
        except socket.error as e:
            self.logger.error(f"心跳包发送失败（套接字错误）: {e}")
            return False
        except Exception as e:
            self.logger.error(f"发送心跳包失败: {e}")
            return False
    
    def start_voice_transmission(self) -> bool:
        """开始语音传输"""
        try:
            if not self.is_connected:
                self.logger.warning("未连接到服务器")
                return False
            
            if not self.audio_handler:
                self.logger.error("音频处理器未初始化")
                return False
            
            # 开始播放（接收语音）
            if not self.audio_handler.is_playback_active():
                self.audio_handler.start_playback()
            
            # 开始录音并设置回调
            def audio_callback(pcm_data):
                # 编码语音数据
                g711_data = self.voice_processor.encode_voice(pcm_data)
                
                # 发送语音数据
                if g711_data:
                    self.send_voice_data(g711_data)
            
            self.audio_handler.start_recording(audio_callback)
            
            self.logger.info("语音传输已启动")
            return True
            
        except Exception as e:
            self.logger.error(f"启动语音传输失败: {e}")
            return False
    
    def stop_voice_transmission(self):
        """停止语音传输"""
        try:
            if self.audio_handler:
                self.audio_handler.stop_recording()
                # 保持播放开启以接收其他设备的语音
            
            self.logger.info("语音传输已停止")
            
        except Exception as e:
            self.logger.error(f"停止语音传输失败: {e}")
    
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息"""
        return {
            'callsign': self.device_config.callsign,
            'ssid': self.device_config.ssid,
            'cpuid': self.device_config.cpuid,
            'model': self.device_config.model,
            'online': self.is_connected,
            'status': self.device_status
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取客户端状态"""
        return {
            'connected': self.is_connected,
            'running': self.running,
            'device_info': self.get_device_info(),
            'audio_active': self.audio_handler.is_recording_active() if self.audio_handler else False,
            'server': f"{self.server_config.host}:{self.server_config.port}" if self.server_config else None
        }
    
    def _update_status(self, key: str, value: Any):
        """更新状态并调用回调"""
        if self.status_callback:
            try:
                self.status_callback(key, value)
            except Exception as e:
                self.logger.error(f"状态回调错误: {e}")
    
    def set_message_callback(self, callback: Callable[[Dict], None]):
        """设置消息回调"""
        self.message_callback = callback
    
    def set_voice_callback(self, callback: Callable[[bytes], None]):
        """设置语音回调"""
        self.voice_callback = callback
    
    def set_status_callback(self, callback: Callable[[str, Any], None]):
        """设置状态回调"""
        self.status_callback = callback
    
    def enable_debug_force_decode(self, enable: bool = True):
        """启用/禁用调试模式：强制解码空包
        
        Args:
            enable: True 启用调试模式，False 禁用
        """
        self.debug_force_decode = enable
        status = "已启用" if enable else "已禁用"
        self.logger.info(f"调试模式强制解码空包 {status}")
    
    def close(self):
        """关闭客户端"""
        self.logger.info("正在关闭NRL客户端...")
        
        # 停止语音传输
        self.stop_voice_transmission()
        
        # 停止播放
        if self.audio_handler:
            self.audio_handler.stop_playback()
        
        # 断开连接
        self.disconnect()
        
        # 关闭音频
        if self.audio_handler:
            self.audio_handler.close()
        
        self.logger.info("NRL客户端已关闭")
    
    def get_servers_list(self) -> list[ServerInfo]:
        """获取服务器列表"""
        return self.servers_list.copy()
    
    def get_current_server_info(self) -> Optional[ServerInfo]:
        """获取当前服务器信息"""
        if 0 <= self.current_server_index < len(self.servers_list):
            return self.servers_list[self.current_server_index]
        return None
    
    def switch_server(self, server_index: int) -> bool:
        """切换服务器
        
        Args:
            server_index: 服务器索引
            
        Returns:
            True: 切换成功，False: 切换失败
        """
        try:
            if not (0 <= server_index < len(self.servers_list)):
                self.logger.error(f"无效的服务器索引: {server_index}")
                return False
            
            # 如果正在连接，先断开
            was_connected = self.is_connected
            if was_connected:
                self.logger.info("正在断开当前连接...")
                self.disconnect()
                time.sleep(0.5)  # 等待断开完成
            
            # 切换服务器
            old_server = self.servers_list[self.current_server_index]
            self.current_server_index = server_index
            new_server = self.servers_list[self.current_server_index]
            
            # 更新服务器配置
            self.server_config.host = new_server.host
            self.server_config.port = new_server.port
            
            self.logger.info(f"服务器已切换: {old_server.name} -> {new_server.name}")
            self.logger.info(f"新服务器地址: {new_server.host}:{new_server.port}")
            
            # 如果之前是连接状态，尝试重新连接
            if was_connected:
                self.logger.info("正在重新连接新服务器...")
                return self.connect()
            
            return True
            
        except Exception as e:
            self.logger.error(f"切换服务器失败: {e}")
            return False