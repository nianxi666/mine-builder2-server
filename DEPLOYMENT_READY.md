# ✅ 部署就绪确认

## 🎯 当前状态

**时间**: 2024-10-27 12:55
**状态**: ✅ **完全就绪，可以立即部署到远程GPU服务器**

## 📦 已准备的文件

### 核心代码（已打包）
```
✅ minecraft_dit.tar.gz (40KB)
   包含所有必需文件：
   - dit_model.py (DiT模型)
   - train.py (训练脚本)
   - inference.py (推理脚本)
   - generate_premium_dataset.py (Gemini数据生成)
   - create_synthetic_dataset.py (合成数据生成)
   - test_system.py (系统测试)
   - requirements_ml.txt (依赖列表)
   - 3个验证过的高质量样本
   - 完整文档
```

### 部署脚本
```
✅ deploy_to_remote.sh - 自动化部署脚本
✅ START_HERE.md - 快速开始指南（推荐阅读）
✅ REMOTE_DEPLOYMENT_GUIDE.md - 详细部署文档
```

### 验证样本（已测试）
```
✅ sample_quality_1.json (29KB) - 凛冬守望石塔 - 374方块 - 卓越
✅ sample_quality_2.json (36KB) - 极简玻璃别墅 - 371方块 - 卓越
✅ sample_quality_3.json (39KB) - 巨型橡树 - 402方块 - 卓越
```

## 🖥️ 服务器信息

```yaml
SSH地址: ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
端口: 30022
用户: root
密码: (无密码或你自己设置的)
内存: 16GB
显存: 6GB
工作目录: /gemini/code
```

## 🚀 立即开始的三个步骤

### 第1步：上传代码包（1分钟）

```bash
cd /home/engine/project

scp -P 30022 minecraft_dit.tar.gz \
  root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com:/gemini/code/
```

### 第2步：SSH连接并设置环境（5分钟）

```bash
# 连接
ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com

# 在服务器上执行
cd /gemini/code
tar -xzf minecraft_dit.tar.gz
cd upload_package

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install google-generativeai numpy tqdm

# 验证
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### 第3步：选择训练方式

#### 选项A：快速测试（30分钟，推荐先做）

```bash
# 生成合成数据
python3 create_synthetic_dataset.py --num-samples 100

# 在screen中训练
screen -S test_train
python3 train.py --dataset-dir dataset --batch-size 4 --epochs 20 --use-amp
# 按 Ctrl+A+D 挂起
```

#### 选项B：完整训练（1-2天）

```bash
# 1. 生成高质量数据集（在screen中，12-20小时）
screen -S dataset
python3 generate_premium_dataset.py \
  --api-key AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A \
  --num-samples 1000
# Ctrl+A+D 挂起

# 2. 等数据集完成后，开始训练（在screen中，4-6小时）
screen -S training
python3 train.py \
  --dataset-dir dataset \
  --batch-size 4 \
  --epochs 100 \
  --use-amp
# Ctrl+A+D 挂起
```

## 📊 配置说明（针对6GB显存）

### 推荐配置

```python
模型大小: small (33M参数)
批次大小: 4 (安全) 或 2 (更安全)
训练轮数: 100-150
学习率: 1e-4
混合精度: --use-amp (必须)
```

### 显存使用估算

| Batch Size | 显存占用 | 状态 |
|------------|----------|------|
| 1 | ~2GB | ✅ 非常安全 |
| 2 | ~3GB | ✅ 安全 |
| 4 | ~4-5GB | ✅ 推荐 |
| 6 | ~5-6GB | ⚠️ 紧张 |
| 8 | ~6-7GB | ❌ OOM |

## 🎮 Screen命令速查表

```bash
# 创建
screen -S 名称

# 列出
screen -ls

# 恢复
screen -r 名称

# 挂起（在screen内）
Ctrl+A, D

# 滚动（在screen内）
Ctrl+A, ESC (用方向键，ESC退出)

# 删除
screen -X -S 名称 quit
```

## 📈 监控训练

### 实时监控

```bash
# 恢复训练会话
screen -r training

# GPU监控
watch -n 1 nvidia-smi

# 系统资源
htop
```

### 检查进度

```bash
# 查看checkpoints
ls -lht outputs/checkpoints/

# 查看最新模型
ls -lh outputs/checkpoints/latest.pt

# 查看配置
cat outputs/config.json
```

## ⏱️ 预计时间

### 数据生成
- 合成数据100个: 1分钟
- Gemini 50个: 2-3小时
- Gemini 1000个: 12-20小时

### 训练（Small模型，6GB显存）
- 20 epochs: ~1小时
- 50 epochs: ~2-3小时
- 100 epochs: ~4-6小时
- 150 epochs: ~6-9小时

### 推理
- DDIM 10个样本: ~2分钟
- DDIM 100个样本: ~15分钟

## 🎯 推荐工作流

### 新手流程（3小时总计）

1. **快速验证（1小时）**
   ```bash
   python3 create_synthetic_dataset.py --num-samples 50
   python3 train.py --epochs 20 --batch-size 4 --use-amp
   python3 inference.py --num-samples 5
   ```

2. **中等训练（2小时）**
   ```bash
   python3 create_synthetic_dataset.py --num-samples 200
   python3 train.py --epochs 50 --batch-size 4 --use-amp
   python3 inference.py --num-samples 20
   ```

### 专业流程（2天总计）

1. **高质量数据（20小时）**
   ```bash
   screen -S dataset
   python3 generate_premium_dataset.py --num-samples 1000
   ```

2. **完整训练（6小时）**
   ```bash
   screen -S training
   python3 train.py --epochs 100 --batch-size 4 --use-amp
   ```

3. **大批量生成（1小时）**
   ```bash
   python3 inference.py --num-samples 100 --sampler ddim
   ```

## 🔥 一键命令集合

### 完整复制粘贴命令（本地）

```bash
cd /home/engine/project
scp -P 30022 minecraft_dit.tar.gz root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com:/gemini/code/
```

### 完整复制粘贴命令（服务器）

```bash
cd /gemini/code && \
tar -xzf minecraft_dit.tar.gz && \
cd upload_package && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu118 && \
pip install -q google-generativeai numpy tqdm && \
python3 -c "import torch; print(f'✅ PyTorch {torch.__version__}'); print(f'✅ CUDA: {torch.cuda.is_available()}'); print(f'✅ GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')" && \
echo "✅ 环境准备完成！"
```

### 快速测试训练

```bash
python3 create_synthetic_dataset.py --num-samples 100 && \
screen -dmS test bash -c "source venv/bin/activate && python3 train.py --dataset-dir dataset --batch-size 4 --epochs 20 --use-amp" && \
echo "✅ 训练已在screen中启动！使用 'screen -r test' 查看"
```

## 🆘 故障排除

### 问题：OOM (显存不足)
```bash
# 解决：减小batch_size
python3 train.py --batch-size 1 --use-amp
```

### 问题：训练中断
```bash
# screen会话仍在运行
screen -r training

# 如果没有，检查checkpoint
ls outputs/checkpoints/
python3 train.py --resume outputs/checkpoints/latest.pt
```

### 问题：SSH断开
```bash
# 重新连接
ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com

# 恢复screen
screen -r training
```

### 问题：数据集生成慢
```bash
# 方案1：使用合成数据
python3 create_synthetic_dataset.py --num-samples 200

# 方案2：减少Gemini样本
python3 generate_premium_dataset.py --num-samples 50
```

## 📚 文档索引

- **START_HERE.md** - 快速开始（推荐先读）
- **REMOTE_DEPLOYMENT_GUIDE.md** - 详细部署指南
- **QUICK_START_GUIDE.md** - 快速指南
- **README_ML.md** - 技术文档
- **FINAL_REPORT.md** - 项目总结

## ✅ 检查清单

部署前确认：
- [ ] 已有minecraft_dit.tar.gz文件
- [ ] 知道SSH连接信息
- [ ] 了解screen基本用法
- [ ] 决定使用合成数据还是Gemini数据
- [ ] 确认batch_size配置（推荐4）

部署后确认：
- [ ] GPU可用（nvidia-smi）
- [ ] PyTorch能识别CUDA
- [ ] 虚拟环境已激活
- [ ] 数据集已生成
- [ ] 训练在screen中运行
- [ ] 能恢复screen会话查看进度

## 🎉 准备完成！

**所有文件就绪，可以立即开始部署！**

**推荐顺序**：
1. 阅读 START_HERE.md（5分钟）
2. 上传代码包（1分钟）
3. 设置环境（5分钟）
4. 快速测试（30分钟）
5. 完整训练（按需）

**现在就开始吧！** 🚀

---

**部署准备完成时间**: 2024-10-27 12:55
**状态**: ✅ 就绪
**下一步**: 运行 scp 上传命令
