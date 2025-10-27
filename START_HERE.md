# 🚀 开始训练 - 快速指南

## 📦 已准备好的文件

```
✅ minecraft_dit.tar.gz (40KB) - 完整代码包
✅ deploy_to_remote.sh - 自动部署脚本  
✅ REMOTE_DEPLOYMENT_GUIDE.md - 详细部署文档
✅ 3个验证过的高质量样本
```

## 🎯 三步开始训练

### 方案A：手动部署（推荐，更可控）

#### 第1步：上传代码包

```bash
cd /home/engine/project

scp -P 30022 minecraft_dit.tar.gz \
  root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com:/gemini/code/
```

#### 第2步：SSH连接到服务器

```bash
ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
```

#### 第3步：在服务器上执行

```bash
# 进入目录
cd /gemini/code

# 解压
tar -xzf minecraft_dit.tar.gz
cd upload_package

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install google-generativeai numpy tqdm

# 测试GPU
python3 -c "import torch; print('CUDA:', torch.cuda.is_available())"

# 快速测试：生成100个合成样本（1分钟）
python3 create_synthetic_dataset.py --num-samples 100 --output-dir dataset

# 开始训练（在screen中）
screen -S training
python3 train.py \
  --dataset-dir dataset \
  --model-size small \
  --batch-size 4 \
  --epochs 50 \
  --use-amp

# 按 Ctrl+A+D 挂起screen
# 稍后用 screen -r training 恢复查看
```

### 方案B：自动部署（需要配置SSH密钥）

```bash
cd /home/engine/project
./deploy_to_remote.sh
```

## 🔧 重要配置（6GB显存）

### 训练参数建议

| 配置 | batch_size | 预计显存 | 训练时间(100 epochs) |
|------|------------|----------|----------------------|
| 最安全 | 2 | 3GB | ~6小时 |
| 推荐 | 4 | 4-5GB | ~4小时 |
| 激进 | 6 | 5-6GB | ~3小时 |

### 完整训练命令

```bash
# 安全配置
python3 train.py --dataset-dir dataset --model-size small --batch-size 2 --epochs 100 --use-amp

# 推荐配置
python3 train.py --dataset-dir dataset --model-size small --batch-size 4 --epochs 100 --use-amp

# 如果OOM，使用
python3 train.py --dataset-dir dataset --model-size small --batch-size 1 --epochs 100 --use-amp
```

## 📊 两种数据集选择

### 选项1：合成数据（推荐快速测试）

**优点**：1分钟生成，无需API
**缺点**：质量一般，用于测试

```bash
python3 create_synthetic_dataset.py --num-samples 100
```

### 选项2：Gemini生成（推荐正式训练）

**优点**：高质量，卓越级建筑
**缺点**：耗时长（12-20小时生成1000个）

```bash
screen -S dataset
python3 generate_premium_dataset.py \
  --api-key AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A \
  --num-samples 1000
# Ctrl+A+D 挂起
```

**快速测试版（50个样本，2-3小时）：**
```bash
python3 generate_premium_dataset.py --num-samples 50
```

## 🎮 Screen使用速查

```bash
# 创建新会话
screen -S 名称

# 列出所有会话
screen -ls

# 恢复会话
screen -r 名称

# 挂起会话（在screen内）
Ctrl+A, 然后按 D

# 滚动查看历史（在screen内）
Ctrl+A, 然后按 ESC，用方向键滚动，按ESC退出

# 杀死会话
screen -X -S 名称 quit
```

## 📈 监控训练

### 实时查看

```bash
# 恢复training会话
screen -r training

# 或查看GPU
watch -n 1 nvidia-smi

# 查看内存
free -h
```

### 检查输出

```bash
# 查看checkpoints
ls -lh outputs/checkpoints/

# 查看配置
cat outputs/config.json

# 查看最新checkpoint
ls -lht outputs/checkpoints/ | head -5
```

## 🎯 推荐工作流

### 快速验证流程（2小时）

```bash
# 1. 生成合成数据
python3 create_synthetic_dataset.py --num-samples 100

# 2. 快速训练
screen -S quick_test
python3 train.py --dataset-dir dataset --batch-size 4 --epochs 30 --use-amp
# Ctrl+A+D

# 3. 等待完成后推理
python3 inference.py \
  --checkpoint outputs/checkpoints/latest.pt \
  --num-samples 10 \
  --sampler ddim
```

### 完整训练流程（1-2天）

```bash
# 1. 生成高质量数据（可选：先生成50个测试）
screen -S dataset
python3 generate_premium_dataset.py --num-samples 1000
# Ctrl+A+D

# 2. 完整训练
screen -S training
python3 train.py \
  --dataset-dir dataset \
  --batch-size 4 \
  --epochs 150 \
  --use-amp \
  --save-every 500
# Ctrl+A+D

# 3. 生成大量样本
screen -S inference
python3 inference.py \
  --checkpoint outputs/checkpoints/latest.pt \
  --num-samples 100 \
  --sampler ddim
```

## 🆘 故障排除

### 问题1: 显存OOM
```bash
# 解决：减小batch_size
python3 train.py --batch-size 1 --use-amp
```

### 问题2: SSH断开
```bash
# screen会话保持运行
# 重新连接后恢复
screen -r training
```

### 问题3: 进程检查
```bash
# 查看Python进程
ps aux | grep python

# 查看GPU使用
nvidia-smi

# 查看screen会话
screen -ls
```

### 问题4: 数据集生成太慢
```bash
# 使用合成数据代替
python3 create_synthetic_dataset.py --num-samples 200

# 或减少Gemini样本数
python3 generate_premium_dataset.py --num-samples 50
```

## 📱 完整命令清单（复制粘贴）

### 在本地上传

```bash
cd /home/engine/project
scp -P 30022 minecraft_dit.tar.gz root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com:/gemini/code/
```

### 在服务器设置

```bash
cd /gemini/code
tar -xzf minecraft_dit.tar.gz
cd upload_package
python3 -m venv venv
source venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install google-generativeai numpy tqdm
```

### 快速测试训练

```bash
python3 create_synthetic_dataset.py --num-samples 100
screen -S test
python3 train.py --dataset-dir dataset --batch-size 4 --epochs 20 --use-amp
# Ctrl+A+D
```

### 完整训练

```bash
screen -S dataset
python3 generate_premium_dataset.py --num-samples 1000
# Ctrl+A+D

# 等完成后
screen -S training  
python3 train.py --dataset-dir dataset --batch-size 4 --epochs 100 --use-amp
# Ctrl+A+D
```

## 📞 需要更多帮助？

查看详细文档：
- `REMOTE_DEPLOYMENT_GUIDE.md` - 完整部署指南
- `QUICK_START_GUIDE.md` - 快速开始
- `README_ML.md` - 技术文档

---

**现在就开始吧！🚀**

建议：先用合成数据快速测试（30分钟），验证系统正常后再生成高质量数据集进行完整训练。
