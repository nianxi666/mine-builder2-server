# 🚀 快速开始指南：Minecraft 16x16x16 DiT训练系统

这是一个完整的AI模型训练系统，用于生成Minecraft 16x16x16 schematic建筑。

## 📋 系统概述

- **模型架构**: Diffusion Transformer (DiT) - 最新的扩散模型架构
- **数据大小**: 16x16x16 体素
- **数据集**: 1000个样本（已生成）
- **训练**: 支持GPU加速，混合精度训练
- **推理**: DDPM/DDIM采样器

## 🎯 文件说明

### 核心文件
- `dit_model.py` - DiT模型定义（3D Transformer扩散模型）
- `train.py` - 训练脚本
- `inference.py` - 推理生成脚本

### 数据集生成
- `create_synthetic_dataset.py` - 合成数据集生成器（推荐，快速）
- `dataset_generator_simple.py` - 使用Gemini API生成（需API密钥）
- `dataset_generator.py` - 完整版（使用函数调用）

### 辅助文件
- `test_system.py` - 系统测试脚本
- `run_pipeline.sh` - 完整流程脚本
- `quick_start.sh` - 快速测试脚本
- `README_ML.md` - 详细文档

## ⚡ 快速开始（3步）

### 方案A: 使用已生成的合成数据集（推荐）

数据集已经生成在 `dataset/` 目录（1000个样本）！

#### 步骤1: 测试系统
```bash
python3 test_system.py
```

#### 步骤2: 开始训练（GPU推荐）
```bash
# 小模型快速测试（5-10分钟）
python3 train.py \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size small \
  --batch-size 8 \
  --epochs 10 \
  --use-amp

# 完整训练（几小时）
python3 train.py \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size small \
  --batch-size 16 \
  --epochs 100 \
  --use-amp
```

#### 步骤3: 生成新建筑
```bash
python3 inference.py \
  --checkpoint outputs/checkpoints/latest.pt \
  --model-size small \
  --num-samples 10 \
  --sampler ddim \
  --num-steps 50
```

### 方案B: 使用Gemini API生成真实数据

需要Google AI Studio API密钥（已提供）：

```bash
# 生成1000个样本（约30-60分钟）
python3 dataset_generator_simple.py \
  --api-key AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A \
  --output-dir dataset_gemini \
  --num-samples 1000

# 然后使用上面的训练命令，修改 --dataset-dir 为 dataset_gemini
```

## 💻 远程GPU训练

### SSH连接后的设置

```bash
# 1. 克隆或上传代码
cd /path/to/project

# 2. 创建虚拟环境
python3 -m venv venv_ml
source venv_ml/bin/activate

# 3. 安装依赖
pip install torch torchvision google-generativeai tqdm numpy

# 4. 生成或上传数据集
# 选项A: 快速生成合成数据
python3 create_synthetic_dataset.py --num-samples 1000

# 选项B: 使用Gemini生成
python3 dataset_generator_simple.py --num-samples 1000

# 5. 开始训练
python3 train.py \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size base \
  --batch-size 32 \
  --epochs 200 \
  --use-amp \
  --num-workers 8

# 6. 后台运行（推荐）
nohup python3 train.py \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size base \
  --batch-size 32 \
  --epochs 200 \
  --use-amp > training.log 2>&1 &

# 监控训练
tail -f training.log
```

### GPU要求

- **最小**: 6GB VRAM（small模型，batch_size=4）
- **推荐**: 16GB VRAM（base模型，batch_size=16）
- **最佳**: 24GB+ VRAM（large模型，batch_size=32）

## 📁 数据集信息

### 当前数据集（synthetic）
- **位置**: `./dataset/`
- **样本数**: 1000
- **类型**: 合成规则建筑
- **包含**: 立方体、塔、金字塔、房屋、树、墙、拱门等

### 数据格式
每个样本包含：
- `data.json` - JSON格式，人类可读
- `voxels.npz` - NumPy压缩格式，训练使用
  - voxels: (16, 16, 16, 2) - [block_id, meta_data]
  - prompt: 文本描述

## 🎮 模型配置

### DiT-Small（推荐开始）
- 参数: ~33M
- Hidden size: 384
- Layers: 12
- 训练时间: 2-4小时（1000样本，100 epochs，GTX 1080）

### DiT-Base
- 参数: ~86M
- Hidden size: 512
- Layers: 16
- 训练时间: 4-8小时

### DiT-Large
- 参数: ~458M
- Hidden size: 768
- Layers: 24
- 训练时间: 8-16小时

## 🔍 检查训练进度

```bash
# 查看checkpoints
ls -lh outputs/checkpoints/

# 最新的checkpoint
ls -lh outputs/checkpoints/latest.pt

# 查看训练日志
tail -50 training.log

# 检查生成的样本
ls -lh generated/
```

## 🎨 生成结果

生成的建筑保存在 `generated/` 目录：

```bash
generated/
├── sample_0000.json    # JSON格式
├── sample_0000.npz     # NPZ格式
├── sample_0001.json
└── ...
```

### 查看生成结果
```python
import json
import numpy as np

# 读取JSON
with open('generated/sample_0000.json') as f:
    data = json.load(f)
    print(f"Prompt: {data['prompt']}")
    print(f"Blocks: {len(data['schematic']['voxels'])}")

# 读取NPZ
data = np.load('generated/sample_0000.npz', allow_pickle=True)
voxels = data['voxels']  # (16, 16, 16, 2)
print(f"Shape: {voxels.shape}")
```

## ⚙️ 训练参数调优

### 提高质量
```bash
python3 train.py \
  --model-size base \        # 使用更大模型
  --epochs 200 \             # 更多训练轮数
  --batch-size 16 \          # 适当的batch size
  --lr 5e-5 \                # 较小的学习率
  --use-amp                  # 混合精度
```

### 加快训练
```bash
python3 train.py \
  --model-size small \       # 小模型
  --batch-size 32 \          # 更大batch（需要更多显存）
  --use-amp \                # 混合精度
  --num-workers 8            # 更多数据加载线程
```

### 节省显存
```bash
python3 train.py \
  --model-size small \
  --batch-size 4 \           # 小batch
  --use-amp \                # 混合精度
  --num-workers 2
```

## 🐛 故障排除

### OOM（显存不足）
- 减小 `--batch-size`
- 使用 `--use-amp`
- 使用更小的模型 `--model-size small`

### 训练loss不下降
- 检查数据集质量
- 尝试不同学习率（1e-4到1e-5）
- 增加训练epochs
- 使用更大的模型

### API 429错误（生成数据集时）
- 脚本会自动重试
- 可以使用合成数据集代替：`create_synthetic_dataset.py`
- 或者减慢生成速度

## 📊 预期结果

### 训练Loss
- 初始: ~0.5-1.0
- 10 epochs: ~0.1-0.3
- 50 epochs: ~0.05-0.15
- 100 epochs: ~0.02-0.10

### 生成质量
- **10 epochs**: 基本形状
- **50 epochs**: 可识别结构
- **100 epochs**: 较好质量
- **200+ epochs**: 最佳质量

## 🎓 下一步

1. **微调模型**: 基于生成结果调整训练参数
2. **扩展数据集**: 生成更多样本（2000-5000）
3. **添加条件**: 实现文本条件生成
4. **集成到Server**: 将模型集成到Mine Builder 2 Server

## 📞 需要帮助？

遇到问题请检查：
1. `test_system.py` - 系统测试
2. `README_ML.md` - 详细文档
3. 训练日志 - `outputs/` 目录

## 🎉 完成！

现在你已经有了：
✅ 完整的数据集（1000个样本）
✅ 最新的DiT模型架构
✅ 训练和推理脚本
✅ GPU加速支持
✅ 混合精度训练

开始训练你的Minecraft建筑生成模型吧！🚀
