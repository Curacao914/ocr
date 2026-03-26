"""
使用说明文档 - 快速指南
"""

# 快速开始指南

## 一、初始化设置（5分钟）

### 1.1 获取API密钥
```bash
# 访问智谱AI官网获取API密钥
# https://open.bigmodel.cn
```

### 1.2 配置环境
```bash
# macOS/Linux
cp .env.example .env
nano .env  # 编辑.env，填入ZHIPU_API_KEY

# Windows
copy .env.example .env
# 用文本编辑器打开.env，填入ZHIPU_API_KEY
```

### 1.3 安装依赖
```bash
# macOS/Linux
pip3 install -r requirements.txt

# Windows
pip install -r requirements.txt
```

## 二、启动应用

### 方式一：使用启动脚本（推荐）
```bash
# macOS/Linux
chmod +x start.sh
./start.sh

# Windows
start.bat
```

### 方式二：直接运行
```bash
# macOS/Linux
python3 main.py

# Windows
python main.py
```

应用启动后自动打开浏览器访问 `http://localhost:7860`

## 三、常见使用场景

### 场景1：识别单个PDF
1. 进入"⚙️ 配置"标签，输入API密钥并初始化
2. 进入"📁 处理文件"标签，选择"单个文件"模式
3. 上传PDF文件
4. 点击"开始处理"等待完成
5. 进入"💾 导出结果"标签，选择导出格式
6. 文件保存到`output/`目录

### 场景2：批量处理一个文件夹
1. 准备工作同场景1
2. 选择"文件夹"模式
3. 输入文件夹路径（如：`~/Documents/pdfs`）
4. 点击"开始处理"
5. 系统自动处理所有文件
6. 批量导出所有结果

### 场景3：处理超大PDF
系统会自动：
- 拆分超过50MB的PDF
- 处理超过100页的PDF
- 无需手动干预

### 场景4：还原扫描文件
1. 上传扫描的PDF或图片
2. 系统自动识别文字和表格
3. 导出整洁的Markdown或Word文档

## 四、输出文件说明

### Markdown输出（.md）
```
├── 元数据（生成时间、工具版本）
├── 完整的文本内容
├── 表格（以Markdown格式）
└── 代码块和特殊格式
```

### Word输出（.docx）
```
├── 格式化的标题和段落
├── 自动生成的表格
├── 嵌入的图片（如需要）
└── 元数据页
```

## 五、故障排除

### 问题1：API密钥错误
```
❌ 错误: API密钥無效
```
**解决方案**：
1. 检查API密钥是否复制正确（无空格）
2. 确认密钥未过期
3. 确认在智谱AI官网获取的是正确的密钥

### 问题2：文件过大无法处理
```
❌ 文件过大: xxx (XX.XXmb, 限制: 50MB)
```
**解决方案**：
系统会自动拆分，如果仍然失败：
- 手动拆分PDF（用Adobe Reader等工具）
- 降低图片分辨率（用图片编辑软件）

### 问题3：识别结果质量差
**解决方案**：
- 确保原始文件清晰（>200dpi）
- 避免高度扭曲的扫描件
- 检查是否有特殊的纹理或背景干扰

### 问题4：导出失败
```
❌ 导出失败: 写入权限不足
```
**解决方案**：
1. 检查`output/`目录是否存在和可写
2. 确认磁盘空间充足
3. 关闭占用输出文件的应用

## 六、性能优化建议

### 提升识别速度
```python
# 最佳实践
1. 使用清晰的扫描件（300dpi）
2. 批量处理相似类型的文档
3. 避免在高并发情况下使用
4. 使用有线网络而非WiFi
```

### 数据成本优化
```
1. 合并多个小文件以减少API调用次数
2. 预先筛选出需要的页面（拆分PDF）
3. 复用识别结果（缓存输出）
```

## 七、高级配置

### 修改文件大小限制
编辑 `src/config.py`：
```python
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 改为需要的大小
MAX_PDF_SIZE = 50 * 1024 * 1024
```

### 修改输出目录
编辑 `.env`：
```
OUTPUT_DIR=./my_output
TEMP_DIR=./my_temp
```

### 调整日志级别
编辑 `.env`：
```
LOG_LEVEL=DEBUG  # 可选: DEBUG, INFO, WARNING, ERROR
```

## 八、与其他工具集成

### 命令行调用
```python
from src.ocr_client import GLMOCRClient
from src.file_processor import FileProcessor

client = GLMOCRClient(api_key="your_key")
result = client.ocr_image("path/to/file.pdf")
print(result.markdown_content)
```

### 作为库使用
```python
import sys
sys.path.insert(0, '/path/to/ocr/tool')

from src.output_converter import OutputConverter

OutputConverter.export_result(
    markdown_content=content,
    output_filename="my_doc",
    output_dir="./output",
    export_format="docx"
)
```

## 九、技术支持

### 获取帮助
1. 查看应用内的"❓ 帮助"标签
2. 查看项目的 [README.md](README.md)
3. 检查 [CHANGELOG.md](CHANGELOG.md) 获取更新信息
4. 查看日志文件：`temp/logs/`

### 日志分析
```bash
# macOS/Linux
tail -f temp/logs/ocr_*.log

# Windows
# 用记事本打开 temp/logs/ocr_*.log
```

### 联系开发者
- GitHub Issues：[项目讨论]
- 邮件：support@example.com

## 十、常见工作流

### 工作流1：合同批量识别和归档
```
1. 将所有合同放在一个文件夹
2. 在应用中输入文件夹路径
3. 选择"导出为Word文档"
4. 自动后自动生成结构化文档
5. 批量上传到文档管理系统
```

### 工作流2：学术论文提取
```
1. 上传研究论文PDF
2. 导出为Markdown
3. 直接用编辑器编辑（保留结构）
4. 提取关键信息
5. 转换为所需格式
```

### 工作流3：发票数据提取
```
1. 批量上传发票图片/PDF
2. 导出为Word文档
3. 使用表格编辑功能检查
4. 导入到财务系统
```

## 常见命令

```bash
# 启动应用
python3 main.py

# 运行测试
python3 test_modules.py

# 查看日志
tail -100f temp/logs/ocr_*.log

# 清理临时文件
rm -rf temp/*

# 安装特定版本依赖
pip install -r requirements.txt --upgrade

# 检查依赖
pip list | grep -E 'zai|gradio|docx|pdf'
```

---

**更多信息**：查看 README.md 和 CHANGELOG.md
