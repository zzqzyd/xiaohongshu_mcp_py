import argparse
import os
from loguru import logger
from xiaohongshu_mcp_py.app_server import AppServer
from xiaohongshu_mcp_py.service import XiaohongshuService


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Xiaohongshu MCP Service')
    parser.add_argument('--headless', type=bool, default=True, help='是否使用无头模式')
    parser.add_argument('--bin', type=str, default='', help='浏览器二进制文件路径')
    args = parser.parse_args()
    
    # 初始化配置
    os.environ['HEADLESS_MODE'] = str(args.headless).lower()
    if args.bin:
        os.environ['BROWSER_BIN_PATH'] = args.bin
    
    # 初始化服务
    xiaohongshu_service = XiaohongshuService()
    
    # 创建并启动应用服务器
    app_server = AppServer(xiaohongshu_service)
    try:
        logger.info("正在启动小红书MCP服务，端口: 18060")
        app_server.start("0.0.0.0", 18060)
    except Exception as e:
        logger.error(f"启动服务器失败: {str(e)}")


if __name__ == '__main__':
    main()