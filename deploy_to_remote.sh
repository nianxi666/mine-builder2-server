#!/bin/bash
# 自动部署到远程GPU服务器的脚本

set -e

# 配置
REMOTE_HOST="ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com"
REMOTE_USER="root"
REMOTE_PORT="30022"
REMOTE_DIR="/gemini/code"
PACKAGE_NAME="minecraft_dit.tar.gz"

echo "========================================"
echo "🚀 部署Minecraft DiT到远程GPU服务器"
echo "========================================"
echo ""

# 步骤1: 检查本地包
echo "📦 步骤1: 检查本地代码包..."
if [ ! -f "$PACKAGE_NAME" ]; then
    echo "❌ 找不到 $PACKAGE_NAME"
    echo "请先运行打包命令或使用已有的包"
    exit 1
fi
echo "✅ 找到代码包: $(ls -lh $PACKAGE_NAME | awk '{print $5}')"
echo ""

# 步骤2: 上传
echo "📤 步骤2: 上传代码包到服务器..."
echo "目标: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
echo ""
scp -P $REMOTE_PORT $PACKAGE_NAME ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/
echo "✅ 上传完成！"
echo ""

# 步骤3: 远程设置
echo "🔧 步骤3: 在服务器上设置环境..."
echo ""

ssh -p $REMOTE_PORT ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
set -e

cd /gemini/code

echo "解压代码包..."
tar -xzf minecraft_dit.tar.gz
cd upload_package

echo "检查GPU..."
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

echo "检查Python..."
python3 --version

echo "创建虚拟环境..."
python3 -m venv venv

echo "安装依赖..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -q google-generativeai numpy tqdm

echo "测试PyTorch和CUDA..."
python3 << 'ENDPY'
import torch
print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"显存: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
ENDPY

echo ""
echo "✅ 环境设置完成！"
echo ""
echo "下一步操作："
echo "1. SSH连接到服务器:"
echo "   ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com"
echo ""
echo "2. 进入工作目录:"
echo "   cd /gemini/code/upload_package"
echo "   source venv/bin/activate"
echo ""
echo "3. 生成数据集（在screen中）:"
echo "   screen -S dataset"
echo "   python3 generate_premium_dataset.py --num-samples 1000"
echo "   # 按 Ctrl+A+D 挂起"
echo ""
echo "4. 或使用合成数据快速测试:"
echo "   python3 create_synthetic_dataset.py --num-samples 100"
echo ""
echo "5. 开始训练:"
echo "   screen -S training"
echo "   python3 train.py --batch-size 4 --epochs 100 --use-amp"
echo "   # 按 Ctrl+A+D 挂起"
echo ""
ENDSSH

echo ""
echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo ""
echo "现在可以SSH连接到服务器开始训练了！"
echo ""
echo "SSH命令:"
echo "ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com"
echo ""
