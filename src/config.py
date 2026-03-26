import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# API配置
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '')
API_BASE_URL = 'https://open.bigmodel.cn/api'

# 文件处理配置
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_PDF_SIZE = 50 * 1024 * 1024    # 50MB
MAX_PDF_PAGES = 100
# PDF内部页面尺寸单位为point（1/72英寸），A4约为595x842 point
MAX_PDF_PAGE_WIDTH = 595
MAX_PDF_PAGE_HEIGHT = 842

# 目录配置
TEMP_DIR = Path(os.getenv('TEMP_DIR', './temp'))
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', './output'))

# 确保目录存在
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# 支持的文件类型
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png'}
SUPPORTED_PDF_FORMAT = {'.pdf'}
SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS | SUPPORTED_PDF_FORMAT

# Gradio配置
GRADIO_SHARE = False
GRADIO_DEBUG = False
