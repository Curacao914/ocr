#!/usr/bin/env python3
"""
GLM-OCR 文档转换工具 - 主程序入口
"""

import sys
import os
import socket
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def _is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """检查端口是否可用。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def _select_server_port() -> int:
    """选择可用端口：优先环境变量，其次7860-7890。"""
    env_port = os.getenv("GRADIO_SERVER_PORT")
    if env_port and env_port.isdigit():
        port = int(env_port)
        if _is_port_available(port):
            return port

    for port in range(7860, 7891):
        if _is_port_available(port):
            return port

    raise RuntimeError("未找到可用端口（7860-7890）")


def _ensure_localhost_no_proxy() -> None:
    """确保 localhost 回环地址不走系统代理。"""
    required = ["localhost", "127.0.0.1", "::1"]

    existing = os.getenv("NO_PROXY") or os.getenv("no_proxy") or ""
    items = [item.strip() for item in existing.split(",") if item.strip()]

    for host in required:
        if host not in items:
            items.append(host)

    value = ",".join(items)
    os.environ["NO_PROXY"] = value
    os.environ["no_proxy"] = value

def main():
    """主入口函数"""
    from src.config import ZHIPU_API_KEY
    from src.logger import get_logger
    from src.gradio_interface import create_interface
    
    logger = get_logger()
    
    # 检查API密钥
    if not ZHIPU_API_KEY or ZHIPU_API_KEY == 'your_api_key_here':
        logger.warning("API密钥未配置或为默认值")
        logger.info("请在.env文件中配置ZHIPU_API_KEY")
    
    logger.info("=" * 50)
    logger.info("GLM-OCR 文档转换工具 v1.0.0")
    logger.info("=" * 50)
    _ensure_localhost_no_proxy()
    
    try:
        logger.info("启动Gradio界面...")
        demo = create_interface()
        server_port = _select_server_port()
        logger.info(f"使用端口: {server_port}")
        try:
            demo.launch(
                server_name="127.0.0.1",
                server_port=server_port,
                share=False,
                inbrowser=True,
                debug=False
            )
        except Exception as launch_error:
            if "localhost is not accessible" in str(launch_error):
                logger.warning("检测到 localhost 不可达，自动启用 share=True 重试")
                demo.launch(
                    server_name="127.0.0.1",
                    server_port=server_port,
                    share=True,
                    inbrowser=True,
                    debug=False
                )
            else:
                raise
    except KeyboardInterrupt:
        logger.info("程序已停止")
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
