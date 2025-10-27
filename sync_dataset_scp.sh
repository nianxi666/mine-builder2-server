#!/bin/bash
REMOTE="root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com"
PASSWORD="liu20062020"
LOCAL_DIR="/home/engine/project/dataset_gemini"
REMOTE_DIR="/gemini/code/dataset_live"

echo "=========================================="
echo "🔄 SCP数据同步 (修复版)"
echo "=========================================="

# 创建远程目录
sshpass -p "$PASSWORD" ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE" "mkdir -p $REMOTE_DIR" 2>&1 | grep -v "Warning:"

while true; do
    if [ ! -d "$LOCAL_DIR" ]; then
        echo "等待本地数据..."
        sleep 30
        continue
    fi
    
    LOCAL_SAMPLES=$(ls -d $LOCAL_DIR/sample_* 2>/dev/null | wc -l)
    
    if [ $LOCAL_SAMPLES -eq 0 ]; then
        echo "等待样本生成..."
        sleep 30
        continue
    fi
    
    REMOTE_SAMPLES=$(sshpass -p "$PASSWORD" ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE" "ls -d $REMOTE_DIR/sample_* 2>/dev/null | wc -l" 2>&1 | grep -v "Warning:" | tail -1)
    
    if [ -z "$REMOTE_SAMPLES" ] || [ "$REMOTE_SAMPLES" == "" ]; then
        REMOTE_SAMPLES=0
    fi
    
    NEW=$((LOCAL_SAMPLES - REMOTE_SAMPLES))
    
    if [ $NEW -gt 0 ]; then
        echo "[$(date '+%H:%M:%S')] 同步: 本地$LOCAL_SAMPLES 远程$REMOTE_SAMPLES 新增$NEW"
        
        # 使用tar+scp传输（更可靠）
        cd $LOCAL_DIR
        tar czf /tmp/new_samples.tar.gz sample_* 2>/dev/null
        sshpass -p "$PASSWORD" scp -P 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/new_samples.tar.gz "$REMOTE:/tmp/" 2>&1 | grep -v "Warning:"
        sshpass -p "$PASSWORD" ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE" "cd $REMOTE_DIR && tar xzf /tmp/new_samples.tar.gz && rm /tmp/new_samples.tar.gz" 2>&1 | grep -v "Warning:"
        rm /tmp/new_samples.tar.gz
        
        echo "✅ 同步完成"
    else
        echo -n "."
    fi
    
    sleep 60
done
