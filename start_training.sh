#!/bin/bash
# 一键启动训练脚本 - 所有文件保存到/gemini/code

set -e

cd /gemini/code/upload_package

echo "=========================================="
echo "🚀 Minecraft DiT 训练启动"
echo "=========================================="
echo ""

# 步骤1: 安装环境
echo "📦 步骤1: 检查并安装环境..."
if ! python3 -c "import torch" 2>/dev/null; then
    echo "安装pip..."
    wget -q https://bootstrap.pypa.io/get-pip.py
    python3 get-pip.py --break-system-packages
    rm get-pip.py
    
    echo "安装PyTorch和依赖..."
    python3 -m pip install --break-system-packages -q torch torchvision --index-url https://download.pytorch.org/whl/cu118
    python3 -m pip install --break-system-packages -q google-generativeai numpy tqdm
fi

python3 -c "import torch; print(f'✅ PyTorch {torch.__version__}'); print(f'✅ CUDA: {torch.cuda.is_available()}')"
echo ""

# 步骤2: 生成数据集
echo "📊 步骤2: 生成训练数据集..."
if [ ! -d "/gemini/code/dataset" ] || [ $(ls -1 /gemini/code/dataset/sample_* 2>/dev/null | wc -l) -lt 50 ]; then
    echo "生成100个合成样本到 /gemini/code/dataset..."
    python3 create_synthetic_dataset.py \
        --num-samples 100 \
        --output-dir /gemini/code/dataset
    echo "✅ 数据集生成完成"
else
    echo "✅ 数据集已存在"
fi
echo ""

# 步骤3: 开始训练
echo "🏋️  步骤3: 开始训练..."
echo "配置:"
echo "  - 数据集: /gemini/code/dataset"
echo "  - 输出: /gemini/code/outputs"
echo "  - 推理样本: /gemini/code/outputs/inference_samples"
echo "  - 模型: small"
echo "  - Batch size: 8"
echo "  - Epochs: 50"
echo "  - 每5步推理一次"
echo ""

python3 train_with_inference.py \
    --dataset-dir /gemini/code/dataset \
    --output-dir /gemini/code/outputs \
    --model-size small \
    --batch-size 8 \
    --epochs 50 \
    --lr 1e-4 \
    --use-amp \
    --save-every 50 \
    --inference-every 5 \
    --inference-samples 2 \
    --inference-steps 10 \
    --num-workers 4

echo ""
echo "=========================================="
echo "✅ 训练完成！"
echo ""
echo "生成的文件:"
echo "  - Checkpoints: /gemini/code/outputs/checkpoints/"
echo "  - 推理样本: /gemini/code/outputs/inference_samples/"
echo ""
echo "查看推理样本:"
echo "  ls -lh /gemini/code/outputs/inference_samples/"
echo ""
echo "=========================================="
