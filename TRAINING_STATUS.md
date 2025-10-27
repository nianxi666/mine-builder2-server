# 🚀 训练状态 - 实时更新

## ✅ 训练已启动

**启动时间**: 刚刚  
**状态**: 🔄 运行中  
**Screen会话**: training  

### 配置信息

```yaml
数据集位置: /gemini/code/dataset (100个合成样本)
输出目录: /gemini/code/outputs
推理样本: /gemini/code/outputs/inference_samples

模型配置:
  - 模型大小: small (33M参数)
  - Batch size: 8
  - Epochs: 50
  - 学习率: 1e-4
  - 混合精度: 启用

特殊功能:
  - 每5步推理一次 ✅
  - 每50步保存checkpoint
  - 推理时生成2个样本
  - 推理采样步数: 10步
```

## 📁 文件位置（所有在/gemini/code）

```
/gemini/code/
├── dataset/                    # 训练数据集
│   ├── sample_0000/
│   ├── sample_0001/
│   └── ...
├── outputs/                    # 训练输出
│   ├── checkpoints/            # 模型checkpoint
│   │   ├── step_000050.pt
│   │   ├── step_000100.pt
│   │   └── latest.pt
│   └── inference_samples/      # 推理测试样本
│       ├── step_000005_sample_0.json
│       ├── step_000005_sample_1.json
│       ├── step_000010_sample_0.json
│       └── ...
├── upload_package/             # 代码目录
└── training.log                # 训练日志
```

## 📊 监控命令

### 从本地监控

```bash
# 查看最新日志
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "tail -50 /gemini/code/training.log"

# 实时监控
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "tail -f /gemini/code/training.log"

# 查看推理样本数量
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "ls /gemini/code/outputs/inference_samples/ | wc -l"

# 查看checkpoint
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "ls -lh /gemini/code/outputs/checkpoints/"

# 查看GPU使用
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "nvidia-smi"
```

### SSH进入服务器

```bash
# 连接
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com

# 然后在服务器上
cd /gemini/code

# 查看screen
screen -ls

# 进入训练会话
screen -r training

# 查看日志
tail -f training.log

# 查看推理样本
ls -lh outputs/inference_samples/

# 查看最新推理样本
ls -lt outputs/inference_samples/ | head -5
```

## 🎯 预期行为

### 训练流程

1. **环境安装** (5-10分钟)
   - 安装pip
   - 安装PyTorch + CUDA
   - 安装其他依赖

2. **数据集生成** (1-2分钟)
   - 生成100个合成样本

3. **训练开始**
   - 加载数据集
   - 创建模型
   - 开始训练

4. **每5步推理** ✅
   ```
   Step 5: 推理 → 生成2个样本
   Step 10: 推理 → 生成2个样本
   Step 15: 推理 → 生成2个样本
   ...
   ```

5. **每50步保存**
   ```
   Step 50: 保存checkpoint
   Step 100: 保存checkpoint
   ...
   ```

### 推理样本命名

```
step_000005_sample_0.json  # 第5步，第0个样本
step_000005_sample_1.json  # 第5步，第1个样本
step_000010_sample_0.json  # 第10步，第0个样本
step_000010_sample_1.json  # 第10步，第1个样本
...
```

## 📈 训练进度估算

```
数据集大小: 100个样本
Batch size: 8
每epoch步数: 100/8 = 13步

推理频率: 每5步一次
每epoch推理次数: 13/5 ≈ 2-3次

总epochs: 50
预计总步数: 13 * 50 = 650步
预计推理次数: 650/5 = 130次
预计生成样本: 130 * 2 = 260个JSON文件

预计训练时间: 2-4小时（取决于GPU）
```

## 🔍 验证训练效果

### 查看推理样本改进

```bash
# SSH进入
cd /gemini/code/outputs/inference_samples

# 查看早期样本（step 5-20）
cat step_000005_sample_0.json | jq '.voxels | length'

# 查看中期样本（step 300左右）
cat step_000300_sample_0.json | jq '.voxels | length'

# 查看后期样本（step 600+）
cat step_000600_sample_0.json | jq '.voxels | length'
```

**期望**：
- 早期：方块数量少或随机
- 中期：开始有结构
- 后期：完整的建筑

## 🆘 故障排除

### 问题1: 训练没有开始

```bash
# 查看screen状态
screen -ls

# 查看日志
tail -100 /gemini/code/training.log

# 重新启动
cd /gemini/code/upload_package
bash start_training.sh
```

### 问题2: 环境安装失败

```bash
# 手动安装
cd /gemini/code/upload_package
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --break-system-packages
python3 -m pip install --break-system-packages torch torchvision --index-url https://download.pytorch.org/whl/cu118
python3 -m pip install --break-system-packages google-generativeai numpy tqdm
```

### 问题3: GPU不可用

```bash
# 检查CUDA
nvidia-smi

# 如果GPU不可用，训练会自动使用CPU（会慢很多）
# 在日志中会看到 "使用设备: cpu"
```

### 问题4: 内存不足

```bash
# 减小batch_size
# 编辑 start_training.sh
# 将 --batch-size 8 改为 --batch-size 4 或 2
```

## 📱 快速命令参考

```bash
# 查看训练日志（最新50行）
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "tail -50 /gemini/code/training.log"

# 查看推理样本数量
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "ls /gemini/code/outputs/inference_samples/ | wc -l"

# 查看GPU使用
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv"

# 查看最新checkpoint
sshpass -p 'liu20062020' ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com "ls -lht /gemini/code/outputs/checkpoints/ | head -5"

# 下载所有推理样本到本地
sshpass -p 'liu20062020' scp -P 30022 -r root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com:/gemini/code/outputs/inference_samples/ ./local_inference_samples/
```

## ✅ 完成后操作

训练完成后，你将在 `/gemini/code/outputs/` 看到：

1. **Checkpoints** - 训练好的模型
2. **Inference samples** - 约260个JSON文件，展示训练过程

你可以：
- 查看推理样本的进化过程
- 使用最新checkpoint进行更多推理
- 分析哪个checkpoint效果最好

---

**当前状态**: 🔄 训练中  
**监控**: `tail -f /gemini/code/training.log`  
**位置**: 所有文件都在 `/gemini/code/` 目录  
**推理**: 每5步自动推理 ✅
