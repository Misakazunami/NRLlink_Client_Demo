"""
NRL客户端Demo

基于nrllink项目开发的Python客户端，实现基本的业余无线电网络互联功能

功能特性:
- 设备上线注册
- 语音通信 (G.711编解码)
- 文本消息
- 心跳维持
- 音频设备管理
- 图形化界面

使用方法:
1. 配置config.yaml文件
2. 运行 python main.py
3. 点击"连接"按钮连接到服务器
4. 使用PTT按钮进行语音通信
5. 发送文本消息

协议说明:
- 基于NRL2协议
- UDP端口60050
- 支持G.711 A-law语音编解码
- 心跳间隔30秒
"""

import sys
import os
import argparse
import logging

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def setup_logging(level=logging.INFO):
    """设置日志系统"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('nrl_client.log', encoding='utf-8')
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='NRL客户端Demo')
    parser.add_argument('--config', '-c', default='config.yaml',
                       help='配置文件路径 (默认: config.yaml)')
    parser.add_argument('--no-gui', action='store_true',
                       help='无GUI模式，使用命令行界面')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    parser.add_argument('--test-audio', action='store_true',
                       help='测试音频设备并退出')
    parser.add_argument('--list-audio', action='store_true',
                       help='列出音频设备并退出')
    parser.add_argument('--enable-cpuid-calc', action='store_true',
                       help='启用CPUID计算（默认关闭，直接使用配置文件中的CPUID）')
    
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    
    try:
        # 音频设备测试
        if args.test_audio or args.list_audio:
            from audio_handler import AudioHandler
            audio_handler = AudioHandler()
            
            if args.list_audio:
                print("音频设备列表:")
                devices = audio_handler.list_audio_devices()
            else:
                print("开始音频设备测试...")
                audio_handler.test_audio_devices()
            
            audio_handler.close()
            return
        
        # GUI模式
        if not args.no_gui:
            try:
                from gui_client import NRLGUIClient
                
                logger.info("启动NRL客户端 (GUI模式)")
                app = NRLGUIClient(enable_cpuid_calc=args.enable_cpuid_calc)
                app.run()
                
            except ImportError as e:
                logger.error(f"GUI组件导入失败: {e}")
                logger.info("尝试使用命令行模式...")
                args.no_gui = True
        
        # 命令行模式
        if args.no_gui:
            from nrl_client import NRLClient
            
            logger.info("启动NRL客户端 (命令行模式)")
            
            # 创建客户端
            client = NRLClient(args.config, enable_cpuid_calc=args.enable_cpuid_calc)
            
            # 简单的命令行界面
            print("\nNRL客户端命令行界面")
            print("可用命令:")
            print("  connect - 连接到服务器")
            print("  disconnect - 断开连接")
            print("  status - 查看状态")
            print("  send <消息> - 发送文本消息")
            print("  voice_start - 开始语音传输")
            print("  voice_stop - 停止语音传输")
            print("  quit - 退出")
            print()
            
            while True:
                try:
                    command = input("> ").strip().lower()
                    
                    if command == 'quit':
                        break
                    elif command == 'connect':
                        if client.connect():
                            print("连接成功")
                        else:
                            print("连接失败")
                    elif command == 'disconnect':
                        client.disconnect()
                        print("已断开连接")
                    elif command == 'status':
                        status = client.get_status()
                        print(f"状态: {status}")
                    elif command.startswith('send '):
                        message = command[5:]
                        if client.send_text_message(message):
                            print(f"发送消息: {message}")
                        else:
                            print("发送失败")
                    elif command == 'voice_start':
                        if client.start_voice_transmission():
                            print("语音传输已启动")
                        else:
                            print("启动语音传输失败")
                    elif command == 'voice_stop':
                        client.stop_voice_transmission()
                        print("语音传输已停止")
                    elif command == '':
                        continue
                    else:
                        print(f"未知命令: {command}")
                        
                except KeyboardInterrupt:
                    print("\n使用 'quit' 命令退出")
                except Exception as e:
                    logger.error(f"命令执行错误: {e}")
            
            # 关闭客户端
            client.close()
            logger.info("NRL客户端已关闭")
    
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()