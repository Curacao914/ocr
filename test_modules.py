#!/usr/bin/env python3
"""
测试脚本 - 验证各个模块功能
"""

import sys
from pathlib import Path
import tempfile
from PIL import Image
import io

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.logger import get_logger
from src.file_processor import FileProcessor
from src.output_converter import OutputConverter
from src.config import TEMP_DIR

logger = get_logger()

def test_file_processor():
    """测试文件处理模块"""
    logger.info("\n" + "="*50)
    logger.info("测试文件处理模块")
    logger.info("="*50)
    
    # 创建测试图片
    logger.info("创建测试图片...")
    test_image_path = TEMP_DIR / "test_image.png"
    img = Image.new('RGB', (100, 100), color='red')
    img.save(test_image_path)
    logger.info(f"✓ 测试图片创建成功: {test_image_path}")
    
    # 测试文件验证
    logger.info("\n测试文件验证...")
    is_valid, message = FileProcessor.validate_file(test_image_path)
    logger.info(f"✓ 验证结果: {message}")
    
    # 测试base64编码
    logger.info("\n测试Base64编码...")
    base64_str = FileProcessor.get_file_base64(test_image_path)
    if base64_str:
        logger.info(f"✓ Base64编码成功，长度: {len(base64_str)}")
    else:
        logger.error("✗ Base64编码失败")
    
    # 清理
    test_image_path.unlink()
    logger.info("✓ 测试图片已删除")

def test_output_converter():
    """测试输出转换模块"""
    logger.info("\n" + "="*50)
    logger.info("测试输出转换模块")
    logger.info("="*50)
    
    # 测试Markdown保存
    logger.info("\n测试Markdown保存...")
    markdown_content = """
# 测试标题

这是一个测试的Markdown文件。

## 子标题

- 列表项1
- 列表项2
- 列表项3

### 代码块

```python
def hello():
    print("Hello World")
```

| 列 1 | 列 2 |
|------|------|
| 数据1 | 数据2 |
"""
    
    md_path = TEMP_DIR / "test_output.md"
    success = OutputConverter.save_markdown(markdown_content, md_path)
    if success:
        logger.info(f"✓ Markdown文件保存成功: {md_path}")
    else:
        logger.error("✗ Markdown文件保存失败")
    
    # 测试DOCX转换
    logger.info("\n测试DOCX转换...")
    docx_path = TEMP_DIR / "test_output.docx"
    success = OutputConverter.markdown_to_docx(markdown_content, docx_path)
    if success:
        logger.info(f"✓ DOCX文件转换成功: {docx_path}")
    else:
        logger.error("✗ DOCX文件转换失败")
    
    # 清理
    md_path.unlink(missing_ok=True)
    docx_path.unlink(missing_ok=True)
    logger.info("✓ 测试文件已删除")

def test_config():
    """测试配置模块"""
    logger.info("\n" + "="*50)
    logger.info("测试配置模块")
    logger.info("="*50)
    
    from src.config import (
        MAX_IMAGE_SIZE, MAX_PDF_SIZE, MAX_PDF_PAGES,
        TEMP_DIR, OUTPUT_DIR, SUPPORTED_FORMATS
    )
    
    logger.info(f"\n配置信息:")
    logger.info(f"  最大图片大小: {MAX_IMAGE_SIZE / 1024 / 1024:.1f}MB")
    logger.info(f"  最大PDF大小: {MAX_PDF_SIZE / 1024 / 1024:.1f}MB")
    logger.info(f"  最大PDF页数: {MAX_PDF_PAGES}")
    logger.info(f"  临时目录: {TEMP_DIR}")
    logger.info(f"  输出目录: {OUTPUT_DIR}")
    logger.info(f"  支持格式: {SUPPORTED_FORMATS}")
    logger.info("✓ 配置加载成功")

def main():
    """运行所有测试"""
    logger.info("="*50)
    logger.info("GLM-OCR 测试套件")
    logger.info("="*50)
    
    try:
        test_config()
        test_file_processor()
        test_output_converter()
        
        logger.info("\n" + "="*50)
        logger.info("✓ 所有测试完成")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"\n✗ 测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
