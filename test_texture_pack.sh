#!/bin/bash
echo "=========================================="
echo "🎨 测试材质包功能"
echo "=========================================="

# 启动服务器
source .venv/bin/activate
python server.py > /tmp/texture_test.log 2>&1 &
SERVER_PID=$!
sleep 4

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ 服务器启动失败"
    cat /tmp/texture_test.log
    exit 1
fi

echo "✅ 服务器已启动 (PID: $SERVER_PID)"
echo ""

# 测试 /api/files 端点
echo "1️⃣  测试文件扫描 API"
response=$(curl -s http://127.0.0.1:5000/api/files)
echo "$response" | python -m json.tool > /tmp/files_response.json 2>/dev/null

# 检查材质包
if echo "$response" | grep -q '"texture"'; then
    echo "   ✅ 材质包在API响应中找到"
    
    # 检查是否有data字段
    if echo "$response" | grep -q '"data"'; then
        echo "   ✅ 材质包包含data字段"
        
        # 检查data长度
        data_length=$(echo "$response" | grep -o '"data"[^}]*' | wc -c)
        echo "   ✅ 材质包data长度: $data_length 字符"
        
        if [ $data_length -gt 1000 ]; then
            echo "   ✅ 材质包数据看起来完整"
        else
            echo "   ⚠️  材质包数据可能不完整"
        fi
    else
        echo "   ❌ 材质包缺少data字段"
    fi
    
    # 显示材质包信息
    echo ""
    echo "   材质包详情:"
    cat /tmp/files_response.json | python -c "
import sys, json
data = json.load(sys.stdin)
if 'texture' in data:
    tex = data['texture']
    print(f\"      名称: {tex.get('name', 'N/A')}\")
    print(f\"      MIME类型: {tex.get('mimeType', 'N/A')}\")
    data_len = len(tex.get('data', ''))
    print(f\"      数据大小: {data_len:,} 字符 (~{data_len*3//4:,} 字节)\")
" 2>/dev/null || echo "      无法解析JSON"
else
    echo "   ❌ 材质包未在API响应中找到"
fi

# 检查日志
echo ""
echo "2️⃣  检查服务器日志"
echo ""
grep -i "材质\|texture\|zip" /tmp/texture_test.log | tail -10

# 清理
echo ""
echo "=========================================="
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "✅ 测试完成"
echo "=========================================="
