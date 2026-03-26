# 📄 GLM-OCR 文档转换工具

一个功能强大的文档OCR识别和转换工具，基于智谱AI的GLM-OCR模型开发。支持PDF和图片的智能识别、处理和导出。

## ✨ 功能特性

### 核心功能
- 📝 **文档识别**：支持PDF、JPG、PNG等多种格式的文档OCR识别
- 🖼️ **图片处理**：自动压缩超大图片，保留高质量输出
- 📦 **PDF处理**：
  - 自动拆分超大PDF（>50MB）
  - 处理超出页数限制的PDF（>100页）
  - 自动调整非A4尺寸的页面
- 📤 **批量处理**：可处理单个文件或整个文件夹
- 💾 **灵活导出**：支持Markdown和Word文档格式导出
- 🎯 **精准保存**：保留印章、签名等重要图片信息
- 🎨 **用户友好**：基于Gradio的图形化界面，易于使用

### 技术特点
- 小模型，高精度：0.9B参数量，SOTA级别的识别能力
- 成本低廉：约为传统OCR方案的1/10
- 高效处理：PDF处理速度 1.86 页/秒，图片处理速度 0.67 张/秒

## 📋 系统要求

- Python 3.8 或更高版本
- 操作系统：Windows、macOS、Linux
- 网络连接（用于API调用）

## 🚀 快速开始

### 1. 环境准备

克隆或下载项目：
```bash
cd 案卷ocr
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

**注意**：在macOS上，如果`pip install`遇到问题，可尝试：
```bash
pip3 install -r requirements.txt
```

### 3. 配置API密钥

#### 方式一：复制和编辑.env文件

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑.env文件，填入你的API密钥
# 使用文本编辑器打开.env，修改以下内容：
ZHIPU_API_KEY=你的API密钥
```

#### 方式二：从智谱AI获取API密钥

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn)
2. 注册账号并登录
3. 进入"API管理"获取API密钥
4. 复制密钥到.env文件的`ZHIPU_API_KEY`字段

### 4. 启动应用

```bash
python3 main.py
```

应用启动后，自动打开浏览器访问 `http://localhost:7860`

## 💡 使用指南

### 方式一：单个文件处理

1. 打开应用界面，进入"⚙️ 配置"标签
2. 输入API密钥，点击"初始化客户端"
3. 进入"📁 处理文件"标签
4. 选择处理模式为"单个文件"
5. 上传PDF或图片文件
6. 点击"开始处理"等待识别完成
7. 进入"💾 导出结果"标签，选择导出格式
8. 点击"导出结果"，文件已保存到`output/`目录

### 方式二：批量处理文件夹

1. 准备工作同上
2. 进入"📁 处理文件"标签
3. 选择处理模式为"文件夹"
4. 输入包含PDF/JPG/PNG的文件夹路径（例：`/path/to/documents`）
5. 点击"开始处理"
6. 系统将自动处理文件夹中的所有文件
7. 导出步骤同上

### 预览和导出

- **预览结果**：在"👁️ 预览结果"标签选择文件并预览识别结果
- **导出格式**：可选择Markdown、Word文档或两种都导出
- **搭配图片**：导出时勾选"包含图片"以保留图片信息
- **输出位置**：所有输出文件保存在`./output/`目录

## 📐 技术细节

### 文件处理流程

#### PDF文件处理

```
输入PDF → 验证大小和页数 → 拆分(>50MB或>100页) → 调整页面为A4 → 输出
```

**处理规则**：
- 文件大小 > 50MB：按照50MB限制进行拆分
- 页数 > 100：每100页拆分为一个文件
- 页面尺寸调整：统一调整为A4标准尺寸（2100×2970像素）

#### 图片文件处理

```
输入图片 → 验证大小 → 压缩(>10MB) → 输出
```

**处理规则**：
- 文件大小 > 10MB：自动压缩
- 使用JPEG格式压缩，保留70-90的质量级别
- 支持RGBA、LA等模式的图片转换

### API调用参数

| 参数 | 说明 | 取值 |
|------|------|------|
| model | 模型名称 | glm-ocr |
| file | 输入文件 | URL或Base64编码 |
| return_crop_images | 返回截图 | false（暂不使用） |
| need_layout_visualization | 需要布局可视化 | false（暂不使用） |
| user_id | 用户标识 | anonymous |

### 输出格式

#### Markdown格式
- 包含完整的文档结构（标题、段落、列表等）
- 自动转换表格为Markdown表格
- 保留代码块格式
- 添加生成时间元数据

#### Word文档格式
- 转换Markdown为Word文档
- 支持自动设置标题样式
- 支持表格、列表等结构化内容
- 可选加入图片附件

## 🛠️ 项目结构

```
案卷ocr/
├── src/
│   ├── __init__.py           # 包初始化
│   ├── config.py              # 配置管理
│   ├── logger.py              # 日志系统
│   ├── file_processor.py       # 文件处理模块
│   ├── ocr_client.py           # API调用模块
│   ├── output_converter.py     # 输出转换模块
│   └── gradio_interface.py     # UI界面
├── main.py                    # 主程序入口
├── test_modules.py            # 测试脚本
├── requirements.txt           # 依赖包列表
├── .env.example              # 环境配置示例
├── .gitignore                # Git忽略文件
├── README.md                 # 本文件
├── CHANGELOG.md              # 更新日志
├── output/                   # 输出文件目录
└── temp/                     # 临时文件目录
```

## 🧪 测试

运行测试套件验证各模块功能：

```bash
python3 test_modules.py
```

测试包括：
- ✓ 配置加载测试
- ✓ 文件处理测试
- ✓ 输出转换测试
- ✓ Base64编码测试

## 🔧 常见问题

### Q1: 如何设置代理访问API？
A: 在.env文件中添加代理配置：
```
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=https://your-proxy:port
```

### Q2: 文件处理失败怎么办？
A: 
1. 检查文件格式是否为PDF/JPG/PNG
2. 检查文件大小是否符合要求
3. 查看`temp/logs/`目录中的日志文件
4. 确认API密钥是否正确

### Q3: 如何修改输出目录？
A: 编辑.env文件，修改`OUTPUT_DIR`和`TEMP_DIR`参数

### Q4: 支持中文吗？
A: 是的，完全支持中文。界面、日志和识别结果均支持中文

### Q5: 可以在后台运行吗？
A: 在Linux/macOS上：
```bash
nohup python3 main.py > app.log 2>&1 &
```
在Windows上：
```bash
python main.py > nul 2>&1 &
```

## 📊 性能参考

在标准硬件环境下的性能指标：

| 指标 | 数值 |
|------|------|
| PDF处理速度 | 1.86 页/秒 |
| 图片处理速度 | 0.67 张/秒 |
| API调用延迟 | <5秒（单个文件） |
| 识别准确率 | 94.6%（OmniDocBench基准） |
| 成本 | ¥0.2/百万Tokens |

## 🤝 支持和反馈

- 文档：[GLM-OCR文档](https://docs.bigmodel.cn/llms.txt)
- 问题反馈：[智谱AI开发者社区](https://chat.z.ai)
- 官网：https://bigmodel.cn

## 📝 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

## 📄 许可证

本项目基于MIT许可证开源。使用GLM-OCR API需遵守智谱AI的服务条款。

## ⚠️ 免责声明

- 本工具仅用于学习和研究目的
- 用户需自行承担使用本工具产生的一切后果
- 不支持用于任何违法或违反智谱AI服务条款的用途
- 建议定期备份重要文档

---

**开发时间**：2026年3月  
**版本**：1.0.0  
**维护者**：AI Assistant  
