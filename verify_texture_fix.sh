#!/bin/bash

echo "=========================================="
echo "🔍 验证材质包功能修复"
echo "=========================================="
echo ""

# 启动服务器
echo "1️⃣  启动服务器..."
source .venv/bin/activate 2>/dev/null || true
python server.py > /tmp/verify_texture.log 2>&1 &
SERVER_PID=$!
sleep 3

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "   ❌ 服务器启动失败"
    cat /tmp/verify_texture.log
    exit 1
fi

echo "   ✅ 服务器已启动 (PID: $SERVER_PID)"
echo ""

# 测试API
echo "2️⃣  测试API端点..."
response=$(curl -s http://127.0.0.1:5000/api/files)
if echo "$response" | grep -q '"texture"'; then
    echo "   ✅ API返回材质包数据"
    texture_data_length=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('texture', {}).get('data', '')))" 2>/dev/null || echo "0")
    echo "   ✅ Base64数据长度: $texture_data_length 字符"
else
    echo "   ❌ API未返回材质包数据"
fi

echo ""
echo "3️⃣  测试JavaScript语法..."
# 检查是否修复了endswith错误
if grep -q "\.endswith(" test_texture_frontend.html; then
    echo "   ❌ 仍然存在 .endswith( 错误（应该是 .endsWith）"
else
    echo "   ✅ JavaScript语法正确（使用 .endsWith）"
fi

echo ""
echo "=========================================="
echo "✅ 验证完成！"
echo "=========================================="
echo ""
echo "现在可以在浏览器中测试："
echo ""
echo "  测试页面: http://127.0.0.1:5000/test-texture"
echo "  主页面:   http://127.0.0.1:5000/"
echo ""
echo "在测试页面中："
echo "  1. 点击 '完整流程测试' 按钮"
echo "  2. 应该看到 '✅ 找到 278 个材质'"
echo "  3. 应该看到 '🎉 所有测试通过！'"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 等待用户
wait $SERVER_PID
