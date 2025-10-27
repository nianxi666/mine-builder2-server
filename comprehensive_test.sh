#!/bin/bash
echo "=========================================="
echo "🧪 Mine Builder 2 Server 全面功能测试"
echo "=========================================="

# 启动服务器（后台运行）
echo ""
echo "1️⃣  启动服务器..."
source .venv/bin/activate
python server.py > /tmp/server.log 2>&1 &
SERVER_PID=$!
echo "   服务器PID: $SERVER_PID"

# 等待服务器启动
echo "   等待服务器启动..."
sleep 4

# 检查服务器是否运行
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "   ❌ 服务器启动失败"
    cat /tmp/server.log
    exit 1
fi
echo "   ✅ 服务器已启动"

echo ""
echo "=========================================="
echo "📡 测试HTTP端点"
echo "=========================================="

# 测试1: 主页
echo ""
echo "2️⃣  测试主页 GET /"
response=$(curl -s -w "\n%{http_code}" http://127.0.0.1:5000/)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
body_length=${#body}

if [ "$http_code" = "200" ]; then
    echo "   ✅ 状态码: $http_code"
    echo "   ✅ 响应长度: $body_length 字符"
    if echo "$body" | grep -q "<!DOCTYPE"; then
        echo "   ✅ 包含DOCTYPE声明"
    fi
    if echo "$body" | grep -q "three.js"; then
        echo "   ✅ 包含Three.js引用"
    fi
    if echo "$body" | grep -q "AI助手"; then
        echo "   ✅ 包含中文内容"
    fi
else
    echo "   ❌ 状态码: $http_code"
fi

# 测试2: /api/files
echo ""
echo "3️⃣  测试文件扫描 GET /api/files"
response=$(curl -s -w "\n%{http_code}" http://127.0.0.1:5000/api/files)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "   ✅ 状态码: $http_code"
    echo "   ✅ 响应数据:"
    echo "$body" | python -m json.tool 2>/dev/null || echo "$body"
else
    echo "   ❌ 状态码: $http_code"
fi

# 测试3: /api/agent/state
echo ""
echo "4️⃣  测试AI代理状态 GET /api/agent/state"
response=$(curl -s -w "\n%{http_code}" http://127.0.0.1:5000/api/agent/state)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "   ✅ 状态码: $http_code"
    echo "   ✅ 响应数据:"
    echo "$body" | python -m json.tool 2>/dev/null || echo "$body"
else
    echo "   ❌ 状态码: $http_code"
fi

# 测试4: /api/validate_key (POST)
echo ""
echo "5️⃣  测试API密钥验证 POST /api/validate_key"
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"apiKey":"invalid_key_for_test"}' \
    http://127.0.0.1:5000/api/validate_key)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

echo "   状态码: $http_code"
echo "   响应: $body"

# 测试5: /api/agent/pause (POST)
echo ""
echo "6️⃣  测试暂停代理 POST /api/agent/pause"
response=$(curl -s -w "\n%{http_code}" -X POST \
    http://127.0.0.1:5000/api/agent/pause)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "   ✅ 状态码: $http_code"
    echo "   响应: $body"
else
    echo "   ❌ 状态码: $http_code"
fi

# 测试6: 测试HEAD请求
echo ""
echo "7️⃣  测试HEAD请求"
http_code=$(curl -s -I -w "%{http_code}" -o /dev/null http://127.0.0.1:5000/)
if [ "$http_code" = "200" ]; then
    echo "   ✅ HEAD请求成功: $http_code"
else
    echo "   ❌ HEAD请求失败: $http_code"
fi

# 测试7: 测试404
echo ""
echo "8️⃣  测试404错误处理"
http_code=$(curl -s -w "%{http_code}" -o /dev/null http://127.0.0.1:5000/nonexistent)
if [ "$http_code" = "404" ]; then
    echo "   ✅ 404处理正确: $http_code"
else
    echo "   ⚠️  404状态码: $http_code"
fi

# 检查服务器日志
echo ""
echo "=========================================="
echo "📋 服务器日志（最后20行）"
echo "=========================================="
tail -20 /tmp/server.log

# 清理
echo ""
echo "=========================================="
echo "🧹 清理"
echo "=========================================="
echo "   关闭服务器..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "   ✅ 服务器已关闭"

echo ""
echo "=========================================="
echo "✅ 测试完成！"
echo "=========================================="
