import os
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import gradio as gr
from datetime import datetime
from dotenv import set_key

from src.file_processor import FileProcessor
from src.ocr_client import GLMOCRClient, OCRResult
from src.output_converter import OutputConverter
from src.config import OUTPUT_DIR, TEMP_DIR
from src.logger import get_logger

logger = get_logger()

class OCRInterface:
    """OCR工具的Gradio界面"""
    
    def __init__(self):
        self.ocr_client: Optional[GLMOCRClient] = None
        self.current_results = []
        self.processing = False
        self.saved_api_key = (os.getenv("ZHIPU_API_KEY") or "").strip()

        if self.saved_api_key:
            try:
                self.ocr_client = GLMOCRClient(api_key=self.saved_api_key)
                logger.info("已自动加载并初始化已保存的API密钥")
            except Exception as e:
                logger.warning(f"已保存的API密钥初始化失败: {e}")

    @staticmethod
    def _persist_api_key(api_key: str) -> None:
        """云端环境使用 Secrets，跳过本地 .env 写入以防报错"""
        os.environ["ZHIPU_API_KEY"] = api_key
        try:
            project_root = Path(__file__).parent.parent
            env_path = project_root / ".env"
            set_key(str(env_path), "ZHIPU_API_KEY", api_key)
        except Exception:
            pass # 忽略云端只读环境下的写入报错

    # ---------------------------------------------------------
    # 注意：这里的剩余代码（_source_key_from_processed_name, 
    # initialize_client, process_files_stream, export_results, 
    # preview_result 等所有类方法）保持你原来写的逻辑完全不变！
    # 为了节省篇幅我不全部重复，请将你原来的方法保留在此处。
    # ---------------------------------------------------------

def create_interface():
    """创建Gradio界面"""
    interface = OCRInterface()
    
    with gr.Blocks(title="GLM-OCR", theme=gr.themes.Soft()) as demo:
        # ... 这里保留你原来所有的 UI 组件定义和事件绑定代码 ...
        pass # 请保留你原有的 create_interface 内部代码

    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
