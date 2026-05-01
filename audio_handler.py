"""
音频处理模块
处理麦克风输入和扬声器输出，以及G.711编解码
"""
import threading # 用于线程安全
import numpy as np #type:ignore
import logging
import time
import pyaudio #type:ignore
from typing import Optional, Callable, Dict
from collections import deque
from nrl_protocol import G711Codec

class AudioHandler:
    """音频处理类"""
    
    def __init__(self, sample_rate: int = 8000, channels: int = 1, 
                 chunk_size: int = 1024, format_str: str = "paInt16"):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = self._get_format(format_str)
        self.format_str = format_str
        
        self.pyaudio = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        
        # 设备选择
        self.input_device_index = None  # 输入设备索引
        self.output_device_index = None  # 输出设备索引
        
        # 音频回调函数
        self.audio_callback: Optional[Callable[[bytes], None]] = None
        
        # 录音状态
        self.is_recording = False
        self.is_playing = False
        
        # 线程安全
        self.lock = threading.Lock()
        
        # 日志
        self.logger = logging.getLogger(__name__)
        
        # 音频缓冲区
        self.record_buffer = []
        self.play_buffer = deque()  # 播放缓冲区，使用deque提高性能
        
        # 语音数据缓存（用于累积到500字节）
        self.voice_data_cache = bytearray()
        self.voice_cache_lock = threading.Lock()
        self.last_voice_send_time = 0.0
        
        # 网络抖动缓冲
        self.jitter_buffer_size = 3  # 缓冲3个数据包（约60ms）
        self.jitter_buffer = deque(maxlen=self.jitter_buffer_size)
        self.jitter_buffer_lock = threading.Lock()
        
        # 播放停止标志 - 用于避免超时检查线程与播放回调的死锁
        self.playback_stop_flag = False
        
    def _get_format(self, format_str: str) -> int:
        """获取PyAudio格式"""
        format_map = {
            "paInt16": pyaudio.paInt16,
            "paInt32": pyaudio.paInt32,
            "paFloat32": pyaudio.paFloat32,
        }
        return format_map.get(format_str, pyaudio.paInt16)
    
    def list_audio_devices(self):
        """
        列出所有音频设备
        这个方法会列出所有音频设备，包括输入设备和输出设备。
        每个设备会包含以下信息：
        - 索引 (index)
        - 名称 (name)
        - 最大输入通道数 (max_input_channels)
        - 最大输出通道数 (max_output_channels)
        - 默认采样率 (default_sample_rate)
        """
        device_count = self.pyaudio.get_device_count()
        devices = []
        
        for i in range(device_count):
            device_info = self.pyaudio.get_device_info_by_index(i)
            devices.append({
                'index': i,
                'name': device_info['name'],
                'max_input_channels': device_info['maxInputChannels'],
                'max_output_channels': device_info['maxOutputChannels'],
                'default_sample_rate': device_info['defaultSampleRate']
            })
            print(f"设备 {i}: {device_info['name']}")
            print(f"  输入通道: {device_info['maxInputChannels']}")
            print(f"  输出通道: {device_info['maxOutputChannels']}")
            print(f"  默认采样率: {device_info['defaultSampleRate']}")
            print()
        
        return devices
    
    def get_input_devices(self):
        """获取所有可用的输入设备"""
        devices = []
        device_count = self.pyaudio.get_device_count()
        
        for i in range(device_count):
            device_info = self.pyaudio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
                })
        
        return devices
    
    def get_output_devices(self):
        """获取所有可用的输出设备"""
        devices = []
        device_count = self.pyaudio.get_device_count()
        
        for i in range(device_count):
            device_info = self.pyaudio.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxOutputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
                })
        
        return devices
    
    def set_input_device(self, device_index: int):
        """设置输入设备"""
        try:
            device_info = self.pyaudio.get_device_info_by_index(device_index)
            if device_info['maxInputChannels'] == 0:
                raise ValueError(f"设备 {device_index} 不支持输入")
            
            self.input_device_index = device_index
            self.logger.info(f"输入设备已设置为: {device_info['name']}")
            return True
        except Exception as e:
            self.logger.error(f"设置输入设备失败: {e}")
            return False
    
    def set_output_device(self, device_index: int):
        """设置输出设备"""
        try:
            device_info = self.pyaudio.get_device_info_by_index(device_index)
            if device_info['maxOutputChannels'] == 0:
                raise ValueError(f"设备 {device_index} 不支持输出")
            
            self.output_device_index = device_index
            self.logger.info(f"输出设备已设置为: {device_info['name']}")
            return True
        except Exception as e:
            self.logger.error(f"设置输出设备失败: {e}")
            return False
    
    def get_current_input_device(self):
        """获取当前输入设备信息"""
        if self.input_device_index is not None:
            try:
                device_info = self.pyaudio.get_device_info_by_index(self.input_device_index)
                return {
                    'index': self.input_device_index,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
                }
            except Exception as e:
                self.logger.error(f"获取输入设备信息失败: {e}")
        return None
    
    def get_current_output_device(self):
        """获取当前输出设备信息"""
        if self.output_device_index is not None:
            try:
                device_info = self.pyaudio.get_device_info_by_index(self.output_device_index)
                return {
                    'index': self.output_device_index,
                    'name': device_info['name'],
                    'channels': device_info['maxOutputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
                }
            except Exception as e:
                self.logger.error(f"获取输出设备信息失败: {e}")
        return None
    
    def start_recording(self, callback: Optional[Callable[[bytes], None]] = None):
        """开始录音"""
        with self.lock:
            if self.is_recording:
                self.logger.warning("已经在录音中")
                return
            
            try:
                self.audio_callback = callback
                self.is_recording = True
                self.record_buffer = []
                
                # 设置输入设备参数
                input_params = {
                    'format': self.format,
                    'channels': self.channels,
                    'rate': self.sample_rate,
                    'input': True,
                    'frames_per_buffer': self.chunk_size,
                    'stream_callback': self._record_callback
                }
                
                # 如果有指定输入设备，使用指定设备
                if self.input_device_index is not None:
                    input_params['input_device_index'] = self.input_device_index
                    device_info = self.get_current_input_device()
                    device_name = device_info['name'] if device_info else f"设备{self.input_device_index}"
                    self.logger.info(f"使用输入设备: {device_name}")
                else:
                    self.logger.info("使用系统默认输入设备")
                
                self.input_stream = self.pyaudio.open(**input_params)
                
                self.input_stream.start_stream()
                self.logger.info("开始录音")
                
            except Exception as e:
                self.logger.error(f"开始录音失败: {e}")
                self.is_recording = False
                raise
    
    def stop_recording(self) -> bytes:
        """停止录音并返回录音数据"""
        with self.lock:
            if not self.is_recording:
                self.logger.warning("没有在录音")
                return b""
            
            try:
                self.is_recording = False
                
                # 清空语音数据缓存
                with self.voice_cache_lock:
                    self.voice_data_cache.clear()
                    self.last_voice_send_time = 0.0
                
                if self.input_stream:
                    self.input_stream.stop_stream()
                    self.input_stream.close()
                    self.input_stream = None
                
                # 合并录音数据
                recorded_data = b''.join(self.record_buffer)
                self.record_buffer = []
                
                self.logger.info("停止录音")
                return recorded_data
                
            except Exception as e:
                self.logger.error(f"停止录音失败: {e}")
                raise
    
    def start_playback(self):
        """开始播放"""
        with self.lock:
            if self.is_playing:
                self.logger.warning("已经在播放中")
                return
            
            try:
                self.is_playing = True
                self.playback_stop_flag = False  # 重置停止标志
                self.play_buffer = deque()  # 使用deque而非列表，支持高效的两端操作
                
                # 设置输出设备参数
                output_params = {
                    'format': self.format,
                    'channels': self.channels,
                    'rate': self.sample_rate,
                    'output': True,
                    'frames_per_buffer': self.chunk_size,
                    'stream_callback': self._play_callback
                }
                
                # 如果有指定输出设备，使用指定设备
                if self.output_device_index is not None:
                    output_params['output_device_index'] = self.output_device_index
                    device_info = self.get_current_output_device()
                    device_name = device_info['name'] if device_info else f"设备{self.output_device_index}"
                    self.logger.info(f"使用输出设备: {device_name}")
                else:
                    self.logger.info("使用系统默认输出设备")
                
                self.output_stream = self.pyaudio.open(**output_params)
                
                self.output_stream.start_stream()
                self.logger.info("开始播放")
                
            except Exception as e:
                self.logger.error(f"开始播放失败: {e}")
                self.is_playing = False
                raise
    
    def stop_playback(self):
        """停止播放"""
        with self.lock:
            if not self.is_playing:
                self.logger.warning("没有在播放")
                return
            
            try:
                self.is_playing = False
                self.playback_stop_flag = False  # 重置停止标志
                
                if self.output_stream:
                    self.output_stream.stop_stream()
                    self.output_stream.close()
                    self.output_stream = None
                
                self.play_buffer = deque()
                self.logger.info("停止播放")
                
            except Exception as e:
                self.logger.error(f"停止播放失败: {e}")
                raise
    
    def _record_callback(self, in_data, frame_count, time_info, status):
        """改进的录音回调函数
        这个函数是录音回调函数，用于处理麦克风输入数据。

        1. 严格按照1000字节PCM（=500字节G.711）管理缓冲区
        2. 避免不规则的填充导致的失真
        3. 确保每个语音包时间长度固定（62.5ms）
        4. 参考nrllink的音频处理逻辑
        
        时间关系：
        - 采样率: 8000 Hz
        - 每个样本: 2字节 (16位)
        - 1000字节PCM = 500个样本 = 62.5ms
        - 对应500字节G.711数据包
        """
        if not self.is_recording:
            return (None, pyaudio.paContinue)
        
        self.record_buffer.append(in_data)
        
        # 处理语音数据缓存 - 严格管理1000字节PCM
        with self.voice_cache_lock:
            self.voice_data_cache.extend(in_data)
            current_time = time.time()
            
            # 关键逻辑：当缓存达到或超过1000字节PCM时，立即发送
            # 1000字节PCM = 500字节G.711 = 62.5ms
            while len(self.voice_data_cache) >= 1000:
                # 提取恰好1000字节PCM
                send_data = bytes(self.voice_data_cache[:1000])
                self.voice_data_cache = self.voice_data_cache[1000:]
                self.last_voice_send_time = current_time
                
                # 如果有回调函数，发送1000字节PCM数据
                # 回调函数会将其编码为500字节G.711
                if self.audio_callback:
                    self.audio_callback(send_data)
                    self.logger.debug(f"发送音频数据: {len(send_data)} bytes PCM")
        
        return (None, pyaudio.paContinue)
    
    def _play_callback(self, in_data, frame_count, time_info, status):
        """播放回调函数 - 改进数据长度匹配和缓冲区管理"""
        # 检查停止标志，如果已标记停止则立即返回
        if not self.is_playing or self.playback_stop_flag:
            return (b'\x00' * frame_count * self.channels * 2, pyaudio.paContinue)
        
        # 计算期望的数据长度（16-bit音频，每个样本2字节）
        expected_length = frame_count * self.channels * 2
        
        # 从播放缓冲区获取数据
        data_chunks = []
        current_length = 0
        
        with self.lock:
            # 从缓冲区收集足够的数据
            while self.play_buffer and current_length < expected_length:
                try:
                    data_chunk = self.play_buffer.popleft()
                    if data_chunk:
                        data_chunks.append(data_chunk)
                        current_length += len(data_chunk)
                except (IndexError, AttributeError) as e:
                    # 缓冲区可能被修改或格式错误，记录但继续
                    self.logger.debug(f"播放缓冲获取异常: {e}")
                    break
        
        if data_chunks:
            # 合并所有数据块
            combined_data = b''.join(data_chunks)
            
            if len(combined_data) == expected_length:
                return (combined_data, pyaudio.paContinue)
            elif len(combined_data) > expected_length:
                # 数据过多，截断并放回多余部分
                result_data = combined_data[:expected_length]
                remaining_data = combined_data[expected_length:]
                if remaining_data:
                    with self.lock:
                        self.play_buffer.appendleft(remaining_data)
                return (result_data, pyaudio.paContinue)
            else:
                # 数据不足，用静音填充
                silence = b'\x00' * (expected_length - len(combined_data))
                return (combined_data + silence, pyaudio.paContinue)
        else:
            # 如果没有数据，播放静音
            return (b'\x00' * expected_length, pyaudio.paContinue)
    
    def add_playback_data(self, data: bytes):
        """添加播放数据到缓冲区 - 支持网络抖动缓冲"""
        if not self.is_playing or not data:
            return
        
        with self.jitter_buffer_lock:
            # 添加时间戳到数据包
            timestamped_data = (time.time(), data)
            self.jitter_buffer.append(timestamped_data)
            
            # 如果缓冲区已满，开始处理数据
            if len(self.jitter_buffer) >= self.jitter_buffer_size:
                self._process_jitter_buffer()
    
    def _process_jitter_buffer(self):
        """处理抖动缓冲区中的数据"""
        with self.jitter_buffer_lock:
            if not self.jitter_buffer:
                return
            
            # 按时间戳排序数据包
            sorted_packets = sorted(self.jitter_buffer, key=lambda x: x[0])
            
            # 将排序后的数据添加到播放缓冲区
            with self.lock:
                for timestamp, data in sorted_packets:
                    self.play_buffer.append(data)
            
            # 清空抖动缓冲区
            self.jitter_buffer.clear()
    
    def add_playback_data_immediate(self, data: bytes):
        """立即添加播放数据（绕过抖动缓冲）"""
        if not self.is_playing or not data:
            return
        
        with self.lock:
            self.play_buffer.append(data)
    
    def get_recorded_audio(self) -> bytes:
        """获取录音数据"""
        with self.lock:
            return b''.join(self.record_buffer)
    
    def clear_record_buffer(self):
        """清空录音缓冲区"""
        with self.lock:
            self.record_buffer = []
    
    def is_recording_active(self) -> bool:
        """检查是否正在录音"""
        with self.lock:
            return self.is_recording
    
    def is_playback_active(self) -> bool:
        """检查是否正在播放"""
        with self.lock:
            return self.is_playing
    
    def get_audio_level(self, data: bytes) -> float:
        """获取音频数据的最大音量级别 (0-1)"""
        if not data:
            return 0.0
        
        # 转换为numpy数组
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # 计算RMS值
        rms = np.sqrt(np.mean(audio_data**2))
        
        # 归一化到0-1范围
        max_value = np.iinfo(np.int16).max
        normalized_level = min(rms / max_value, 1.0)
        
        return normalized_level
    
    def test_audio_devices(self):
        """测试音频设备"""
        print("测试音频设备...")
        
        # 测试录音
        print("测试录音5秒...")
        try:
            self.start_recording()
            time.sleep(5)
            recorded_data = self.stop_recording()
            print(f"录音测试完成，录制了 {len(recorded_data)} 字节数据")
        except Exception as e:
            print(f"录音测试失败: {e}")
        
        # 测试播放
        if recorded_data:
            print("测试播放...")
            try:
                self.start_playback()
                self.add_playback_data(recorded_data)
                time.sleep(5)
                self.stop_playback()
                print("播放测试完成")
            except Exception as e:
                print(f"播放测试失败: {e}")
    
    def close(self):
        """关闭音频处理"""
        try:
            self.stop_recording()
            self.stop_playback()
            
            if self.pyaudio:
                self.pyaudio.terminate()
                
            self.logger.info("音频处理已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭音频处理失败: {e}")


class VoiceProcessor:
    """语音处理器，处理G.711编解码
    
    参考nrllink的G.711实现，提供编解码功能
    支持错误恢复和数据包丢失处理
    """
    
    def __init__(self):
        self.codec = G711Codec()
        self.logger = logging.getLogger(__name__)
        
        # 统计信息
        self.encode_count = 0
        self.decode_count = 0
        self.error_count = 0
    
    def encode_voice(self, pcm_data: bytes) -> bytes:
        """编码PCM语音数据为G.711
        
        参考nrllink的G.711编码，每个500字节的G.711帧对应1000字节的PCM数据
        """
        try:
            if not pcm_data:
                self.logger.warning("PCM数据为空，返回静音帧")
                return b'\x80' * 500  # G.711静音值
            
            # 编码PCM数据
            encoded = self.codec.encode(pcm_data)
            
            if not encoded or len(encoded) == 0:
                self.logger.warning(f"编码失败: 编码结果为空")
                return b'\x80' * 500  # 返回静音帧
            
            self.encode_count += 1
            self.logger.debug(f"语音编码: {len(pcm_data)} bytes PCM -> {len(encoded)} bytes G.711")
            return encoded
            
        except Exception as e:
            self.logger.error(f"语音编码异常: {e}")
            self.error_count += 1
            return b'\x80' * 500  # 返回静音帧作为错误处理
    
    def decode_voice(self, g711_data: bytes) -> bytes:
        """将G.711解码为PCM - 增强错误处理
        
        参考nrllink的G.711解码，每个500字节的G.711帧解码为1000字节的PCM数据
        """
        try:
            # 检查输入数据有效性
            if not g711_data:
                self.logger.warning("G.711数据为空，返回静音数据")
                return b'\x00' * 1000  # 返回静音数据（500样本 * 2字节）
            
            # 解码G.711数据
            pcm_data = self.codec.decode(g711_data)
            
            # 如果解码失败或返回空数据，提供静音数据
            if not pcm_data:
                self.logger.warning(f"G.711解码失败: 输入长度={len(g711_data)}")
                return b'\x00' * 1000  # 返回静音数据
            
            self.decode_count += 1
            self.logger.debug(f"语音解码: {len(g711_data)} bytes G.711 -> {len(pcm_data)} bytes PCM")
            return pcm_data
            
        except Exception as e:
            self.logger.error(f"G.711解码异常: {e}, 数据长度={len(g711_data) if g711_data else 0}")
            self.error_count += 1
            return b'\x00' * 1000  # 返回静音数据作为错误处理
    
    def process_recorded_audio(self, pcm_data: bytes) -> bytes:
        """处理录制的音频数据"""
        return self.encode_voice(pcm_data)
    
    def process_received_audio(self, g711_data: bytes) -> bytes:
        """处理接收的音频数据"""
        return self.decode_voice(g711_data)
    
    def get_stats(self) -> Dict[str, int]:
        """获取处理统计信息"""
        return {
            'encode_count': self.encode_count,
            'decode_count': self.decode_count,
            'error_count': self.error_count
        }