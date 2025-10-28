#!/bin/bash
# 持续同步数据集到远程服务器

REMOTE="root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com"
PASSWORD="liu20062020"
LOCAL_DIR="/home/engine/project/dataset_gemini"
REMOTE_DIR="/gemini/code/dataset_live"

echo "=========================================="
echo "🔄 数据集持续同步"
echo "=========================================="
echo "本地: $LOCAL_DIR"
echo "远程: $REMOTE:$REMOTE_DIR"
echo ""

# 创建远程目录
sshpass -p "$PASSWORD" ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE" "mkdir -p $REMOTE_DIR" 2>&1 | grep -v "Warning:"

SYNC_COUNT=0

while true; do
    # 检查本地数据
    if [ ! -d "$LOCAL_DIR" ]; then
        echo "等待本地数据目录创建..."
        sleep 10
        continue
    fi
    
    LOCAL_SAMPLES=$(ls -d $LOCAL_DIR/sample_* 2>/dev/null | wc -l)
    
    if [ $LOCAL_SAMPLES -eq 0 ]; then
        echo "等待数据生成..."
        sleep 10
        continue
    fi
    
    # 检查远程数据
    REMOTE_SAMPLES=$(sshpass -p "$PASSWORD" ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE" "ls -d $REMOTE_DIR/sample_* 2>/dev/null | wc -l" 2>&1 | grep -v "Warning:" | tail -1)
    
    if [ -z "$REMOTE_SAMPLES" ]; then
        REMOTE_SAMPLES=0
    fi
    
    NEW_SAMPLES=$((LOCAL_SAMPLES - REMOTE_SAMPLES))
    
    if [ $NEW_SAMPLES -gt 0 ]; then
        SYNC_COUNT=$((SYNC_COUNT + 1))
        echo "[$(date '+%H:%M:%S')] 🔄 同步 #$SYNC_COUNT: 本地${LOCAL_SAMPLES}个，远程${REMOTE_SAMPLES}个，新增${NEW_SAMPLES}个"
        
        # 同步新数据
        sshpass -p "$PASSWORD" rsync -avz --progress -e "ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
            $LOCAL_DIR/ $REMOTE:$REMOTE_DIR/ 2>&1 | grep -v "Warning:" | tail -5
        
        echo "✅ 同步完成"
    else
        echo -n "."
    fi
    
    # 每30秒检查一次
    sleep 30
done
