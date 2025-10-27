# 🚀 远程GPU服务器部署指南

## 📋 服务器信息

```bash
SSH: ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
内存: 16GB
显存: 6GB (GTX 1060 或类似)
工作目录: /gemini/code
```

## 🎯 完整部署流程

### 步骤1: 上传代码包

在**本地机器**执行：

```bash
cd /home/engine/project

# 已经打包好了
ls -lh minecraft_dit.tar.gz  # 应该看到40KB的文件

# 上传到远程服务器
scp -P 30022 minecraft_dit.tar.gz \
  root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com:/gemini/code/
```

### 步骤2: SSH连接到服务器

```bash
ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
```

### 步骤3: 在服务器上解压并设置环境

```bash
# 进入工作目录
cd /gemini/code

# 解压
tar -xzf minecraft_dit.tar.gz
cd upload_package

# 检查GPU
nvidia-smi

# 检查Python版本
python3 --version

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖（根据6GB显存优化）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install google-generativeai numpy tqdm

# 测试PyTorch和CUDA
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### 步骤4: 生成数据集（在服务器上）

由于服务器性能更好，直接在服务器上生成数据集：

```bash
# 使用screen挂起会话
screen -S dataset_gen

# 生成1000个样本（约12-20小时）
python3 generate_premium_dataset.py \
  --api-key AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A \
  --num-samples 1000 \
  --output-dir dataset

# 按 Ctrl+A+D 挂起screen
# 查看进度: screen -r dataset_gen
```

**或者快速测试（生成50个样本）：**

```bash
screen -S dataset_test

python3 generate_premium_dataset.py \
  --api-key AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A \
  --num-samples 50 \
  --output-dir dataset_test

# Ctrl+A+D 挂起
```

### 步骤5: 开始训练（6GB显存优化配置）

**重要：6GB显存需要小心配置！**

#### 方案A: Small模型 + 小batch（最安全）

```bash
screen -S training

python3 train.py \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size small \
  --batch-size 2 \
  --epochs 100 \
  --lr 1e-4 \
  --use-amp \
  --num-workers 2

# Ctrl+A+D 挂起
# 查看: screen -r training
```

#### 方案B: Small模型 + 中batch（推荐）

```bash
python3 train.py \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size small \
  --batch-size 4 \
  --epochs 150 \
  --lr 1e-4 \
  --use-amp \
  --num-workers 4
```

#### 如果显存不够，调整参数：

```bash
# 最小配置
python3 train.py \
  --dataset-dir dataset \
  --model-size small \
  --batch-size 1 \
  --epochs 100 \
  --use-amp
```

### 步骤6: 监控训练

#### 查看训练进度

```bash
# 列出所有screen会话
screen -ls

# 恢复训练会话
screen -r training

# 查看日志（如果使用nohup）
tail -f training.log

# 查看GPU使用
watch -n 1 nvidia-smi
```

#### 检查checkpoints

```bash
ls -lh outputs/checkpoints/
cat outputs/config.json
```

### 步骤7: 训练完成后推理

```bash
screen -S inference

python3 inference.py \
  --checkpoint outputs/checkpoints/latest.pt \
  --model-size small \
  --num-samples 20 \
  --sampler ddim \
  --num-steps 50 \
  --output-dir generated

# Ctrl+A+D 挂起
```

## 📊 Screen命令速查

```bash
# 创建新会话
screen -S 会话名

# 列出所有会话
screen -ls

# 恢复会话
screen -r 会话名

# 挂起会话（在screen内）
Ctrl+A+D

# 杀死会话
screen -X -S 会话名 quit

# 查看所有窗口
Ctrl+A+"
```

## 🔧 内存/显存不够时的解决方案

### 如果训练时OOM（显存不足）

1. **减小batch size**
```bash
--batch-size 1  # 最小
```

2. **使用混合精度**
```bash
--use-amp  # 必须启用
```

3. **减少workers**
```bash
--num-workers 1
```

4. **监控显存使用**
```bash
watch -n 0.5 nvidia-smi
```

### 如果内存不够（16GB应该够用）

```bash
# 减少数据加载workers
--num-workers 2

# 检查内存使用
free -h
htop
```

### 显存使用预估

| 配置 | 显存需求 | 适用 |
|------|----------|------|
| Small, batch=1 | ~2GB | ✅ 6GB够用 |
| Small, batch=2 | ~3GB | ✅ 6GB够用 |
| Small, batch=4 | ~4-5GB | ✅ 6GB够用（紧张）|
| Small, batch=8 | ~6-7GB | ❌ 6GB不够 |
| Base, batch=1 | ~4GB | ⚠️ 可能紧张 |

## 🎨 使用合成数据快速测试（无需API）

如果想快速开始，可以使用合成数据：

```bash
# 生成100个合成样本（秒级完成）
python3 create_synthetic_dataset.py \
  --num-samples 100 \
  --output-dir dataset_synthetic

# 快速训练测试（10分钟）
python3 train.py \
  --dataset-dir dataset_synthetic \
  --model-size small \
  --batch-size 4 \
  --epochs 10 \
  --use-amp
```

## 📈 预期时间

### 数据集生成（使用Gemini API）
- 50个样本: ~2-3小时
- 100个样本: ~4-6小时
- 1000个样本: ~12-20小时

### 训练时间（6GB显存，Small模型）
- 10 epochs: ~30分钟
- 50 epochs: ~2-3小时
- 100 epochs: ~4-6小时
- 200 epochs: ~8-12小时

### 推理时间
- DDIM 50步: ~10秒/样本
- DDPM 1000步: ~3-5分钟/样本

## 🎯 推荐工作流

### 快速测试流程（1小时）

```bash
# 1. 合成数据（1分钟）
python3 create_synthetic_dataset.py --num-samples 100

# 2. 快速训练（30分钟）
screen -S test_train
python3 train.py --dataset-dir dataset_synthetic --epochs 30 --batch-size 4 --use-amp
# Ctrl+A+D

# 3. 推理测试（5分钟）
python3 inference.py --checkpoint outputs/checkpoints/latest.pt --num-samples 10
```

### 完整训练流程（24-48小时）

```bash
# 1. 生成高质量数据集（12-20小时）
screen -S dataset
python3 generate_premium_dataset.py --num-samples 1000
# Ctrl+A+D

# 等待完成后...

# 2. 完整训练（8-12小时）
screen -S training
python3 train.py --dataset-dir dataset --epochs 100 --batch-size 4 --use-amp
# Ctrl+A+D

# 3. 生成结果
python3 inference.py --checkpoint outputs/checkpoints/latest.pt --num-samples 50
```

## 🔥 一键启动脚本

创建快速启动脚本：

```bash
cat > quick_train.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 启动Minecraft DiT训练..."

# 激活虚拟环境
source venv/bin/activate

# 检查数据集
if [ ! -d "dataset/sample_0000" ]; then
    echo "📦 生成合成数据集..."
    python3 create_synthetic_dataset.py --num-samples 100
fi

# 开始训练
echo "🏋️ 开始训练..."
python3 train.py \
    --dataset-dir dataset \
    --output-dir outputs \
    --model-size small \
    --batch-size 4 \
    --epochs 50 \
    --use-amp \
    --num-workers 2

echo "✅ 训练完成！"
EOF

chmod +x quick_train.sh

# 在screen中运行
screen -S training ./quick_train.sh
```

## 🆘 常见问题

### 1. SSH连接断开怎么办？
使用screen挂起会话，重新连接后用`screen -r`恢复

### 2. 显存OOM
减小batch_size到1或2

### 3. 训练loss不下降
- 检查数据集质量
- 增加epochs
- 调整学习率

### 4. API限流
- 脚本会自动重试
- 或使用合成数据集

### 5. 查看训练进度
```bash
screen -r training  # 实时查看
# 或者
tail -f outputs/train.log  # 如果有日志
```

## 📞 需要帮助？

如果遇到问题：
1. 检查`screen -ls`看进程是否还在运行
2. 查看`nvidia-smi`检查GPU使用
3. 查看`free -h`检查内存
4. 检查日志文件

---

**准备就绪！现在可以开始部署了！** 🚀

建议流程：
1. 上传代码包 (scp命令)
2. SSH连接服务器
3. 解压并安装依赖
4. 使用screen启动数据集生成
5. 数据集完成后启动训练
6. 定期检查进度
