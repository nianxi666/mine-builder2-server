# 🎯 你需要执行的操作步骤

## ⚡ 快速版（10分钟开始训练）

### 1. 上传代码（本地执行）

打开终端，复制粘贴：

```bash
cd /home/engine/project
scp -P 30022 minecraft_dit.tar.gz root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com:/gemini/code/
```

*如果要求输入密码，输入你的服务器密码*

### 2. 连接服务器

```bash
ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
```

### 3. 一键设置并开始（服务器上执行）

复制粘贴下面整段命令：

```bash
cd /gemini/code && \
tar -xzf minecraft_dit.tar.gz && \
cd upload_package && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu118 && \
pip install -q google-generativeai numpy tqdm && \
python3 create_synthetic_dataset.py --num-samples 100 && \
screen -dmS training bash -c "source venv/bin/activate && python3 train.py --dataset-dir dataset --batch-size 4 --epochs 50 --use-amp" && \
echo "✅ 训练已启动！使用 'screen -r training' 查看进度"
```

### 4. 查看训练进度

```bash
# 查看所有screen会话
screen -ls

# 进入训练会话
screen -r training

# 挂起会话（在screen内按）
Ctrl+A, 然后按 D

# 查看GPU使用
nvidia-smi
```

**完成！训练已经在后台运行了！** 🎉

---

## 📋 详细版（完整流程）

### 步骤1: 本地上传

```bash
# 在你的本地机器上
cd /home/engine/project

# 上传代码包
scp -P 30022 minecraft_dit.tar.gz \
  root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com:/gemini/code/

# 看到进度条，等待完成
```

### 步骤2: SSH连接

```bash
ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
```

### 步骤3: 解压和设置环境

```bash
# 进入工作目录
cd /gemini/code

# 解压代码
tar -xzf minecraft_dit.tar.gz
cd upload_package

# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装PyTorch（GPU版本）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 安装其他依赖
pip install google-generativeai numpy tqdm

# 验证安装
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}')"

# 应该看到 "CUDA可用: True"
```

### 步骤4A: 快速测试（推荐先做）

```bash
# 生成100个合成数据样本（1分钟）
python3 create_synthetic_dataset.py --num-samples 100 --output-dir dataset

# 查看生成的数据
ls dataset/sample_* | wc -l  # 应该显示100

# 在screen中开始训练
screen -S test_training

# 启动训练（30分钟，20个epoch）
python3 train.py \
  --dataset-dir dataset \
  --model-size small \
  --batch-size 4 \
  --epochs 20 \
  --use-amp

# 挂起screen：按 Ctrl+A，然后按 D
```

### 步骤4B: 完整训练（测试通过后）

```bash
# 选项1: 使用合成数据（快速）
python3 create_synthetic_dataset.py --num-samples 500 --output-dir dataset

# 选项2: 使用Gemini生成高质量数据（慢但好）
screen -S dataset_gen
python3 generate_premium_dataset.py \
  --api-key AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A \
  --num-samples 1000 \
  --output-dir dataset
# Ctrl+A+D 挂起，等12-20小时完成

# 等数据集完成后，开始训练
screen -S training

python3 train.py \
  --dataset-dir dataset \
  --model-size small \
  --batch-size 4 \
  --epochs 100 \
  --use-amp \
  --save-every 500

# Ctrl+A+D 挂起
```

### 步骤5: 监控和查看

```bash
# 查看所有screen会话
screen -ls

# 恢复训练会话
screen -r training

# 查看GPU使用
nvidia-smi

# 查看训练输出目录
ls -lh outputs/checkpoints/

# 查看最新的checkpoint
ls -lt outputs/checkpoints/ | head -5
```

### 步骤6: 训练完成后生成样本

```bash
# 使用训练好的模型生成新建筑
python3 inference.py \
  --checkpoint outputs/checkpoints/latest.pt \
  --model-size small \
  --num-samples 20 \
  --sampler ddim \
  --num-steps 50 \
  --output-dir generated

# 查看生成结果
ls generated/
```

---

## 🎮 Screen操作指南

### 基本命令

```bash
# 创建新会话
screen -S 会话名

# 列出所有会话
screen -ls

# 恢复会话
screen -r 会话名

# 在会话内挂起（重要！）
按 Ctrl+A，然后按 D

# 在会话内滚动查看历史
按 Ctrl+A，然后按 ESC
用方向键或PageUp/PageDown滚动
按 ESC 退出滚动模式

# 杀死会话
screen -X -S 会话名 quit
```

### 常用场景

```bash
# 启动训练后挂起
screen -S training
python3 train.py ...
# Ctrl+A+D

# 查看训练进度
screen -r training

# 如果忘记会话名
screen -ls  # 列出所有
screen -r   # 如果只有一个会话，直接恢复
```

---

## 📊 训练参数说明

### 根据你的6GB显存

| Batch Size | 显存使用 | 训练速度 | 推荐 |
|------------|----------|----------|------|
| 1 | ~2GB | 慢 | 最安全 |
| 2 | ~3GB | 中等 | 安全 |
| 4 | ~4-5GB | 快 | ✅ 推荐 |
| 6 | ~5-6GB | 很快 | ⚠️ 冒险 |
| 8 | ~6-7GB | 最快 | ❌ 会OOM |

### 推荐配置

**快速测试：**
```bash
--batch-size 4 --epochs 20
```

**中等训练：**
```bash
--batch-size 4 --epochs 50
```

**完整训练：**
```bash
--batch-size 4 --epochs 100
```

**如果OOM：**
```bash
--batch-size 2 --epochs 100
```

---

## 🆘 可能遇到的问题

### 问题1: 上传失败
```bash
# 检查网络连接
ping direct.virtaicloud.com

# 确认文件存在
ls -lh /home/engine/project/minecraft_dit.tar.gz

# 重试上传
scp -P 30022 minecraft_dit.tar.gz root@...
```

### 问题2: SSH连接超时
```bash
# 检查端口和主机
telnet direct.virtaicloud.com 30022

# 或使用verbose模式查看详情
ssh -v -p 30022 root@...
```

### 问题3: 训练OOM
```bash
# 立即修改batch_size
# 在train.py命令中改为
--batch-size 2
# 或
--batch-size 1
```

### 问题4: screen命令不存在
```bash
# 安装screen
apt update && apt install -y screen

# 或使用tmux
apt install -y tmux
tmux new -s training
```

### 问题5: 想查看但找不到会话
```bash
# 列出所有screen
screen -ls

# 如果显示Detached，恢复它
screen -r 会话名

# 如果显示Attached（已被占用）
screen -d -r 会话名  # 强制恢复
```

---

## ✅ 检查清单

### 上传前
- [ ] 在/home/engine/project目录
- [ ] minecraft_dit.tar.gz存在（40KB）
- [ ] 知道SSH密码（或无密码）

### 连接后
- [ ] 成功SSH到服务器
- [ ] 在/gemini/code目录
- [ ] 文件已上传到服务器

### 设置后
- [ ] 代码已解压到upload_package
- [ ] 虚拟环境已创建并激活
- [ ] PyTorch和CUDA正常（nvidia-smi有输出）
- [ ] 依赖包已安装

### 训练前
- [ ] 数据集已生成（ls dataset/sample_*）
- [ ] 知道如何使用screen
- [ ] 确定了batch_size（推荐4）

### 训练中
- [ ] 训练在screen中运行
- [ ] 能用screen -r恢复查看
- [ ] GPU在工作（nvidia-smi显示占用）
- [ ] outputs目录在增长

---

## 🎯 建议顺序

### 第一次使用（今天）

1. ✅ 上传代码（5分钟）
2. ✅ 设置环境（5分钟）
3. ✅ 快速测试（1小时）
   - 生成100个合成样本
   - 训练20个epochs
   - 验证系统正常

### 第二次使用（明天）

4. ⏰ 生成高质量数据（12-20小时）
   - 使用Gemini API
   - 在screen中运行
   - 晚上启动，第二天查看

### 第三次使用（后天）

5. 🏋️ 完整训练（4-6小时）
   - 100个epochs
   - batch_size=4
   - 在screen中运行

6. 🎨 生成样本（30分钟）
   - 生成50-100个建筑
   - 查看质量

---

## 📱 快速命令参考

### 上传（本地）
```bash
cd /home/engine/project
scp -P 30022 minecraft_dit.tar.gz root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com:/gemini/code/
```

### 连接（本地）
```bash
ssh -p 30022 root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
```

### 一键设置（服务器）
```bash
cd /gemini/code && tar -xzf minecraft_dit.tar.gz && cd upload_package && python3 -m venv venv && source venv/bin/activate && pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu118 && pip install -q google-generativeai numpy tqdm
```

### 快速训练（服务器）
```bash
python3 create_synthetic_dataset.py --num-samples 100
screen -S training
python3 train.py --batch-size 4 --epochs 20 --use-amp
```

### 查看进度（服务器）
```bash
screen -r training  # 恢复
nvidia-smi          # 查看GPU
screen -ls          # 列出会话
```

---

## 🎉 准备完成！

**所有准备工作已完成，现在可以开始了！**

**第一步**: 复制上面的"上传"命令，在本地终端运行
**第二步**: 复制"连接"命令，SSH到服务器
**第三步**: 复制"一键设置"命令，在服务器上运行

**就这么简单！** 🚀

如有问题，查看详细文档：
- START_HERE.md
- REMOTE_DEPLOYMENT_GUIDE.md
- DEPLOYMENT_READY.md
