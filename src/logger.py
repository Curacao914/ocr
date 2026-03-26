import logging
import sys
from datetime import datetime
from pathlib import Path
from src.config import LOG_LEVEL, TEMP_DIR

# 创建日志目录
LOG_DIR = TEMP_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = LOG_DIR / f"ocr_{datetime.now().strftime('%Y%m%d')}.log"

# 创建logger
logger = logging.getLogger('OCR_Tool')
logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

# 创建格式化器
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 文件处理器
try:
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"无法创建日志文件: {e}")

def get_logger():
    return logger
