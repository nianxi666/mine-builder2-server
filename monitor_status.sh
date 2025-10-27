#!/bin/bash
# 监控本地和远程状态

echo "=========================================="
echo "📊 实时状态监控"
echo "=========================================="
echo ""

while true; do
    clear
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    
    # 本地数据生成状态
    echo "📦 本地数据生成:"
    if [ -f gemini_generation.pid ]; then
        PID=$(cat gemini_generation.pid)
        if ps -p $PID > /dev/null; then
            echo "   ✅ 运行中 (PID: $PID)"
            LOCAL_SAMPLES=$(ls -d dataset_gemini/sample_* 2>/dev/null | wc -l)
            echo "   已生成: $LOCAL_SAMPLES 个样本"
            tail -3 gemini_generation.log 2>/dev/null | sed 's/^/   /'
        else
            echo "   ❌ 已停止"
        fi
    else
        echo "   ⚠️  未启动"
    fi
    echo ""
    
    # 数据同步状态
    echo "🔄 数据同步:"
    if [ -f dataset_sync.pid ]; then
        PID=$(cat dataset_sync.pid)
        if ps -p $PID > /dev/null; then
            echo "   ✅ 运行中 (PID: $PID)"
            tail -3 dataset_sync.log 2>/dev/null | sed 's/^/   /'
        else
            echo "   ❌ 已停止"
        fi
    else
        echo "   ⚠️  未启动"
    fi
    echo ""
    
    # 远程训练状态
    echo "🏋️  远程训练:"
    REMOTE_STATUS=$(sshpass -p 'liu20062020' ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "screen -ls 2>&1 | grep training_live" 2>&1 | grep -v "Warning:" | head -1)
    
    if [ -n "$REMOTE_STATUS" ]; then
        echo "   ✅ 运行中"
        REMOTE_LOG=$(sshpass -p 'liu20062020' ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "tail -5 /gemini/code/training_live.log 2>&1" 2>&1 | grep -v "Warning:" | tail -3)
        echo "$REMOTE_LOG" | sed 's/^/   /'
    else
        echo "   ⚠️  等待启动或未运行"
    fi
    
    echo ""
    echo "=========================================="
    echo "按 Ctrl+C 退出监控"
    echo ""
    
    sleep 30
done
