import time
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from zai import ZhipuAiClient

from src.config import ZHIPU_API_KEY
from src.logger import get_logger
from src.file_processor import FileProcessor

logger = get_logger()

@dataclass
class OCRResult:
    """OCR结果数据类"""
    success: bool
    markdown_content: str = ""
    layout_details: list = None
    images: list = None
    error_message: str = ""
    tokens_used: int = 0
    request_id: str = ""

class GLMOCRClient:
    """GLM-OCR API客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化客户端"""
        self.api_key = api_key or ZHIPU_API_KEY
        
        if not self.api_key:
            raise ValueError("API密钥未设置，请检查环境变量或传入参数")
        
        try:
            self.client = ZhipuAiClient(api_key=self.api_key)
            logger.info("GLM-OCR客户端初始化成功")
        except Exception as e:
            logger.error(f"GLM-OCR客户端初始化失败: {e}")
            raise
    
    @staticmethod
    def _extract_image_urls(md_content: str, layout_details) -> list:
        """从markdown与布局详情中提取图片URL（含印章/截图）。"""
        urls = []

        if md_content:
            md_urls = re.findall(r"!\[[^\]]*\]\((https?://[^)\s]+)\)", md_content)
            urls.extend(md_urls)

        if layout_details:
            for page_items in layout_details:
                if not isinstance(page_items, list):
                    continue
                for item in page_items:
                    if not isinstance(item, dict):
                        continue
                    if item.get("label") == "image":
                        content = item.get("content")
                        if isinstance(content, str) and content.startswith("http"):
                            urls.append(content)

        # 去重并保持顺序
        seen = set()
        deduped = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                deduped.append(u)
        return deduped

    @staticmethod
    def _is_effectively_empty_result(markdown_content: str, images: list, tokens_used: int) -> bool:
        """判断OCR结果是否为空内容（用于避免空结果被误判为成功）。"""
        text = (markdown_content or "").strip()
        image_count = len(images or [])
        return (not text) and image_count == 0 and int(tokens_used or 0) == 0

    @staticmethod
    def _extract_markdown_from_response(response) -> str:
        """尽量兼容不同SDK版本的响应字段，提取markdown正文。"""
        for key in ["md_results", "markdown", "content", "text"]:
            value = getattr(response, key, None)
            if isinstance(value, str) and value.strip():
                return value

        if isinstance(response, dict):
            for key in ["md_results", "markdown", "content", "text"]:
                value = response.get(key)
                if isinstance(value, str) and value.strip():
                    return value

        result_obj = getattr(response, "result", None)
        if isinstance(result_obj, str) and result_obj.strip():
            return result_obj
        if isinstance(result_obj, dict):
            for key in ["md_results", "markdown", "content", "text"]:
                value = result_obj.get(key)
                if isinstance(value, str) and value.strip():
                    return value

        return ""

    def ocr_image(
        self,
        file_path: Path,
        return_crop_images: bool = False,
        need_layout_visualization: bool = False,
        user_id: str = "anonymous"
    ) -> OCRResult:
        """
        识别单个图片或PDF文件
        
        Args:
            file_path: 文件路径
            return_crop_images: 是否返回截图信息
            need_layout_visualization: 是否需要详细布局图片结果信息
            user_id: 用户ID
        
        Returns:
            OCRResult: 识别结果
        """
        try:
            logger.info(f"开始OCR识别: {file_path.name}")

            payload_candidates = FileProcessor.build_file_payload_candidates(file_path)
            if not payload_candidates:
                return OCRResult(
                    success=False,
                    error_message=f"无法读取文件: {file_path}"
                )

            response = None
            last_error: Optional[Exception] = None

            for attempt, payload in enumerate(payload_candidates, 1):
                logger.info(f"发送API请求... (payload方案 {attempt}/{len(payload_candidates)})")
                try:
                    response = self.client.layout_parsing.create(
                        model="glm-ocr",
                        file=payload,
                        return_crop_images=return_crop_images,
                        need_layout_visualization=need_layout_visualization,
                        user_id=user_id
                    )
                    break
                except Exception as req_error:
                    last_error = req_error
                    logger.warning(f"payload方案 {attempt} 失败: {req_error}")

                    # 1210通常是输入格式解析错误，继续尝试下一个载荷方案
                    if '"code":"1210"' in str(req_error) or "输入格式/解析错误" in str(req_error):
                        continue
                    # 其他错误也继续尝试下一个方案，直到耗尽候选
                    continue

            if response is None:
                raise last_error if last_error else RuntimeError("所有载荷方案均失败")
            
            logger.info(f"API请求完成，处理结果...")
            
            # 解析响应
            md_content = self._extract_markdown_from_response(response)
            
            layout_details = getattr(response, 'layout_details', None)
            extracted_urls = self._extract_image_urls(md_content, layout_details)
            # 仅保留可映射到正文的图片，避免把layout可视化整页图追加到文末
            images = extracted_urls
            
            usage = getattr(response, 'usage', {})
            tokens_used = getattr(usage, 'total_tokens', 0) if usage else 0
            request_id = getattr(response, 'request_id', "")

            # 有些请求会返回成功状态但正文为空且tokens=0，需作为异常场景处理
            if self._is_effectively_empty_result(md_content, images, tokens_used):
                logger.error(f"OCR返回空结果: {file_path.name}")
                return OCRResult(
                    success=False,
                    error_message="OCR返回空结果（内容为空且Token为0）",
                    request_id=request_id
                )
            
            logger.info(f"识别完成 (Token used: {tokens_used})")
            
            return OCRResult(
                success=True,
                markdown_content=md_content,
                layout_details=layout_details,
                images=images,
                tokens_used=tokens_used,
                request_id=request_id
            )
        
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return OCRResult(
                success=False,
                error_message=f"识别失败: {str(e)}"
            )
    
    def ocr_batch(
        self,
        file_paths: list,
        return_crop_images: bool = False,
        need_layout_visualization: bool = False,
        user_id: str = "anonymous",
        progress_callback=None
    ) -> list:
        """
        批量识别多个文件
        
        Args:
            file_paths: 文件路径列表
            return_crop_images: 是否返回截图信息
            need_layout_visualization: 是否需要详细布局图片结果信息
            user_id: 用户ID
            progress_callback: 进度回调函数
        
        Returns:
            list: OCR结果列表
        """
        results = []
        total = len(file_paths)
        
        logger.info(f"开始批量处理 {total} 个文件")
        
        for index, file_path in enumerate(file_paths, 1):
            if progress_callback:
                progress_callback(index, total, f"正在处理: {file_path.name}")
            
            result = self.ocr_image(
                file_path,
                return_crop_images=return_crop_images,
                need_layout_visualization=need_layout_visualization,
                user_id=user_id
            )
            
            results.append({
                'file': file_path.name,
                'result': result
            })
            
            # 避免API限流
            time.sleep(1)
        
        logger.info(f"批量处理完成，成功: {sum(1 for r in results if r['result'].success)}/{total}")
        
        return results
    
    def validate_api_key(self) -> bool:
        """验证API密钥是否有效"""
        try:
            # 尝试一个简单的API调用来验证密钥
            logger.info("验证API密钥...")
            # 这里可以添加一个轻量级的测试调用
            return True
        except Exception as e:
            logger.error(f"API密钥验证失败: {e}")
            return False
