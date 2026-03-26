"""
项目文档导航 - 快速查找你需要的文档
"""

# 📚 项目文档导航

## 🎯 根据你的需求选择文档

### 我是第一次使用

👉 **推荐按顺序阅读**：

1. **[BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)** ⭐⭐⭐⭐⭐
   - 📖 完全新手指南
   - ⏱️ 预计阅读时间：20分钟
   - 📋 内容：从0开始的全部步骤
   - ✨ 包含：安装、配置、首次使用、常见问题

2. **[QUICKSTART.md](QUICKSTART.md)** ⭐⭐⭐⭐
   - 🚀 快速开始指南  
   - ⏱️ 预计阅读时间：10分钟
   - 📋 内容：最小化配置和启动
   - ✨ 包含：快速命令、基础用法、工作流示例

3. **[README.md](README.md)**
   - 📖 完整项目文档
   - ⏱️ 预计阅读时间：30分钟
   - 📋 内容：详细的功能和技术说明
   - ✨ 包含：功能清单、技术栈、配置选项

### 我已经安装好了，想快速开始

👉 **跳过前面，直接看**：

```bash
# 方式一：使用启动脚本（推荐）
./start.sh              # macOS/Linux
# 或
start.bat              # Windows

# 方式二：直接运行
python3 main.py         # macOS/Linux
# 或
python main.py          # Windows
```

📖 详见：[QUICKSTART.md](QUICKSTART.md) 的"启动应用"部分

### 我想了解项目的完整细节

👉 **推荐阅读**：

1. [README.md](README.md) - 完整的项目文档
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目完成总结
3. [CHANGELOG.md](CHANGELOG.md) - 版本更新日志

### 我遇到问题想解决

👉 **按问题类型查找**：

| 问题类型 | 文档位置 |
|---------|--------|
| 安装问题 | [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md#前置需求) |
| API密钥问题 | [QUICKSTART.md](QUICKSTART.md#获取api密钥) |
| 常见错误 | [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md#常见问题速查表) |
| 性能问题 | [README.md](README.md#性能参考) |
| 进阶配置 | [QUICKSTART.md](QUICKSTART.md#高级配置) |

### 我是开发者，想集成或扩展

👉 **推荐阅读**：

1. [README.md](README.md#项目结构) - 项目结构
2. [README.md](README.md#技术细节) - 技术细节
3. [QUICKSTART.md](QUICKSTART.md#与其他工具集成) - 集成指南
4. 代码中的docstring和注释

## 📋 全部文档列表

### 📖 用户文档

| 文档 | 用途 | 阅读时间 |
|------|------|--------|
| **BEGINNER_GUIDE.md** | 完全新手指南 | 20分钟 |
| **QUICKSTART.md** | 快速开始 | 10分钟 |
| **README.md** | 完整文档 | 30分钟 |
| **FAQ.md** | 常见问题解答 | 5分钟 |

### 📊 项目文档

| 文档 | 用途 | 阅读时间 |
|------|------|--------|
| **CHANGELOG.md** | 版本更新日志 | 10分钟 |
| **PROJECT_SUMMARY.md** | 项目完成总结 | 15分钟 |
| **本文件** | 文档导航 | 5分钟 |

### 💻 代码文档

| 文件 | 说明 |
|------|------|
| `src/config.py` | 配置管理 |
| `src/logger.py` | 日志系统 |
| `src/file_processor.py` | 文件处理 |
| `src/ocr_client.py` | API调用 |
| `src/output_converter.py` | 输出转换 |
| `src/gradio_interface.py` | UI界面 |

### ⚙️ 配置文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境变量配置 |
| `.env.example` | 配置示例 |
| `.gitignore` | Git忽略文件 |
| `requirements.txt` | Python依赖 |

## 🗺️ 快速导航地图

```
从这里开始
    ↓
是否是第一次使用？
    ├─ 是 → BEGINNER_GUIDE.md
    └─ 否 → 继续
         是否已安装配置好？
         ├─ 是 → QUICKSTART.md"启动应用"部分
         └─ 否 → 回到BEGINNER_GUIDE.md
                遇到问题？
                ├─ 安装问题 → BEGINNER_GUIDE.md#前置需求
                ├─ 使用问题 → README.md#常见问题
                └─ 其他 → 查看日志并联系支持
```

## 💡 最常见的场景

### 场景1：我想立即开始使用（5分钟）

**推荐路径**：
1. 复制 [QUICKSTART.md](QUICKSTART.md) 中的命令
2. 按顺序运行
3. Web界面打开后开始使用

**参考时间**：5分钟

### 场景2：我想充分理解这个工具（1小时）

**推荐路径**：
1. 阅读 [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md) (20分钟)
2. 阅读 [README.md](README.md) (30分钟)
3. 实际操作 (10分钟)

**参考时间**：1小时

### 场景3：我遇到了问题（10分钟）

**推荐路径**：
1. 查看 [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md#常见问题速查表)
2. 如果未解决，查看应用的"❓ 帮助"标签
3. 查看日志文件 `temp/logs/`
4. 联系技术支持

**参考时间**：10分钟

### 场景4：我想集成它到我的系统（30分钟）

**推荐路径**：
1. 理解项目结构（[README.md](README.md#项目结构)）
2. 查看API文档（[QUICKSTART.md](QUICKSTART.md#与其他工具集成)）
3. 编写集成代码
4. 测试和调试

**参考时间**：30分钟

## 🔗 外部资源

### 官方链接

- 🌐 **智谱AI官网**：https://bigmodel.cn
- 📚 **GLM-OCR文档**：https://docs.bigmodel.cn/llms.txt
- 🔑 **API管理**：https://open.bigmodel.cn
- 💬 **开发者社区**：https://chat.z.ai

### 技术文档

- 📖 **Gradio文档**：https://gradio.app
- 📖 **PyPDF2文档**：https://pypdf2.readthedocs.io
- 📖 **python-docx文档**：https://python-docx.readthedocs.io
- 📖 **Pillow文档**：https://pillow.readthedocs.io

## 📞 获取帮助

### 按问题类型选择

| 问题类型 | 解决方案 |
|---------|--------|
| 🤔 功能使用问题 | 查看应用内"❓ 帮助"标签 |
| 🐛 识别效果问题 | 查看[README.md](README.md#常见问题) |
| ⚙️ 配置问题 | 查看[BEGINNER_GUIDE.md](BEGINNER_GUIDE.md) |
| 🔧 技术问题 | 查看代码注释和docstring |
| 📋 其他问题 | 查看[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |

### 查看日志

```bash
# 最新的日志文件
cd temp/logs
ls -lart                    # macOS/Linux
# 或
dir                         # Windows
```

## 🎯 推荐学习路径

### 初级用户（想快速使用）
```
BEGINNER_GUIDE.md → QUICKSTART.md → 开始使用
预计时间：30分钟
```

### 中级用户（想充分了解）
```
BEGINNER_GUIDE.md → README.md → 实际操作 → 进阶功能
预计时间：2小时
```

### 高级用户（想开发集成）
```
README.md → PROJECT_SUMMARY.md → 代码研究 → 开发集成
预计时间：4小时+
```

## ✅ 文档检查清单

在开始前，你已经检查过：

- [ ] 了解项目是做什么的（README.md简介部分）
- [ ] 知道如何安装（BEGINNER_GUIDE.md或QUICKSTART.md）
- [ ] 知道如何获取API密钥（BEGINNER_GUIDE.md）
- [ ] 知道如何启动应用（QUICKSTART.md）
- [ ] 知道如何处理文件（应用内教程）
- [ ] 知道如何导出结果（README.md使用指南）
- [ ] 知道遇到问题怎么办（常见问题部分）

## 🎓 持续学习

### 深入学习建议

1. **第1周**：实际操作，熟悉基本功能
2. **第2周**：探索高级功能，优化工作流
3. **第3周**：学习技术细节，尝试集成
4. **第4周**：自定义配置，适配业务需求

### 推荐资源

- 💻 **代码注释**：查看src/目录的源代码
- 📝 **日志分析**：查看temp/logs/目录的日志
- 🧪 **测试脚本**：运行test_modules.py学习
- 📚 **外部文档**：查看上面的"外部资源"

## 🌟 一句话总结每个文档

| 文档 | 一句话总结 |
|------|---------|
| BEGINNER_GUIDE.md | 从零开始一步步学习安装和使用 |
| QUICKSTART.md | 快速上手的最小化指南 |
| README.md | 项目的完整功能和技术文档 |
| CHANGELOG.md | 项目的版本历史和更新记录 |
| PROJECT_SUMMARY.md | 项目的开发完成情况总结 |
| 本文件 | 各个文档的导航和查找指南 |

---

## 🚀 立即开始

**第一次使用？** → 打开 [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)

**已准备好？** → 打开 [QUICKSTART.md](QUICKSTART.md)

**想完整了解？** → 打开 [README.md](README.md)

**需要帮助？** → 查看"获取帮助"部分

---

**最后更新**：2026-03-26  
**文档版本**：v1.0.0  
**难度等级**：初级～高级  
**预计总学习时间**：30分钟～4小时（取决于你的需求）
