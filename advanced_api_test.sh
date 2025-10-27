#!/bin/bash
echo "=========================================="
echo "🔬 高级API交互测试"
echo "=========================================="

# 启动服务器
source .venv/bin/activate
python server.py > /tmp/server.log 2>&1 &
SERVER_PID=$!
sleep 4

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ 服务器启动失败"
    exit 1
fi

echo "✅ 服务器已启动 (PID: $SERVER_PID)"
echo ""

# 测试存档导出
echo "1️⃣  测试存档导出 POST /api/save/export"
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "voxelData": {"0,0,0": {"blockId": 1, "metaData": 0}},
        "chatHistory": [{"role": "user", "content": "测试"}],
        "agentState": {"is_running": false}
    }' \
    http://127.0.0.1:5000/api/save/export \
    --output /tmp/test_save.zip)
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ] && [ -f /tmp/test_save.zip ]; then
    echo "   ✅ 导出成功，状态码: $http_code"
    ls -lh /tmp/test_save.zip
    echo "   检查ZIP内容:"
    unzip -l /tmp/test_save.zip 2>/dev/null | head -10
else
    echo "   ❌ 导出失败，状态码: $http_code"
fi

# 测试存档导入
echo ""
echo "2️⃣  测试存档导入 POST /api/save/import"
if [ -f /tmp/test_save.zip ]; then
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -F "file=@/tmp/test_save.zip" \
        http://127.0.0.1:5000/api/save/import)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    echo "   状态码: $http_code"
    if [ "$http_code" = "200" ]; then
        echo "   ✅ 导入成功"
        echo "$body" | python -m json.tool 2>/dev/null | head -20
    else
        echo "   ❌ 导入失败"
        echo "$body"
    fi
fi

# 测试AI代理继续
echo ""
echo "3️⃣  测试继续代理 POST /api/agent/continue"
response=$(curl -s -w "\n%{http_code}" -X POST \
    http://127.0.0.1:5000/api/agent/continue)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

echo "   状态码: $http_code"
if [ "$http_code" = "200" ]; then
    echo "   ✅ 成功"
    echo "   $body"
fi

# 再次检查状态
echo ""
echo "4️⃣  验证代理状态变化 GET /api/agent/state"
response=$(curl -s http://127.0.0.1:5000/api/agent/state)
echo "$response" | python -m json.tool 2>/dev/null

# 测试并发请求
echo ""
echo "5️⃣  测试并发请求（10个同时请求）"
for i in {1..10}; do
    curl -s http://127.0.0.1:5000/api/agent/state > /dev/null &
done
wait
echo "   ✅ 10个并发请求完成"

# 测试大型POST数据
echo ""
echo "6️⃣  测试大型POST数据"
large_data='{"voxelData": {'
for i in {0..100}; do
    large_data="${large_data}\"$i,0,0\": {\"blockId\": 1, \"metaData\": 0}"
    if [ $i -lt 100 ]; then
        large_data="${large_data},"
    fi
done
large_data="${large_data}}}"

response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$large_data" \
    http://127.0.0.1:5000/api/save/export \
    -o /dev/null)
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
    echo "   ✅ 大数据POST成功: $http_code"
else
    echo "   ❌ 大数据POST失败: $http_code"
fi

# 性能测试
echo ""
echo "7️⃣  性能测试（100次请求）"
start_time=$(date +%s.%N)
for i in {1..100}; do
    curl -s http://127.0.0.1:5000/api/agent/state > /dev/null
done
end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)
rps=$(echo "100 / $duration" | bc)

echo "   ✅ 100次请求完成"
echo "   总耗时: ${duration}秒"
echo "   平均RPS: ${rps}/秒"

# 测试错误处理
echo ""
echo "8️⃣  测试错误处理"
echo "   测试无效JSON:"
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{invalid json}' \
    http://127.0.0.1:5000/api/save/export)
http_code=$(echo "$response" | tail -n1)
echo "   状态码: $http_code (期望400或500)"

echo "   测试缺少必需参数:"
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{}' \
    http://127.0.0.1:5000/api/validate_key)
http_code=$(echo "$response" | tail -n1)
echo "   状态码: $http_code (期望400)"

# 内存检查
echo ""
echo "9️⃣  检查服务器内存使用"
memory=$(ps -o rss= -p $SERVER_PID 2>/dev/null)
if [ ! -z "$memory" ]; then
    memory_mb=$(echo "scale=2; $memory / 1024" | bc)
    echo "   服务器内存使用: ${memory_mb} MB"
fi

# 清理
echo ""
echo "=========================================="
echo "🧹 清理"
echo "=========================================="
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
rm -f /tmp/test_save.zip
echo "✅ 清理完成"

echo ""
echo "=========================================="
echo "✅ 高级测试完成！"
echo "=========================================="
