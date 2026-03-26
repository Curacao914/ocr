#!/bin/bash

# GLM-OCR 快速启动脚本

echo "========================================="
echo "GLM-OCR 文档转换工具 - 快速启动"
echo "========================================="
echo ""

# 检查Python环境
echo "1. 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    echo ""
    echo "按 Enter 键关闭此窗口..."
    read -r
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ 找到Python3: $python_version"
echo ""

# 检查依赖
echo "2. 检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ 未找到requirements.txt文件"
    echo ""
    echo "按 Enter 键关闭此窗口..."
    read -r
    exit 1
fi

pip3 list | grep -q "zai-sdk" || echo "⚠️  建议先运行: pip3 install -r requirements.txt"
echo ""

# 检查.env文件
echo "3. 配置检查..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "❌ 缺少.env文件"
        echo "请复制.env.example到.env并填入API密钥:"
        echo "  cp .env.example .env"
        echo "  编辑.env文件，填入ZHIPU_API_KEY"
        echo ""
        echo "按 Enter 键关闭此窗口..."
        read -r
        exit 1
    fi
fi

# 检查API密钥
api_key=$(grep '^ZHIPU_API_KEY=' .env | cut -d '=' -f 2)
if [ -z "$api_key" ] || [ "$api_key" = "your_api_key_here" ]; then
    echo "❌ API密钥未配置或为默认值"
    echo "请在.env文件中设置有效的API密钥"
    echo ""
    echo "按 Enter 键关闭此窗口..."
    read -r
    exit 1
fi
echo "✓ API密钥已配置"
echo ""

# 避免localhost请求误走系统代理
if [ -n "$NO_PROXY" ]; then
    export NO_PROXY="$NO_PROXY,localhost,127.0.0.1,::1"
else
    export NO_PROXY="localhost,127.0.0.1,::1"
fi
export no_proxy="$NO_PROXY"

# 创建必要的目录
echo "4. 创建目录..."
mkdir -p output temp logs
echo "✓ 目录检查完成"
echo ""

# 启动应用
echo "5. 启动应用..."
echo "========================================="
echo "应用正在启动..."
echo "请在浏览器中打开: http://localhost:7860"
echo "按 Ctrl+C 停止应用"
echo "========================================="
echo ""

python3 main.py

# 脚本结束后保持终端打开
echo ""
echo "========================================="
echo "应用已关闭"
echo "按 Enter 键关闭此窗口..."
echo "========================================="
read -r
