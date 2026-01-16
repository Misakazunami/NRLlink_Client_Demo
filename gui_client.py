"""
NRL客户端GUI界面
提供图形化界面操作客户端
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import logging
from typing import Dict, Any

from nrl_client import NRLClient

class NRLGUIClient:
    """NRL客户端GUI类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NRL客户端 - 无线电网络互联")
        self.root.geometry("800x600")
        
        # 客户端
        self.client = None
        
        # UI组件
        self.main_frame = None
        self.status_frame = None
        self.control_frame = None
        self.log_frame = None
        self.audio_frame = None
        
        # 状态变量
        self.connection_status = tk.StringVar(value="未连接")
        self.device_info = tk.StringVar(value="设备信息")
        self.audio_level = tk.DoubleVar(value=0.0)
        self.ptt_active = tk.BooleanVar(value=False)
        
        # 日志
        self.setup_logging()
        
        # 初始化UI
        self.setup_ui()
        
        # 定时器
        self.update_timer = None
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 创建日志处理器用于GUI显示
        self.log_handler = GUILogHandler(self.log_message)
        self.log_handler.setLevel(logging.INFO)
        
        # 获取根日志记录器
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
    
    def setup_ui(self):
        """设置UI界面"""
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        
        # 状态栏
        self.create_status_frame()
        
        # 控制面板
        self.create_control_frame()
        
        # 音频控制
        self.create_audio_frame()
        
        # 日志区域
        self.create_log_frame()
        
        # 菜单
        self.create_menu()
    
    def create_status_frame(self):
        """创建状态栏"""
        self.status_frame = ttk.LabelFrame(self.main_frame, text="状态", padding="5")
        self.status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 连接状态
        ttk.Label(self.status_frame, text="连接状态:").grid(row=0, column=0, sticky=tk.W)
        status_label = ttk.Label(self.status_frame, textvariable=self.connection_status, 
                               font=('Arial', 10, 'bold'))
        status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        # 设备信息
        ttk.Label(self.status_frame, text="设备信息:").grid(row=0, column=2, sticky=tk.W)
        device_label = ttk.Label(self.status_frame, textvariable=self.device_info)
        device_label.grid(row=0, column=3, sticky=tk.W, padx=(5, 20))
        
        # 音频级别
        ttk.Label(self.status_frame, text="音频级别:").grid(row=0, column=4, sticky=tk.W)
        self.audio_level_bar = ttk.Progressbar(self.status_frame, variable=self.audio_level, 
                                             maximum=1.0, length=100)
        self.audio_level_bar.grid(row=0, column=5, sticky=tk.W, padx=(5, 0))
    
    def create_control_frame(self):
        """创建控制面板"""
        self.control_frame = ttk.LabelFrame(self.main_frame, text="控制", padding="5")
        self.control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 连接控制
        self.connect_button = ttk.Button(self.control_frame, text="连接", 
                                       command=self.connect_to_server)
        self.connect_button.grid(row=0, column=0, padx=(0, 10))
        
        self.disconnect_button = ttk.Button(self.control_frame, text="断开", 
                                            command=self.disconnect_from_server,
                                            state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=1, padx=(0, 10))
        
        # 设备配置
        ttk.Button(self.control_frame, text="设备配置", 
                  command=self.show_device_config).grid(row=0, column=2, padx=(0, 10))
        
        # 测试功能
        ttk.Button(self.control_frame, text="测试音频设备", 
                  command=self.test_audio_devices).grid(row=0, column=3, padx=(0, 10))
        
        # 发送文本消息
        ttk.Label(self.control_frame, text="消息:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.message_entry = ttk.Entry(self.control_frame, width=40)
        self.message_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.send_message_button = ttk.Button(self.control_frame, text="发送", 
                                            command=self.send_text_message,
                                            state=tk.DISABLED)
        self.send_message_button.grid(row=1, column=3, padx=(10, 0), pady=(10, 0))
    
    def create_audio_frame(self):
        """创建音频控制面板"""
        self.audio_frame = ttk.LabelFrame(self.main_frame, text="音频控制", padding="5")
        self.audio_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 设备选择区域
        device_frame = ttk.Frame(self.audio_frame)
        device_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 输入设备选择
        ttk.Label(device_frame, text="输入设备:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.input_device_var = tk.StringVar()
        self.input_device_combo = ttk.Combobox(device_frame, textvariable=self.input_device_var,
                                             state="readonly", width=30)
        self.input_device_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        self.input_device_combo.bind('<<ComboboxSelected>>', self.on_input_device_changed)
        
        # 输出设备选择
        ttk.Label(device_frame, text="输出设备:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.output_device_var = tk.StringVar()
        self.output_device_combo = ttk.Combobox(device_frame, textvariable=self.output_device_var,
                                              state="readonly", width=30)
        self.output_device_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 15))
        self.output_device_combo.bind('<<ComboboxSelected>>', self.on_output_device_changed)
        
        # 刷新设备按钮
        ttk.Button(device_frame, text="刷新设备", 
                  command=self.refresh_audio_devices).grid(row=0, column=4, padx=(10, 0))
        
        # PTT按钮
        self.ptt_button = ttk.Button(self.audio_frame, text="按住说话 (PTT)", 
                                   command=self.toggle_ptt,
                                   style="PTT.TButton")
        self.ptt_button.grid(row=1, column=0, padx=(0, 10))
        
        # PTT状态指示
        self.ptt_status_label = ttk.Label(self.audio_frame, text="PTT: 未激活", 
                                        font=('Arial', 10, 'bold'))
        self.ptt_status_label.grid(row=1, column=1, padx=(0, 20))
        
        # 音频控制按钮
        ttk.Button(self.audio_frame, text="开始播放", 
                  command=self.start_playback).grid(row=1, column=2, padx=(0, 10))
        
        ttk.Button(self.audio_frame, text="停止播放", 
                  command=self.stop_playback).grid(row=1, column=3, padx=(0, 10))
        
        # 音频级别显示
        ttk.Label(self.audio_frame, text="录音级别:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.record_level_bar = ttk.Progressbar(self.audio_frame, maximum=1.0, length=200)
        self.record_level_bar.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_log_frame(self):
        """创建日志区域"""
        self.log_frame = ttk.LabelFrame(self.main_frame, text="日志", padding="5")
        self.log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置日志文本框的滚动
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        
        # 日志级别控制
        log_control_frame = ttk.Frame(self.log_frame)
        log_control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(log_control_frame, text="日志级别:").grid(row=0, column=0, sticky=tk.W)
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(log_control_frame, textvariable=self.log_level_var,
                                       values=["DEBUG", "INFO", "WARNING", "ERROR"],
                                       state="readonly", width=10)
        log_level_combo.grid(row=0, column=1, padx=(5, 0))
        log_level_combo.bind('<<ComboboxSelected>>', self.on_log_level_changed)
        
        ttk.Button(log_control_frame, text="清空日志", 
                  command=self.clear_log).grid(row=0, column=2, padx=(20, 0))
    
    def create_menu(self):
        """创建菜单"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建配置", command=self.new_config)
        file_menu.add_command(label="加载配置", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="音频设备测试", command=self.test_audio_devices)
        tools_menu.add_command(label="网络测试", command=self.test_network)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def log_message(self, message: str):
        """记录消息到日志区域"""
        if self.log_text:
            self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
            self.log_text.see(tk.END)
    
    def connect_to_server(self):
        """连接到服务器"""
        try:
            if not self.client:
                self.client = NRLClient()
                
                # 设置回调
                self.client.set_message_callback(self.on_message_received)
                self.client.set_voice_callback(self.on_voice_received)
                self.client.set_status_callback(self.on_status_changed)
            
            if self.client.connect():
                self.connection_status.set("已连接")
                self.connect_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.NORMAL)
                self.send_message_button.config(state=tk.NORMAL)
                
                # 开始状态更新
                self.start_status_update()
                
                self.log_message("连接到服务器成功")
            else:
                messagebox.showerror("连接失败", "无法连接到服务器")
                
        except Exception as e:
            messagebox.showerror("连接错误", f"连接失败: {str(e)}")
            self.log_message(f"连接错误: {str(e)}")
    
    def disconnect_from_server(self):
        """断开服务器连接"""
        try:
            if self.client:
                self.client.disconnect()
                self.client = None
            
            self.connection_status.set("未连接")
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.send_message_button.config(state=tk.DISABLED)
            
            # 停止状态更新
            self.stop_status_update()
            
            self.log_message("已断开服务器连接")
            
        except Exception as e:
            messagebox.showerror("断开错误", f"断开连接失败: {str(e)}")
    
    def toggle_ptt(self):
        """切换PTT状态"""
        if not self.client:
            messagebox.showwarning("未连接", "请先连接到服务器")
            return
        
        if not self.ptt_active.get():
            # 开始语音传输
            if self.client.start_voice_transmission():
                self.ptt_active.set(True)
                self.ptt_status_label.config(text="PTT: 激活", foreground="red")
                self.log_message("PTT激活 - 开始语音传输")
        else:
            # 停止语音传输
            self.client.stop_voice_transmission()
            self.ptt_active.set(False)
            self.ptt_status_label.config(text="PTT: 未激活", foreground="black")
            self.log_message("PTT释放 - 停止语音传输")
    
    def start_playback(self):
        """开始播放"""
        if self.client and self.client.audio_handler:
            try:
                self.client.audio_handler.start_playback()
                self.log_message("开始播放")
            except Exception as e:
                messagebox.showerror("播放错误", f"开始播放失败: {str(e)}")
    
    def stop_playback(self):
        """停止播放"""
        if self.client and self.client.audio_handler:
            try:
                self.client.audio_handler.stop_playback()
                self.log_message("停止播放")
            except Exception as e:
                messagebox.showerror("播放错误", f"停止播放失败: {str(e)}")
    
    def send_text_message(self):
        """发送文本消息"""
        if not self.client:
            messagebox.showwarning("未连接", "请先连接到服务器")
            return
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        try:
            if self.client.send_text_message(message):
                self.log_message(f"发送消息: {message}")
                self.message_entry.delete(0, tk.END)
            else:
                messagebox.showerror("发送失败", "发送消息失败")
        except Exception as e:
            messagebox.showerror("发送错误", f"发送消息失败: {str(e)}")
    
    def on_message_received(self, message: Dict):
        """消息接收回调"""
        self.log_message(f"收到消息 [{message.get('from', '未知')}] {message.get('data', '')}")
    
    def on_voice_received(self, voice_data: bytes):
        """语音接收回调"""
        self.log_message(f"收到语音数据: {len(voice_data)} bytes")
    
    def on_status_changed(self, key: str, value: Any):
        """状态变化回调"""
        if key == 'connected':
            status = "已连接" if value else "未连接"
            self.connection_status.set(status)
            
            # 连接成功后刷新音频设备列表
            if value and self.client and self.client.audio_handler:
                try:
                    self.refresh_audio_devices()
                except Exception as e:
                    self.log_message(f"刷新音频设备失败: {str(e)}")
    
    def start_status_update(self):
        """开始状态更新"""
        def update_status():
            if self.client:
                try:
                    status = self.client.get_status()
                    device_info = status.get('device_info', {})
                    
                    # 更新设备信息
                    callsign = device_info.get('callsign', '未知')
                    ssid = device_info.get('ssid', 0)
                    self.device_info.set(f"{callsign}-{ssid}")
                    
                    # 更新音频级别
                    if self.client.audio_handler:
                        # 这里可以添加实际的音频级别检测
                        pass
                    
                except Exception as e:
                    self.log_message(f"状态更新错误: {str(e)}")
            
            # 继续定时更新
            if self.client:
                self.update_timer = self.root.after(1000, update_status)
        
        update_status()
    
    def stop_status_update(self):
        """停止状态更新"""
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
    
    def refresh_audio_devices(self):
        """刷新音频设备列表"""
        if not self.client or not self.client.audio_handler:
            messagebox.showwarning("未初始化", "音频处理器未初始化")
            return
        
        try:
            # 获取输入设备
            input_devices = self.client.audio_handler.get_input_devices()
            input_device_names = [f"{device['index']}: {device['name']}" for device in input_devices]
            
            # 获取输出设备
            output_devices = self.client.audio_handler.get_output_devices()
            output_device_names = [f"{device['index']}: {device['name']}" for device in output_devices]
            
            # 更新下拉列表
            self.input_device_combo['values'] = input_device_names
            self.output_device_combo['values'] = output_device_names
            
            # 设置默认值或当前选择
            current_input = self.client.audio_handler.get_current_input_device()
            current_output = self.client.audio_handler.get_current_output_device()
            
            if current_input:
                current_input_name = f"{current_input['index']}: {current_input['name']}"
                if current_input_name in input_device_names:
                    self.input_device_var.set(current_input_name)
            elif input_device_names:
                self.input_device_var.set(input_device_names[0])
            
            if current_output:
                current_output_name = f"{current_output['index']}: {current_output['name']}"
                if current_output_name in output_device_names:
                    self.output_device_var.set(current_output_name)
            elif output_device_names:
                self.output_device_var.set(output_device_names[0])
            
            self.log_message(f"音频设备列表已刷新 - 输入设备: {len(input_devices)}, 输出设备: {len(output_devices)}")
            
        except Exception as e:
            messagebox.showerror("刷新失败", f"刷新音频设备列表失败: {str(e)}")
    
    def on_input_device_changed(self, event):
        """输入设备选择改变"""
        if not self.client or not self.client.audio_handler:
            return
        
        selected = self.input_device_var.get()
        if selected:
            try:
                device_index = int(selected.split(':')[0])
                if self.client.audio_handler.set_input_device(device_index):
                    self.log_message(f"输入设备已更改为: {selected}")
                else:
                    messagebox.showerror("设置失败", "设置输入设备失败")
            except Exception as e:
                messagebox.showerror("设置错误", f"设置输入设备失败: {str(e)}")
    
    def on_output_device_changed(self, event):
        """输出设备选择改变"""
        if not self.client or not self.client.audio_handler:
            return
        
        selected = self.output_device_var.get()
        if selected:
            try:
                device_index = int(selected.split(':')[0])
                if self.client.audio_handler.set_output_device(device_index):
                    self.log_message(f"输出设备已更改为: {selected}")
                else:
                    messagebox.showerror("设置失败", "设置输出设备失败")
            except Exception as e:
                messagebox.showerror("设置错误", f"设置输出设备失败: {str(e)}")
    
    def test_audio_devices(self):
        """测试音频设备"""
        if self.client and self.client.audio_handler:
            try:
                self.log_message("开始测试音频设备...")
                self.client.audio_handler.test_audio_devices()
                self.log_message("音频设备测试完成")
            except Exception as e:
                messagebox.showerror("测试错误", f"音频设备测试失败: {str(e)}")
        else:
            messagebox.showwarning("未初始化", "音频处理器未初始化")
    
    def test_network(self):
        """网络测试"""
        if self.client:
            try:
                self.log_message("开始网络测试...")
                result = self.client.send_heartbeat()
                if result:
                    self.log_message("网络测试成功")
                else:
                    self.log_message("网络测试失败")
            except Exception as e:
                self.log_message(f"网络测试错误: {str(e)}")
        else:
            messagebox.showwarning("未连接", "请先连接到服务器")
    
    def show_device_config(self):
        """显示设备配置"""
        if not self.client:
            messagebox.showwarning("未连接", "请先连接到服务器")
            return
        
        device_info = self.client.get_device_info()
        config_text = f"""
设备配置信息:
呼号: {device_info.get('callsign', '未知')}
SSID: {device_info.get('ssid', '未知')}
CPUID: {device_info.get('cpuid', '未知')}
型号: {device_info.get('model', '未知')}
在线状态: {'在线' if device_info.get('online') else '离线'}
        """
        
        messagebox.showinfo("设备配置", config_text.strip())
    
    def new_config(self):
        """新建配置"""
        messagebox.showinfo("提示", "新建配置功能开发中...")
    
    def load_config(self):
        """加载配置"""
        messagebox.showinfo("提示", "加载配置功能开发中...")
    
    def on_log_level_changed(self, event):
        """日志级别改变"""
        level = self.log_level_var.get()
        logging.getLogger().setLevel(getattr(logging, level))
        self.log_message(f"日志级别已更改为: {level}")
    
    def clear_log(self):
        """清空日志"""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
NRL客户端 Demo
版本: Beta 1.2

基于nrllink项目开发的Python客户端
支持功能:
- 设备上线注册
- 语音通信 (G.711编解码)
- 文本消息
- 心跳维持
- 音频设备管理

作者: BH6ERO
        """
        messagebox.showinfo("关于", about_text.strip())
    
    def on_closing(self):
        """窗口关闭处理"""
        if self.client:
            self.client.close()
        
        self.root.destroy()
    
    def run(self):
        """运行GUI应用"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 设置PTT按钮样式
        style = ttk.Style()
        style.configure("PTT.TButton", font=('Arial', 12, 'bold'))
        
        self.log_message("NRL客户端已启动")
        self.log_message("请先连接到服务器开始使用")
        
        self.root.mainloop()


class GUILogHandler(logging.Handler):
    """GUI日志处理器"""
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    
    def emit(self, record):
        """发送日志记录"""
        try:
            msg = self.format(record)
            if self.callback:
                # 使用线程安全的方式调用
                self.callback(msg)
        except Exception:
            self.handleError(record)


def main():
    """主函数"""
    app = NRLGUIClient()
    app.run()


if __name__ == "__main__":
    main()