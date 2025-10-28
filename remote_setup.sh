#!/bin/bash
# 远程服务器设置脚本 - 在服务器上运行

set -e

cd /gemini/code/upload_package

echo "=========================================="
echo "🚀 设置Minecraft DiT训练环境"
echo "=========================================="
echo ""

# 1. 手动安装pip
echo "📦 步骤1: 安装pip..."
if ! python3 -m pip --version 2>/dev/null; then
    wget -q https://bootstrap.pypa.io/get-pip.py
    python3 get-pip.py --break-system-packages 2>&1 | tail -3
    rm get-pip.py
fi
python3 -m pip --version
echo "✅ pip已安装"
echo ""

# 2. 安装依赖
echo "📦 步骤2: 安装Python依赖..."
python3 -m pip install --break-system-packages torch torchvision --index-url https://download.pytorch.org/whl/cu118 2>&1 | tail -5
python3 -m pip install --break-system-packages google-generativeai numpy tqdm 2>&1 | tail -3
echo "✅ 依赖已安装"
echo ""

# 3. 测试PyTorch
echo "🔍 步骤3: 测试PyTorch和CUDA..."
python3 << 'ENDPY'
import torch
print(f"✅ PyTorch版本: {torch.__version__}")
print(f"✅ CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✅ GPU数量: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"   显存: {torch.cuda.get_device_properties(i).total_memory / 1e9:.2f} GB")
ENDPY
echo ""

# 4. 生成小数据集测试
echo "📊 步骤4: 生成测试数据集（10个样本）..."
python3 create_synthetic_dataset.py --num-samples 10 --output-dir dataset_test
echo "✅ 测试数据集生成完成"
echo ""

# 5. 显示下一步
echo "=========================================="
echo "✅ 环境设置完成！"
echo ""
echo "下一步操作："
echo ""
echo "1. 生成完整数据集（在screen中）："
echo "   screen -S dataset"
echo "   python3 generate_premium_dataset.py --num-samples 1000"
echo "   # Ctrl+A+D 挂起"
echo ""
echo "2. 或使用合成数据快速训练："
echo "   python3 create_synthetic_dataset.py --num-samples 200"
echo ""
echo "3. 开始训练（在screen中）："
echo "   screen -S training"
echo "   python3 train.py --dataset-dir dataset --batch-size 8 --epochs 50 --use-amp"
echo "   # Ctrl+A+D 挂起"
echo ""
echo "4. 查看训练进度："
echo "   screen -r training"
echo ""
echo "=========================================="
