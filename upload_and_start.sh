#!/bin/bash
# 上传文件并启动GLM-4.6训练管道

echo "=========================================="
echo "🚀 部署GLM-4.6训练管道"
echo "=========================================="
echo ""

REMOTE="root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com"
PASSWORD="liu20062020"

echo "1. 上传Python脚本..."

# 安装sshpass（如果需要）
if ! command -v sshpass &> /dev/null; then
    echo "   安装sshpass..."
    sudo apt-get install -y sshpass 2>&1 | tail -2
fi

# 上传文件
echo "   上传 generate_dataset_glm4.py..."
sshpass -p "$PASSWORD" scp -P 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    /home/engine/project/generate_dataset_glm4.py \
    "$REMOTE:/gemini/code/upload_package/" 2>&1 | grep -v "Warning:"

echo "   上传 train_incremental.py..."
sshpass -p "$PASSWORD" scp -P 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    /home/engine/project/train_incremental.py \
    "$REMOTE:/gemini/code/upload_package/" 2>&1 | grep -v "Warning:"

echo "   上传 start_glm4_pipeline.sh..."
sshpass -p "$PASSWORD" scp -P 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    /home/engine/project/start_glm4_pipeline.sh \
    "$REMOTE:/gemini/code/upload_package/" 2>&1 | grep -v "Warning:"

echo "✅ 文件已上传"
echo ""

echo "2. 启动远程训练管道..."
sshpass -p "$PASSWORD" ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "$REMOTE" "cd /gemini/code/upload_package && chmod +x start_glm4_pipeline.sh && bash start_glm4_pipeline.sh" 2>&1 | grep -v "Warning:"

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo ""
echo "监控命令:"
echo "  ssh -p 30022 $REMOTE"
echo "  screen -r data_gen      # 数据生成"
echo "  screen -r training_glm4 # 训练"
echo "=========================================="
