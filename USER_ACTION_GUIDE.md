# 🎯 用户操作指南

## 📊 当前状态

### ✅ 已完成
1. 远程服务器环境配置完成
2. OpenAI包安装成功（用于GLM-4.6）
3. 所有训练脚本上传完成
4. 本地Gemini数据生成在后台运行（慢速）

### ⏳ 待解决
1. GLM-4.6数据生成卡住（首次API调用无响应）
2. 本地Gemini生成速度慢（100秒/样本）

---

## 🚀 推荐方案：立即启动合成数据训练

**这个方案可以让你立即看到训练效果！**

### 📝 执行步骤

#### 方式1：一键自动启动（推荐）

```bash
bash /home/engine/project/start_synthetic_training.exp
```

这个脚本会自动：
1. 连接到远程服务器
2. 生成200个合成数据样本（5分钟）
3. 在screen中启动训练
4. 显示初始训练日志

#### 方式2：手动执行（如果自动脚本失败）

```bash
# 1. 连接到远程服务器
ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
# 密码: liu20062020

# 2. 生成合成数据
cd /gemini/code/upload_package
python3 create_synthetic_dataset.py --num-samples 200 --output-dir /gemini/code/dataset_synthetic

# 3. 启动训练
screen -S training
python3 train_with_inference.py \
  --dataset-dir /gemini/code/dataset_synthetic \
  --output-dir /gemini/code/outputs_synthetic \
  --model-size small \
  --batch-size 8 \
  --epochs 100 \
  --lr 1e-4 \
  --use-amp \
  --save-every 50 \
  --inference-every 10 \
  --inference-samples 2 \
  --inference-steps 50 \
  --num-workers 4 \
  2>&1 | tee /gemini/code/training_synthetic.log

# 4. 挂起screen（让训练在后台运行）
# 按 Ctrl+A，然后按 D

# 5. 退出SSH
exit
```

---

## 📱 监控训练进度

### 查看训练进度

```bash
# 连接到远程
ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
# 密码: liu20062020

# 进入训练screen
screen -r training

# 或查看日志
tail -f /gemini/code/training_synthetic.log

# 查看推理样本
ls -lh /gemini/code/outputs_synthetic/inference_samples/

# 查看checkpoints
ls -lh /gemini/code/outputs_synthetic/checkpoints/
```

### 监控命令（本地运行）

```bash
# 使用自动监控脚本
bash /home/engine/project/check_status.sh
```

---

## ⏱️ 预计时间

- **数据生成**: 5分钟（200个样本）
- **训练时间**: 2-4小时（100 epochs）
- **推理间隔**: 每10步生成2个推理样本

---

## 📈 训练指标

### 期待看到的内容

```
Epoch 1/100
Step 10: Loss=0.85, 推理样本已生成
Step 20: Loss=0.72, 推理样本已生成
...
Epoch 10/100
Step 100: Loss=0.35, 保存checkpoint
...
```

### 文件输出

```
/gemini/code/outputs_synthetic/
├── checkpoints/
│   ├── checkpoint_step_0050.pt
│   ├── checkpoint_step_0100.pt
│   └── latest.pt
├── inference_samples/
│   ├── step_000010_sample_0.json
│   ├── step_000010_sample_1.json
│   ├── step_000020_sample_0.json
│   └── ...
└── training.log
```

---

## 🔧 如果遇到问题

### 问题1：训练未启动

```bash
# 检查screen状态
ssh -p 30022 root4563@...
screen -ls

# 如果没有training，重新启动
cd /gemini/code/upload_package
# 执行上面的手动步骤
```

### 问题2：显存不足

```bash
# 降低batch size
# 在train_with_inference.py命令中
# 将 --batch-size 8 改为 --batch-size 4
# 或 --batch-size 2
```

### 问题3：想停止训练

```bash
ssh -p 30022 root4563@...
screen -r training
# 按 Ctrl+C 停止
# 或
screen -X -S training quit
```

---

## 🎯 后续步骤

### 1. 训练完成后

```bash
# 连接到远程
ssh -p 30022 root4563@...

# 查看最终模型
ls -lh /gemini/code/outputs_synthetic/checkpoints/latest.pt

# 查看所有推理样本
ls /gemini/code/outputs_synthetic/inference_samples/ | wc -l

# 下载感兴趣的文件（本地运行）
scp -P 30022 root4563@...:/gemini/code/outputs_synthetic/checkpoints/latest.pt ./
scp -r -P 30022 root4563@...:/gemini/code/outputs_synthetic/inference_samples ./
```

### 2. 使用真实数据（可选）

当本地Gemini生成足够数据后（100+样本）：

```bash
# 本地运行同步脚本
nohup bash /home/engine/project/sync_dataset_scp.sh > sync.log 2>&1 &

# 远程启动真实数据训练
ssh -p 30022 ...
cd /gemini/code/upload_package
screen -S training_real
python3 train_incremental.py \
  --dataset-dir /gemini/code/dataset_live \
  --output-dir /gemini/code/outputs_real \
  --model-size small \
  --batch-size 8 \
  --max-epochs 200 \
  --min-samples 100 \
  --refresh-interval 60 \
  --inference-every 10
```

---

## 📋 快速参考

### SSH连接
```bash
ssh -p 30022 root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com
# 密码: liu20062020
```

### Screen命令
```bash
screen -ls                # 列出所有session
screen -r training        # 恢复training session
Ctrl+A, D                 # 挂起当前session
screen -X -S training quit  # 关闭training session
```

### 重要路径
```bash
/gemini/code/upload_package/          # 代码目录
/gemini/code/dataset_synthetic/       # 合成数据
/gemini/code/outputs_synthetic/       # 训练输出
/gemini/code/training_synthetic.log   # 训练日志
```

---

## 🎊 总结

**现在就执行这个命令开始训练：**

```bash
bash /home/engine/project/start_synthetic_training.exp
```

**或者手动SSH到远程服务器按步骤操作！**

**预计2-4小时后你就能看到训练完成的模型！** 🎉
