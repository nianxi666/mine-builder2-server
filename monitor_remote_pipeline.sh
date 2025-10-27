#!/bin/bash
# 监控远程GLM-4.6训练管道

REMOTE="root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com"
PASSWORD="liu20062020"

while true; do
    clear
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    echo "📊 GLM-4.6训练管道实时监控"
    echo "=========================================="
    echo ""
    
    # 获取远程状态
    sshpass -p "$PASSWORD" ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE" bash << 'REMOTE_CMD' 2>&1 | grep -v "Warning:"
    
    echo "📦 数据生成状态:"
    if screen -ls | grep data_gen > /dev/null; then
        echo "   ✅ 运行中"
        SAMPLES=$(ls -d /gemini/code/dataset_glm4/sample_* 2>/dev/null | wc -l)
        echo "   已生成: $SAMPLES 个样本"
        tail -3 /gemini/code/data_gen_glm4.log 2>/dev/null | sed 's/^/   /'
    else
        echo "   ❌ 未运行"
    fi
    echo ""
    
    echo "🏋️  训练状态:"
    if screen -ls | grep training_glm4 > /dev/null; then
        echo "   ✅ 运行中"
        tail -5 /gemini/code/training_glm4.log 2>/dev/null | sed 's/^/   /'
    else
        echo "   ⏳ 等待启动（需要50个样本）"
    fi
    echo ""
    
    echo "📂 输出文件:"
    if [ -d "/gemini/code/outputs_glm4" ]; then
        CHECKPOINTS=$(ls /gemini/code/outputs_glm4/checkpoints/*.pt 2>/dev/null | wc -l)
        INFERENCES=$(ls /gemini/code/outputs_glm4/inference_samples/*.json 2>/dev/null | wc -l)
        echo "   Checkpoints: $CHECKPOINTS 个"
        echo "   推理样本: $INFERENCES 个"
    else
        echo "   等待创建..."
    fi
    echo ""
    
    echo "📊 Screen会话:"
    screen -ls 2>&1 | grep -E "data_gen|training_glm4|Socket" | sed 's/^/   /'
    
REMOTE_CMD
    
    echo ""
    echo "=========================================="
    echo "自动刷新中... (Ctrl+C 退出)"
    sleep 30
done
