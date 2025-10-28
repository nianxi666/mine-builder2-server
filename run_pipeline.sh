#!/bin/bash
# 完整的DiT训练流程脚本

set -e  # 遇到错误立即退出

# 配置
API_KEY="${GEMINI_API_KEY:-AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A}"
NUM_SAMPLES=1000
MODEL_SIZE="small"
BATCH_SIZE=8
EPOCHS=100

echo "=========================================="
echo "DiT Minecraft Voxel Generation Pipeline"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# 步骤1: 生成数据集
echo "Step 1: Generating dataset..."
echo "------------------------------------------"
if [ ! -d "dataset" ] || [ $(ls -1 dataset/sample_* 2>/dev/null | wc -l) -lt $NUM_SAMPLES ]; then
    python3 dataset_generator.py \
        --api-key "$API_KEY" \
        --output-dir dataset \
        --num-samples $NUM_SAMPLES \
        --model gemini-2.0-flash-exp
    echo "Dataset generation complete!"
else
    echo "Dataset already exists with sufficient samples. Skipping..."
fi
echo ""

# 步骤2: 训练模型
echo "Step 2: Training model..."
echo "------------------------------------------"
python3 train.py \
    --dataset-dir dataset \
    --output-dir outputs \
    --model-size $MODEL_SIZE \
    --batch-size $BATCH_SIZE \
    --epochs $EPOCHS \
    --lr 1e-4 \
    --use-amp \
    --save-every 500
echo "Training complete!"
echo ""

# 步骤3: 生成样本
echo "Step 3: Generating samples..."
echo "------------------------------------------"
python3 inference.py \
    --checkpoint outputs/checkpoints/latest.pt \
    --model-size $MODEL_SIZE \
    --num-samples 10 \
    --sampler ddim \
    --num-steps 50 \
    --output-dir generated
echo "Sample generation complete!"
echo ""

echo "=========================================="
echo "Pipeline complete!"
echo "Results saved in:"
echo "  - Dataset: ./dataset"
echo "  - Model: ./outputs"
echo "  - Generated: ./generated"
echo "=========================================="
