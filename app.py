#!/usr/bin/env python3
"""
GLM-OCR 文档转换工具 - Hugging Face Spaces 入口
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主入口函数"""
    from src.logger import get_logger
    from src.gradio_interface import create_interface
    
    logger = get_logger()
    
    logger.info("=" * 50)
    logger.info("GLM-OCR 文档转换工具 - 云端部署版")
    logger.info("=" * 50)
    
    try:
        logger.info("启动Gradio界面...")
        demo = create_interface()
        # Hugging Face 会自动接管端口，直接 launch 即可，不需要填参数
        demo.launch()
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
