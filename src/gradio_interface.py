import os
import re
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

        # 启动时自动尝试加载已保存的 API Key
        if self.saved_api_key:
            try:
                self.ocr_client = GLMOCRClient(api_key=self.saved_api_key)
                logger.info("已自动加载并初始化已保存的API密钥")
            except Exception as e:
                logger.warning(f"已保存的API密钥初始化失败，请重新设置: {e}")

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

    @staticmethod
    def _source_key_from_processed_name(file_name: str) -> str:
        """将预处理后的分片文件名归并为原始文件键。"""
        # 兼容: xxx_part1.pdf, xxx_part1_resized.pdf, xxx_resized.pdf
        name = re.sub(r"_part\d+(_resized)?$", "", Path(file_name).stem)
        name = re.sub(r"_resized$", "", name)
        return name
    
    def initialize_client(self, api_key: str) -> tuple:
        """初始化OCR客户端"""
        try:
            api_key = (api_key or "").strip()
            if not api_key:
                return False, "请输入API密钥"

            # 先持久化，再初始化，确保下次启动自动沿用
            self._persist_api_key(api_key)
            self.saved_api_key = api_key
            
            self.ocr_client = GLMOCRClient(api_key=api_key)
            logger.info("客户端初始化成功")
            return True, "客户端初始化成功 ✓"
        except Exception as e:
            logger.error(f"客户端初始化失败: {e}")
            return False, f"初始化失败: {str(e)}"
    
    def process_files_stream(
        self,
        file_input: Optional[object],
        folder_path: Optional[str],
        process_single: bool,
        max_concurrency: int,
        ocr_progress=None
    ):
        """
        处理文件
        """
        if not self.ocr_client:
            yield "", "请先初始化客户端", "未开始"
            return
        
        self.processing = True
        files_to_process = []
        
        try:
            # 获取要处理的文件
            if process_single and file_input is not None:
                # 支持单次选择多个文件
                selected_files = file_input if isinstance(file_input, list) else [file_input]
                for selected in selected_files:
                    if hasattr(selected, 'name'):
                        file_path = Path(selected.name)
                    else:
                        file_path = Path(selected)

                    is_valid, message = FileProcessor.validate_file(file_path)
                    if not is_valid:
                        yield "", message, f"校验失败: {file_path.name}"
                        return

                    # 预处理文件
                    processed_files, status = FileProcessor.process_file(file_path)
                    if not processed_files:
                        yield "", status, f"预处理失败: {file_path.name}"
                        return

                    files_to_process.extend(processed_files)
            
            elif folder_path:
                # 从文件夹获取文件
                folder = Path(folder_path)
                if not folder.exists():
                    yield "", f"文件夹不存在: {folder_path}", "未开始"
                    return
                
                all_files = FileProcessor.get_file_list_from_folder(folder)
                if not all_files:
                    yield "", "文件夹中没有支持的文件", "未开始"
                    return
                
                # 预处理所有文件
                for file_path in all_files:
                    processed_files, status = FileProcessor.process_file(file_path)
                    files_to_process.extend(processed_files)
            
            else:
                yield "", "请选择文件或输入文件夹路径", "未开始"
                return
            
            if not files_to_process:
                yield "", "没有要处理的文件", "未开始"
                return

            # 先回传准备状态
            yield "等待处理...", f"准备完成，共 {len(files_to_process)} 个文件", "排队中..."
            
            # 批量OCR识别（并发）
            total = len(files_to_process)
            workers = max(1, min(int(max_concurrency), total))
            logger.info(f"开始处理 {total} 个文件，并发数: {workers}")

            results = []
            done = 0
            success_count = 0

            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_task = {
                    executor.submit(
                        self.ocr_client.ocr_image,
                        file_path,
                        True,
                        True
                    ): (idx, file_path)
                    for idx, file_path in enumerate(files_to_process)
                }

                for future in as_completed(future_to_task):
                    idx, file_path = future_to_task[future]
                    try:
                        result = future.result()
                    except Exception as exec_error:
                        result = OCRResult(success=False, error_message=str(exec_error))

                    done += 1
                    if result.success:
                        success_count += 1
                        results.append({
                            'order': idx,
                            'file_name': file_path.name,
                            'status': '✓ 成功',
                            'markdown': result.markdown_content,
                            'images': result.images or [],
                            'tokens': result.tokens_used
                        })
                    else:
                        results.append({
                            'order': idx,
                            'file_name': file_path.name,
                            'status': f'✗ 失败: {result.error_message}',
                            'markdown': '',
                            'images': [],
                            'tokens': 0
                        })

                    # 实时进度更新
                    progress_text = (
                        f"{done}/{total} | 成功 {success_count} | 失败 {done - success_count} | "
                        f"最新完成: {file_path.name}"
                    )
                    if callable(ocr_progress):
                        try:
                            ocr_progress(done / total, desc=progress_text)
                        except Exception as progress_error:
                            logger.warning(f"进度更新失败，已忽略: {progress_error}")

                    file_list_html = self._generate_file_list_html(results)
                    status_msg = f"处理中: {done}/{total}"
                    yield file_list_html, status_msg, progress_text

            # 先按处理前顺序排序，再按原文档聚合分片，保证跨页连续
            results.sort(key=lambda x: x.get('order', 0))
            grouped = {}
            for item in results:
                source_key = self._source_key_from_processed_name(item['file_name'])
                if source_key not in grouped:
                    grouped[source_key] = {
                        'file_name': f"{source_key}.pdf" if source_key else item['file_name'],
                        'status': '✓ 成功',
                        'markdown_parts': [],
                        'images': [],
                        'tokens': 0,
                    }

                g = grouped[source_key]
                if item['markdown']:
                    g['markdown_parts'].append(item['markdown'])
                g['images'].extend(item['images'] or [])
                g['tokens'] += item['tokens'] or 0
                if not item['status'].startswith('✓'):
                    g['status'] = item['status']

            merged_results = []
            for _, g in grouped.items():
                # 图片去重
                seen = set()
                dedup_images = [u for u in g['images'] if not (u in seen or seen.add(u))]
                merged_markdown = "\n\n".join(g['markdown_parts']).strip()
                merged_tokens = g['tokens'] or 0
                # 兜底：避免“空内容+0 token”被显示为成功
                if g['status'].startswith('✓') and not merged_markdown and not dedup_images and merged_tokens == 0:
                    g['status'] = '✗ 失败: OCR返回空结果（内容为空且Token为0）'

                merged_results.append({
                    'file_name': g['file_name'],
                    'status': g['status'],
                    'markdown': merged_markdown,
                    'images': dedup_images,
                    'tokens': merged_tokens,
                })

            self.current_results = merged_results
            
            # 生成文件列表HTML
            file_list_html = self._generate_file_list_html(self.current_results)
            
            status_msg = f"处理完成: {sum(1 for r in self.current_results if r['status'].startswith('✓'))}/{len(self.current_results)} 成功"
            logger.info(status_msg)
            
            yield file_list_html, status_msg, "全部完成"
        
        except Exception as e:
            logger.exception(f"文件处理出错: {e}")
            yield "", f"处理出错: {str(e)}", f"异常: {str(e)}"
        finally:
            self.processing = False
    
    def export_results(
        self,
        export_format: str,
        include_images: bool
    ) -> tuple:
        """显示导出结果"""
        try:
            if not self.current_results:
                return "", "没有要导出的结果"
            
            success_count = 0
            exported_files = []
            
            for result in self.current_results:
                if not result['status'].startswith('✓'):
                    continue
                
                file_name = Path(result['file_name']).stem
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_name = f"{file_name}_{timestamp}"
                
                # 导出内容
                success, files = OutputConverter.export_result(
                    markdown_content=result['markdown'],
                    output_filename=output_name,
                    output_dir=OUTPUT_DIR,
                    export_format=export_format,
                    image_urls=result['images'] if include_images else None,
                    include_metadata=True
                )
                
                if success:
                    success_count += 1
                    exported_files.extend(files)
            
            if exported_files:
                export_html = self._generate_export_html(exported_files)
                msg = f"成功导出 {success_count} 个文件"
                return export_html, msg
            else:
                return "", "导出失败"
        
        except Exception as e:
            logger.error(f"导出出错: {e}")
            return "", f"导出出错: {str(e)}"
    
    def preview_result(self, result_index: int) -> tuple:
        """预览单个结果"""
        try:
            if result_index >= len(self.current_results):
                return "", "无效的结果索引"
            
            result = self.current_results[result_index]
            content = result['markdown']
            
            return content, f"预览: {result['file_name']} ({result['status']})"
        
        except Exception as e:
            logger.error(f"预览失败: {e}")
            return "", f"预览失败: {str(e)}"
    
    @staticmethod
    def _generate_file_list_html(results: List[dict]) -> str:
        """生成文件列表HTML"""
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '''
        <tr style="background-color: #f0f0f0;">
            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">文件名</th>
            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">状态</th>
            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Token使用</th>
        </tr>
        '''
        
        for i, result in enumerate(results):
            status_color = "#28a745" if result['status'].startswith('✓') else "#dc3545"
            html += f'''
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">{result['file_name']}</td>
                <td style="border: 1px solid #ddd; padding: 8px; color: {status_color};">{result['status']}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{result['tokens']}</td>
            </tr>
            '''
        
        html += '</table>'
        return html
    
    @staticmethod
    def _generate_export_html(exported_files: List[str]) -> str:
        """生成导出文件列表HTML"""
        html = '<div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 12px; border-radius: 4px;">'
        html += '<h4 style="color: #155724;">✓ 导出成功</h4>'
        html += '<ul>'
        
        for file_path in exported_files:
            html += f'<li>{Path(file_path).name}</li>'
        
        html += '</ul>'
        html += f'<p style="color: #666;">输出目录: {OUTPUT_DIR}</p>'
        html += '</div>'
        
        return html

def create_interface():
    """创建Gradio界面"""
    interface = OCRInterface()
    
    with gr.Blocks(title="GLM-OCR", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # GLM-OCR 极简工作台
            一步到位。
            """
        )

        with gr.Row():
            process_mode = gr.Radio(
                choices=["单个文件", "文件夹"],
                value="单个文件",
                label="来源类型",
            )
            process_btn = gr.Button("开始处理", variant="primary")
            export_btn = gr.Button("导出", variant="secondary")

        file_input = gr.File(
            label="上传文件（可多选）",
            file_types=["pdf", "image"],
            file_count="multiple",
            visible=True,
        )
        folder_input = gr.Textbox(
            label="文件夹路径",
            placeholder="/path/to/folder",
            visible=False,
        )

        with gr.Accordion("高级设置（可选）", open=False):
            api_key_input = gr.Textbox(
                label="ZHIPU API密钥",
                type="password",
                placeholder="输入你的API密钥",
                value=interface.saved_api_key,
            )
            init_btn = gr.Button("保存并初始化", variant="secondary")
            init_status = gr.Textbox(
                label="配置状态",
                interactive=False,
                value="已加载已保存的API密钥" if interface.saved_api_key else "未检测到已保存密钥"
            )

            concurrency = gr.Slider(
                minimum=1,
                maximum=8,
                step=1,
                value=3,
                label="并发数",
            )
            export_format = gr.Radio(
                choices=["Markdown", "Word文档", "两种格式"],
                value="两种格式",
                label="导出格式",
            )
            include_images = gr.Checkbox(
                label="导出时包含图片",
                value=True,
            )
            gr.Markdown(
                "支持：PDF/JPG/JPEG/PNG；图片≤10MB，PDF≤50MB，最多100页。"
            )

        result_html = gr.HTML(label="处理结果", value="等待处理...")
        process_status = gr.Textbox(label="状态信息", interactive=False)
        realtime_progress = gr.Textbox(label="实时进度", interactive=False, value="未开始")

        with gr.Row():
            result_selector = gr.Dropdown(choices=[], label="预览文件", value=None)
            preview_refresh_btn = gr.Button("刷新列表", variant="secondary")
            preview_btn = gr.Button("预览", variant="secondary")

        preview_title = gr.Textbox(label="预览信息", interactive=False)
        preview_markdown = gr.Markdown()

        export_html = gr.HTML(value="等待导出...")
        export_status = gr.Textbox(label="导出状态", interactive=False)

        def on_init_click(api_key):
            success, message = interface.initialize_client(api_key)
            return message

        def on_mode_change(mode):
            is_single = mode == "单个文件"
            return gr.update(visible=is_single), gr.update(visible=not is_single)

        def refresh_preview_list():
            if not interface.current_results:
                return gr.update(choices=[], value=None), "暂无可预览结果"
            choices = [r['file_name'] for r in interface.current_results]
            return gr.update(choices=choices, value=choices[0]), f"已加载 {len(choices)} 个结果"

        def on_preview_click(result_name):
            if not interface.current_results:
                return "没有可预览的结果", "请先处理文件"

            for result in interface.current_results:
                if result['file_name'] == result_name:
                    return result['markdown'], f"预览: {result['file_name']}"

            return "未找到结果", "错误"

        def on_process_click(file_input, folder_path, process_mode, concurrency_value, progress=gr.Progress()):
            is_single = process_mode == "单个文件"
            yield from interface.process_files_stream(
                file_input,
                folder_path if not is_single else None,
                is_single,
                int(concurrency_value),
                progress
            )

        def on_export_click(format_choice, include_imgs):
            format_map = {
                "Markdown": "markdown",
                "Word文档": "docx",
                "两种格式": "both"
            }
            return interface.export_results(
                format_map.get(format_choice, "both"),
                include_imgs
            )

        init_btn.click(
            on_init_click,
            inputs=[api_key_input],
            outputs=[init_status]
        )

        process_mode.change(
            on_mode_change,
            inputs=[process_mode],
            outputs=[file_input, folder_input]
        )

        process_btn.click(
            on_process_click,
            inputs=[file_input, folder_input, process_mode, concurrency],
            outputs=[result_html, process_status, realtime_progress]
        )

        export_btn.click(
            on_export_click,
            inputs=[export_format, include_images],
            outputs=[export_html, export_status]
        )

        preview_refresh_btn.click(
            refresh_preview_list,
            outputs=[result_selector, preview_title]
        )

        preview_btn.click(
            on_preview_click,
            inputs=[result_selector],
            outputs=[preview_markdown, preview_title]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
