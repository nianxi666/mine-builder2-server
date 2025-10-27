#!/bin/bash
# 快速开始脚本 - 生成10个样本进行测试

set -e

API_KEY="${GEMINI_API_KEY:-AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A}"

echo "=========================================="
echo "Quick Start - Test with 10 samples"
echo "=========================================="
echo ""

# 1. 测试系统
echo "Testing system..."
python3 test_system.py
echo ""

# 2. 生成小数据集（10个样本用于测试）
echo "Generating test dataset (10 samples)..."
python3 dataset_generator.py \
    --api-key "$API_KEY" \
    --output-dir dataset_test \
    --num-samples 10 \
    --model gemini-2.0-flash-exp
echo ""

# 3. 快速训练测试（只训练5个epoch）
echo "Quick training test (5 epochs)..."
python3 train.py \
    --dataset-dir dataset_test \
    --output-dir outputs_test \
    --model-size small \
    --batch-size 2 \
    --epochs 5 \
    --lr 1e-4 \
    --save-every 100
echo ""

# 4. 测试推理
echo "Testing inference..."
python3 inference.py \
    --checkpoint outputs_test/checkpoints/latest.pt \
    --model-size small \
    --num-samples 2 \
    --sampler ddim \
    --num-steps 20 \
    --output-dir generated_test
echo ""

echo "=========================================="
echo "Quick start complete!"
echo ""
echo "Next steps for full training:"
echo "  1. Generate full dataset (1000 samples):"
echo "     python3 dataset_generator.py --num-samples 1000"
echo ""
echo "  2. Train full model:"
echo "     python3 train.py --epochs 100"
echo ""
echo "  3. Generate results:"
echo "     python3 inference.py --num-samples 20"
echo "=========================================="
