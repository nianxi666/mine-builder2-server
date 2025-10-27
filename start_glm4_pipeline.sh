#!/bin/bash
# 在远程GPU服务器上使用GLM-4.6生成数据并训练

cd /gemini/code/upload_package

echo "=========================================="
echo "🚀 GLM-4.6 完整训练管道"
echo "=========================================="
echo ""

# 安装openai包
echo "📦 安装依赖..."
python3 -m pip install --break-system-packages -q openai 2>&1 | tail -3
echo "✅ 依赖已安装"
echo ""

# 启动数据生成（后台）
echo "📊 启动GLM-4.6数据生成..."
screen -dmS data_gen bash -c '
cd /gemini/code/upload_package
python3 generate_dataset_glm4.py \
  --num-samples 500 \
  --output-dir /gemini/code/dataset_glm4 \
  2>&1 | tee /gemini/code/data_gen_glm4.log
'
echo "✅ 数据生成已在screen中启动"
echo ""

# 等待50个样本
echo "⏳ 等待50个初始样本（约15分钟）..."
while true; do
    SAMPLES=$(ls -d /gemini/code/dataset_glm4/sample_* 2>/dev/null | wc -l)
    echo -ne "\r   当前: $SAMPLES/50 个样本"
    
    if [ $SAMPLES -ge 50 ]; then
        echo ""
        break
    fi
    
    sleep 30
done

echo "✅ 初始数据已就绪"
echo ""

# 启动增量训练
echo "🏋️  启动增量训练..."
screen -dmS training_glm4 bash -c '
cd /gemini/code/upload_package
python3 train_incremental.py \
  --dataset-dir /gemini/code/dataset_glm4 \
  --output-dir /gemini/code/outputs_glm4 \
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
  --num-workers 4 \
  2>&1 | tee /gemini/code/training_glm4.log
'
echo "✅ 训练已在screen中启动"
echo ""

echo "=========================================="
echo "✅ 管道已启动！"
echo ""
echo "监控命令:"
echo "  数据生成: screen -r data_gen"
echo "  训练进度: screen -r training_glm4"
echo ""
echo "日志文件:"
echo "  数据: /gemini/code/data_gen_glm4.log"
echo "  训练: /gemini/code/training_glm4.log"
echo ""
echo "Screen列表:"
screen -ls
echo "=========================================="
