# 🚀 远程GPU服务器部署状态

## ✅ 已完成的步骤

### 1. SSH连接测试 ✅
```
服务器: ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
端口: 30022
用户: root4563@root
密码: liu20062020
```

**测试结果：**
- ✅ SSH连接成功
- ✅ 内存: **503GB**（超大内存！）
- ✅ Python 3.10.12
- ✅ CUDA 11.8

### 2. 代码上传 ✅
```bash
已上传: /gemini/code/minecraft_dit.tar.gz (40KB)
```

### 3. 代码解压 ✅
```bash
工作目录: /gemini/code/upload_package/
包含: 所有训练代码、数据生成器、模型定义
```

### 4. 环境安装 🔄 进行中
```bash
正在执行: remote_setup.sh
- 安装pip
- 安装PyTorch (CUDA 11.8)
- 安装依赖 (google-generativeai, numpy, tqdm)
- 测试GPU
- 生成测试数据集
```

**注意：** PyTorch下载较大（~2GB），需要几分钟时间。

## 📱 下一步操作

### 等待环境安装完成后（约5-10分钟）

#### 方案A：使用合成数据快速测试（推荐先做）

```bash
# SSH连接到服务器
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com

# 进入工作目录
cd /gemini/code/upload_package

# 生成200个合成样本
python3 create_synthetic_dataset.py --num-samples 200 --output-dir dataset

# 在screen中开始训练
screen -S training
python3 train.py \
  --dataset-dir dataset \
  --model-size small \
  --batch-size 8 \
  --epochs 50 \
  --use-amp

# 挂起screen: Ctrl+A, D
```

#### 方案B：使用Gemini生成高质量数据（完整流程）

```bash
# SSH连接
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com

cd /gemini/code/upload_package

# 在screen中生成数据集
screen -S dataset
python3 generate_premium_dataset.py \
  --api-key AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A \
  --num-samples 1000 \
  --output-dir dataset

# Ctrl+A, D 挂起

# 等数据集完成后，开始训练
screen -S training
python3 train.py \
  --dataset-dir dataset \
  --model-size small \
  --batch-size 8 \
  --epochs 100 \
  --use-amp

# Ctrl+A, D 挂起
```

## 🎯 监控命令

### 检查环境安装状态

```bash
# 本地执行，查看安装进度
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "cd /gemini/code/upload_package && python3 -c 'import torch; print(f\"PyTorch {torch.__version__}\"); print(f\"CUDA: {torch.cuda.is_available()}\")'"
```

### 查看训练进度

```bash
# SSH连接后
screen -ls                    # 列出所有会话
screen -r training            # 恢复training会话
nvidia-smi                    # 查看GPU使用
ls -lh outputs/checkpoints/   # 查看保存的模型
```

## ⚙️ 服务器配置建议

### 由于503GB超大内存，可以使用更大的配置！

| 配置项 | 原建议 (16GB) | 新建议 (503GB) |
|--------|---------------|----------------|
| batch_size | 4 | 16-32 ⭐ |
| num_workers | 2 | 8-16 ⭐ |
| model_size | small | base 或 large ⭐ |
| epochs | 50-100 | 200-300 ⭐ |

**推荐配置（充分利用大内存）：**

```bash
python3 train.py \
  --dataset-dir dataset \
  --model-size base \
  --batch-size 16 \
  --epochs 150 \
  --use-amp \
  --num-workers 8
```

**激进配置（如果显存也很大）：**

```bash
python3 train.py \
  --dataset-dir dataset \
  --model-size large \
  --batch-size 32 \
  --epochs 200 \
  --use-amp \
  --num-workers 16
```

## 🔍 故障排查

### 如果环境安装失败

```bash
# SSH连接
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com

cd /gemini/code/upload_package

# 手动安装pip
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --break-system-packages

# 手动安装PyTorch
python3 -m pip install --break-system-packages torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 手动安装其他依赖
python3 -m pip install --break-system-packages google-generativeai numpy tqdm

# 测试
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### 如果GPU不可用

```bash
# 检查CUDA
nvidia-smi
ls /usr/local/cuda*/bin/nvcc

# 安装CPU版本PyTorch（备选方案）
python3 -m pip install --break-system-packages torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

## 📊 预计时间

### 环境安装
- pip安装: 1-2分钟
- PyTorch下载安装: 5-10分钟
- 其他依赖: 2-3分钟
- **总计: 10-15分钟**

### 数据生成
- 合成数据200个: 1-2分钟
- Gemini 1000个: 12-20小时

### 训练时间
- Small模型, batch=8, 50 epochs: 2-3小时
- Base模型, batch=16, 150 epochs: 8-12小时
- Large模型, batch=32, 200 epochs: 24-36小时

## 🎉 完成后的效果

训练完成后你将拥有：

1. **训练好的DiT模型** - 可以生成16x16x16 Minecraft建筑
2. **Checkpoint文件** - outputs/checkpoints/latest.pt
3. **训练日志** - 可查看loss变化
4. **推理脚本** - 可生成新的建筑

### 使用训练好的模型生成建筑

```bash
python3 inference.py \
  --checkpoint outputs/checkpoints/latest.pt \
  --model-size base \
  --num-samples 50 \
  --sampler ddim \
  --num-steps 50 \
  --output-dir generated
```

## 📞 快速命令参考

```bash
# 连接服务器
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com

# 进入工作目录
cd /gemini/code/upload_package

# 生成数据
python3 create_synthetic_dataset.py --num-samples 200

# 训练
screen -S training
python3 train.py --batch-size 16 --epochs 100 --use-amp

# 推理
python3 inference.py --checkpoint outputs/checkpoints/latest.pt --num-samples 20
```

---

**当前状态**: ⏳ **环境安装中**  
**预计完成**: 10-15分钟  
**下一步**: 等待安装完成，然后开始训练

**建议**: 由于有503GB大内存，可以使用更大的模型（base或large）和更大的batch_size（16-32）！
