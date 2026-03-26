import os
import base64
from pathlib import Path
from typing import List, Tuple, Optional
import logging

from PIL import Image
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter, Transformation
from pdf2image import convert_from_path

from src.config import (
    MAX_IMAGE_SIZE, MAX_PDF_SIZE, MAX_PDF_PAGES,
    MAX_PDF_PAGE_WIDTH, MAX_PDF_PAGE_HEIGHT,
    SUPPORTED_FORMATS, TEMP_DIR
)
from src.logger import get_logger

logger = get_logger()

class FileProcessor:
    """文件预处理类"""
    
    @staticmethod
    def validate_file(file_path: Path) -> Tuple[bool, str]:
        """验证文件是否有效"""
        if not file_path.exists():
            return False, f"文件不存在: {file_path}"
        
        # 检查文件扩展名
        if file_path.suffix.lower() not in SUPPORTED_FORMATS:
            return False, f"不支持的文件格式: {file_path.suffix}"
        
        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_path.suffix.lower() != '.pdf':
            max_size = MAX_IMAGE_SIZE
            size_limit = "10MB"

            if file_size > max_size:
                return False, f"文件过大: {file_path.name} ({file_size / 1024 / 1024:.2f}MB, 限制: {size_limit})"

        # PDF 即使超出 50MB/100页，也先进入预处理拆分流程，不在这里直接拒绝
        
        return True, "验证通过"
    
    @staticmethod
    def get_pdf_page_count(file_path: Path) -> int:
        """获取PDF页数"""
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            logger.error(f"无法读取PDF页数: {e}")
            return 0
    
    @staticmethod
    def split_pdf(file_path: Path, output_dir: Path) -> List[Path]:
        """
        拆分PDF文件
        如果PDF超过100页或50MB，拆分为多个文件。
        目标：在满足页数和体积约束的前提下，尽量使用最少分片。
        """
        logger.info(f"检查PDF页数: {file_path.name}")

        page_count = FileProcessor.get_pdf_page_count(file_path)
        file_size = file_path.stat().st_size
        logger.info(f"PDF总页数: {page_count}")
        logger.info(f"PDF大小: {file_size / 1024 / 1024:.2f}MB")

        if page_count <= MAX_PDF_PAGES and file_size <= MAX_PDF_SIZE:
            return [file_path]

        logger.info(f"PDF超过限制（页数>{MAX_PDF_PAGES} 或 大小>{MAX_PDF_SIZE / 1024 / 1024:.0f}MB），进行最少拆分...")
        
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)

                min_by_pages = max(1, (page_count + MAX_PDF_PAGES - 1) // MAX_PDF_PAGES)
                min_by_size = max(1, (file_size + MAX_PDF_SIZE - 1) // MAX_PDF_SIZE)
                num_splits = max(min_by_pages, min_by_size)

                while num_splits <= page_count:
                    output_files: List[Path] = []

                    # 尽量均匀分配页数，同时保证每片不超过100页
                    base = page_count // num_splits
                    extra = page_count % num_splits
                    start_page = 0
                    valid = True

                    for i in range(num_splits):
                        pages_this_part = base + (1 if i < extra else 0)
                        if pages_this_part <= 0 or pages_this_part > MAX_PDF_PAGES:
                            valid = False
                            break

                        end_page = start_page + pages_this_part

                        writer = PdfWriter()
                        for page_num in range(start_page, end_page):
                            writer.add_page(reader.pages[page_num])

                        output_file = output_dir / f"{file_path.stem}_part{i+1}.pdf"
                        with open(output_file, 'wb') as out_f:
                            writer.write(out_f)

                        output_files.append(output_file)
                        start_page = end_page

                    # 校验每个分片是否满足页数/体积限制
                    if valid:
                        for split_file in output_files:
                            split_pages = FileProcessor.get_pdf_page_count(split_file)
                            split_size = split_file.stat().st_size
                            if split_pages > MAX_PDF_PAGES or split_size > MAX_PDF_SIZE:
                                valid = False
                                break

                    if valid and output_files:
                        for split_file in output_files:
                            split_pages = FileProcessor.get_pdf_page_count(split_file)
                            split_size_mb = split_file.stat().st_size / 1024 / 1024
                            logger.info(f"已生成: {split_file.name} ({split_pages}页, {split_size_mb:.2f}MB)")
                        logger.info(f"拆分完成，分片数: {len(output_files)}")
                        return output_files

                    # 当前分片数不满足约束，增加分片重试
                    for split_file in output_files:
                        try:
                            split_file.unlink(missing_ok=True)
                        except Exception:
                            pass
                    num_splits += 1

                logger.error("无法在限制范围内完成PDF拆分")
                return []
        
        except Exception as e:
            logger.error(f"PDF拆分失败: {e}")
            return []

    @staticmethod
    def split_pdf_by_page_limit(file_path: Path, output_dir: Path, max_pages: int, suffix: str = "sub") -> List[Path]:
        """按最大页数强制拆分PDF（用于OCR空结果时的细粒度重试）。"""
        if max_pages <= 0:
            return []

        page_count = FileProcessor.get_pdf_page_count(file_path)
        if page_count <= 0:
            return []
        if page_count <= max_pages:
            return [file_path]

        output_files: List[Path] = []
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                num_splits = (page_count + max_pages - 1) // max_pages

                for i in range(num_splits):
                    writer = PdfWriter()
                    start_page = i * max_pages
                    end_page = min((i + 1) * max_pages, page_count)

                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])

                    output_file = output_dir / f"{file_path.stem}_{suffix}{i+1}.pdf"
                    with open(output_file, 'wb') as out_f:
                        writer.write(out_f)

                    output_files.append(output_file)
                    logger.info(f"已生成细分PDF: {output_file.name} ({end_page - start_page}页)")

            return output_files
        except Exception as e:
            logger.error(f"按页强制拆分失败: {e}")
            return []
    
    @staticmethod
    def adjust_pdf_page_size(file_path: Path, output_dir: Path) -> Path:
        """
        调整PDF页面尺寸为A4标准
        处理非A4纸张的PDF
        """
        logger.info(f"检查PDF页面尺寸: {file_path.name}")
        
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                
                # 检查第一页的尺寸
                if len(reader.pages) == 0:
                    logger.warning(f"PDF为空: {file_path.name}")
                    return file_path
                
                first_page = reader.pages[0]
                page_width = float(first_page.mediabox.width)
                page_height = float(first_page.mediabox.height)
                
                logger.info(f"原始页面尺寸: {page_width:.0f} x {page_height:.0f}")
                
                # 检查是否需要调整（允许10%的误差）
                a4_tolerance = 0.1
                is_a4_width = abs(page_width - MAX_PDF_PAGE_WIDTH) / MAX_PDF_PAGE_WIDTH < a4_tolerance
                is_a4_height = abs(page_height - MAX_PDF_PAGE_HEIGHT) / MAX_PDF_PAGE_HEIGHT < a4_tolerance
                
                # 考虑横向A4
                is_a4_landscape = (abs(page_width - MAX_PDF_PAGE_HEIGHT) / MAX_PDF_PAGE_HEIGHT < a4_tolerance and
                                 abs(page_height - MAX_PDF_PAGE_WIDTH) / MAX_PDF_PAGE_WIDTH < a4_tolerance)

                # 仅对“明显大于A4”的页面做缩放，避免把正常A4或更小页面放大重排
                is_oversized = (
                    page_width > MAX_PDF_PAGE_WIDTH * (1 + a4_tolerance)
                    or page_height > MAX_PDF_PAGE_HEIGHT * (1 + a4_tolerance)
                )
                
                if (is_a4_width and is_a4_height) or is_a4_landscape or not is_oversized:
                    logger.info("页面尺寸无需调整")
                    return file_path
                
                logger.info("页面尺寸不是A4，进行调整...")
                
                writer = PdfWriter()
                a4_w = float(MAX_PDF_PAGE_WIDTH)
                a4_h = float(MAX_PDF_PAGE_HEIGHT)

                for page in reader.pages:
                    src_w = float(page.mediabox.width)
                    src_h = float(page.mediabox.height)

                    if src_w <= 0 or src_h <= 0:
                        writer.add_page(page)
                        continue

                    # 直接缩放页面到A4，避免空白页/资源丢失
                    page.scale_to(a4_w, a4_h)
                    writer.add_page(page)
                
                output_file = output_dir / f"{file_path.stem}_resized.pdf"
                with open(output_file, 'wb') as out_f:
                    writer.write(out_f)
                
                logger.info(f"已生成A4尺寸PDF: {output_file.name}")
                return output_file
        
        except Exception as e:
            logger.error(f"PDF页面尺寸调整失败: {e}")
            return file_path
    
    @staticmethod
    def compress_image(file_path: Path, output_dir: Path, quality: int = 85) -> Path:
        """压缩图片文件"""
        logger.info(f"压缩图片: {file_path.name}")
        
        try:
            img = Image.open(file_path)
            
            # 获取原始图片信息
            original_size = file_path.stat().st_size
            logger.info(f"原始大小: {original_size / 1024 / 1024:.2f}MB")
            
            # 如果图片已经小于限制，直接返回
            if original_size <= MAX_IMAGE_SIZE:
                logger.info("图片大小符合要求，无需压缩")
                return file_path
            
            # 转换为RGB（如果需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = bg
            
            # 输出文件路径
            output_file = output_dir / f"{file_path.stem}_compressed.jpg"
            
            # 迭代压缩直到满足大小要求
            current_quality = quality
            while current_quality >= 10:
                img.save(output_file, 'JPEG', quality=current_quality, optimize=True)
                
                compressed_size = output_file.stat().st_size
                if compressed_size <= MAX_IMAGE_SIZE:
                    logger.info(f"压缩成功: {compressed_size / 1024 / 1024:.2f}MB (质量: {current_quality})")
                    return output_file
                
                current_quality -= 5
            
            logger.warning(f"无法将图片压缩到{MAX_IMAGE_SIZE / 1024 / 1024:.0f}MB以下")
            return output_file
        
        except Exception as e:
            logger.error(f"图片压缩失败: {e}")
            return file_path
    
    @staticmethod
    def process_file(file_path: Path) -> Tuple[List[Path], str]:
        """
        处理单个文件
        返回处理后的文件列表和状态信息
        """
        logger.info(f"开始处理文件: {file_path.name}")
        
        # 验证文件
        is_valid, message = FileProcessor.validate_file(file_path)
        if not is_valid:
            logger.error(message)
            return [], message
        
        output_files = []
        
        try:
            if file_path.suffix.lower() == '.pdf':
                # PDF处理流程
                # 1. 拆分超大PDF
                split_files = FileProcessor.split_pdf(file_path, TEMP_DIR)
                if not split_files:
                    return [], f"PDF无法拆分到限制范围内: {file_path.name}"
                
                # 2. 调整每个PDF的页面尺寸
                for split_file in split_files:
                    resized_file = FileProcessor.adjust_pdf_page_size(split_file, TEMP_DIR)
                    output_files.append(resized_file)
            
            else:
                # 图片处理流程
                # 压缩图片
                compressed_file = FileProcessor.compress_image(file_path, TEMP_DIR)
                output_files.append(compressed_file)
            
            if not output_files:
                return [], f"文件处理失败，未生成可用输出: {file_path.name}"

            logger.info(f"文件处理完成，输出文件数: {len(output_files)}")
            return output_files, "处理成功"
        
        except Exception as e:
            logger.error(f"文件处理出错: {e}")
            return [], f"处理失败: {str(e)}"
    
    @staticmethod
    def get_file_base64(file_path: Path) -> str:
        """获取文件的base64编码"""
        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"无法读取文件: {e}")
            return ""

    @staticmethod
    def get_mime_type(file_path: Path) -> str:
        """根据文件扩展名返回MIME类型。"""
        ext = file_path.suffix.lower()
        mapping = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        return mapping.get(ext, "application/octet-stream")

    @staticmethod
    def build_file_payload_candidates(file_path: Path) -> List[str]:
        """
        构建可回退的文件载荷候选。
        优先使用带MIME的Data URI，其次纯base64文本。
        """
        file_base64 = FileProcessor.get_file_base64(file_path)
        if not file_base64:
            return []

        mime = FileProcessor.get_mime_type(file_path)
        return [
            f"data:{mime};base64,{file_base64}",
            file_base64,
        ]
    
    @staticmethod
    def get_file_list_from_folder(folder_path: Path) -> List[Path]:
        """从文件夹获取所有支持的文件"""
        if not folder_path.is_dir():
            logger.error(f"不是有效的文件夹: {folder_path}")
            return []
        
        files = []
        for ext in SUPPORTED_FORMATS:
            files.extend(folder_path.glob(f"*{ext}"))
            files.extend(folder_path.glob(f"*{ext.upper()}"))
        
        logger.info(f"从文件夹获取 {len(files)} 个文件")
        return sorted(files)

    @staticmethod
    def convert_pdf_to_images(file_path: Path, output_dir: Path, dpi: int = 200) -> List[Path]:
        """将PDF按页转换为PNG图片，返回图片路径列表。"""
        output_images: List[Path] = []
        try:
            pages = convert_from_path(str(file_path), dpi=dpi, fmt="png")
            for idx, page in enumerate(pages, 1):
                image_path = output_dir / f"{file_path.stem}_page_{idx}.png"
                page.save(image_path, format="PNG")
                output_images.append(image_path)
            logger.info(f"PDF转图片完成: {file_path.name} -> {len(output_images)} 张")
            return output_images
        except Exception as e:
            logger.error(f"PDF转图片失败: {file_path.name}, 错误: {e}")
            return []
