#!/bin/bash
# 远程增量训练启动脚本

cd /gemini/code/upload_package

echo "=========================================="
echo "🚀 启动增量训练"
echo "=========================================="
echo ""

# 创建screen会话
screen -dmS training_live bash -c '
python3 train_incremental.py \
  --dataset-dir /gemini/code/dataset_live \
  --output-dir /gemini/code/outputs_live \
  --model-size small \
  --batch-size 8 \
  --max-epochs 200 \
  --lr 1e-4 \
  --use-amp \
  --min-samples 50 \
  --refresh-interval 60 \
  --save-every 100 \
  --inference-every 10 \
  --inference-samples 2 \
  --inference-steps 50 \
  --num-workers 4 2>&1 | tee /gemini/code/training_live.log
'

echo "✅ 增量训练已在screen中启动"
echo "查看: screen -r training_live"
screen -ls
