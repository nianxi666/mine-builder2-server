#!/bin/bash

echo "=========================================="
echo "🎨 材质包功能测试"
echo "=========================================="
echo ""
echo "正在启动服务器..."
echo ""

# 启动服务器
source .venv/bin/activate 2>/dev/null || true
python server.py &
SERVER_PID=$!

# 等待启动
sleep 3

echo ""
echo "=========================================="
echo "✅ 服务器已启动！"
echo "=========================================="
echo ""
echo "请在浏览器中访问以下地址进行测试："
echo ""
echo "  1. 测试页面："
echo "     http://127.0.0.1:5000/test-texture"
echo ""
echo "  2. 主页面："
echo "     http://127.0.0.1:5000/"
echo ""
echo "测试步骤："
echo "  1. 打开测试页面"
echo "  2. 依次点击4个测试按钮"
echo "  3. 查看每个测试的结果"
echo "  4. 如果有失败，复制错误信息"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

# 等待用户
wait $SERVER_PID
