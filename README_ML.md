# Minecraft Voxel Generation with DiT (Diffusion Transformer)

使用最新的Diffusion Transformer (DiT)架构生成16x16x16的Minecraft建筑结构。

## 🚀 特性

- **DiT架构**: 使用最新的Diffusion Transformer替代传统UNet
- **函数调用**: 使用Gemini 2.5 Pro的Function Calling生成结构化数据集
- **3D扩散模型**: 专为3D体素数据设计的扩散模型
- **高效训练**: 支持混合精度训练和梯度累积
- **灵活采样**: 支持DDPM和DDIM采样器

## 📦 安装

```bash
# 安装ML训练依赖
pip install -r requirements_ml.txt

# 如果使用GPU，确保安装CUDA版本的PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 📊 数据集生成

### 步骤1: 生成数据集

使用Gemini 2.5 Pro生成1000个训练样本：

```bash
python dataset_generator.py \
  --api-key YOUR_API_KEY \
  --output-dir dataset \
  --num-samples 1000 \
  --model gemini-2.0-flash-exp
```

**参数说明**:
- `--api-key`: Google AI Studio API密钥
- `--output-dir`: 数据集输出目录
- `--num-samples`: 生成样本数量
- `--model`: 使用的Gemini模型（推荐使用gemini-2.0-flash-exp，速度快成本低）

**数据集结构**:
```
dataset/
├── sample_0000/
│   ├── data.json        # 人类可读的JSON格式
│   └── voxels.npz       # 训练用的压缩格式
├── sample_0001/
├── ...
└── metadata.json        # 数据集元信息
```

### 数据集特点

1. **多样性**: 包含房屋、塔、雕塑、树木等多种建筑类型
2. **结构化输出**: 使用函数调用确保AI返回正确格式，避免对话式输出
3. **方块字典参考**: AI会参考Minecraft方块ID字典生成真实的建筑
4. **自动重试**: 遇到API 429错误会自动重试，支持断点续传

## 🏋️ 模型训练

### DiT模型架构选择

提供三种模型大小：

| 模型 | 参数量 | Hidden Size | Depth | Heads | 推荐用途 |
|------|--------|-------------|-------|-------|----------|
| DiT-Small | ~33M | 384 | 12 | 6 | 快速实验 |
| DiT-Base | ~86M | 512 | 16 | 8 | 平衡性能 |
| DiT-Large | ~458M | 768 | 24 | 12 | 最佳质量 |

### 步骤2: 训练模型

#### 基础训练（单GPU）

```bash
python train.py \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size small \
  --batch-size 8 \
  --epochs 100 \
  --lr 1e-4 \
  --use-amp \
  --save-every 500
```

#### 推荐配置（GPU服务器）

```bash
# 使用Base模型，混合精度训练
python train.py \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size base \
  --batch-size 16 \
  --epochs 200 \
  --lr 1e-4 \
  --weight-decay 0.01 \
  --grad-clip 1.0 \
  --use-amp \
  --num-workers 8 \
  --save-every 1000
```

#### 高端配置（多GPU/A100）

```bash
# Large模型，更大batch size
python train.py \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size large \
  --batch-size 32 \
  --epochs 300 \
  --lr 5e-5 \
  --use-amp \
  --num-workers 16
```

**训练参数说明**:
- `--model-size`: 模型大小（small/base/large）
- `--batch-size`: 批次大小（根据GPU内存调整）
- `--epochs`: 训练轮数
- `--lr`: 学习率
- `--use-amp`: 启用混合精度训练（节省显存，加速训练）
- `--grad-clip`: 梯度裁剪阈值
- `--save-every`: 每N个batch保存一次检查点

### 从检查点恢复训练

```bash
python train.py \
  --resume outputs/checkpoints/latest.pt \
  --dataset-dir dataset \
  --output-dir outputs \
  --model-size small
```

## 🎨 生成新建筑

### 步骤3: 推理生成

```bash
# 使用DDIM快速采样（推荐）
python inference.py \
  --checkpoint outputs/checkpoints/latest.pt \
  --model-size small \
  --num-samples 10 \
  --sampler ddim \
  --num-steps 50 \
  --output-dir generated

# 使用DDPM完整采样（质量更高但更慢）
python inference.py \
  --checkpoint outputs/final_model.pt \
  --model-size small \
  --num-samples 5 \
  --sampler ddpm \
  --output-dir generated
```

**推理参数**:
- `--checkpoint`: 模型检查点路径
- `--num-samples`: 生成样本数量
- `--sampler`: 采样器类型（ddim推荐，更快）
- `--num-steps`: DDIM采样步数（50通常足够，越大质量越好但越慢）
- `--batch-size`: 批量生成大小

### 生成结果

生成的文件保存在`generated/`目录：
```
generated/
├── sample_0000.json    # JSON格式schematic
├── sample_0000.npz     # NPZ格式（可直接加载）
├── sample_0001.json
└── ...
```

## 🔧 工作流程示例

### 完整流程（从零开始）

```bash
# 1. 生成数据集（约30分钟，1000样本）
python dataset_generator.py \
  --api-key YOUR_API_KEY \
  --num-samples 1000

# 2. 训练模型（GPU服务器上，约2-8小时）
python train.py \
  --model-size base \
  --batch-size 16 \
  --epochs 100 \
  --use-amp

# 3. 生成新建筑
python inference.py \
  --checkpoint outputs/checkpoints/latest.pt \
  --model-size base \
  --num-samples 20 \
  --sampler ddim
```

## 📈 训练监控

训练过程会保存：
- **检查点**: `outputs/checkpoints/` 
- **配置文件**: `outputs/config.json`
- **最终模型**: `outputs/final_model.pt`

监控训练loss：
```bash
# 查看训练日志
tail -f outputs/train.log

# 如果安装了tensorboard
tensorboard --logdir outputs/logs
```

## 🎯 性能优化建议

### GPU内存优化

如果遇到OOM错误：
1. 减小`--batch-size`
2. 使用`--use-amp`启用混合精度
3. 减少`--num-workers`
4. 使用更小的模型（small而不是base）

### 训练速度优化

1. **使用DDIM采样**: 比DDPM快20倍，质量相近
2. **混合精度训练**: 启用`--use-amp`
3. **增加batch size**: 充分利用GPU
4. **多worker数据加载**: 设置`--num-workers=8`

### 生成质量优化

1. **增加训练epoch**: 至少100个epoch
2. **使用更大模型**: base或large
3. **增加数据集大小**: 2000-5000样本更好
4. **调整采样步数**: DDIM使用50-100步

## 🐛 常见问题

### Q: API 429错误

A: 脚本会自动重试。如果频繁遇到，可以：
- 增加采样间隔时间
- 使用多个API密钥轮换
- 使用更便宜的模型（gemini-2.0-flash-exp）

### Q: 训练loss不下降

A: 检查：
- 数据集质量（是否有足够多样本）
- 学习率（尝试1e-4到1e-5）
- 模型大小（可能需要更大模型）

### Q: 生成结果不好

A: 
- 训练更多epochs（至少100）
- 增加数据集大小和多样性
- 使用DDIM采样并增加步数
- 尝试更大的模型

## 📚 技术细节

### DiT架构

基于论文 "Scalable Diffusion Models with Transformers" (2023):
- 使用Transformer替代传统UNet
- Adaptive Layer Normalization条件化时间步
- 3D Patch Embedding处理体素数据
- 更好的可扩展性和性能

### 扩散过程

- **训练**: 学习预测添加到数据的噪声
- **采样**: 从随机噪声逐步去噪生成结构
- **DDPM**: 原始采样算法，1000步
- **DDIM**: 确定性采样，可用50步达到相似质量

### 数据格式

体素数据：`(D, H, W, 2)` 其中：
- D, H, W = 16 (体素分辨率)
- 通道0: block_id (方块类型)
- 通道1: meta_data (方块变体)

## 🤝 进阶使用

### 自定义数据集

修改`dataset_generator.py`中的`BUILDING_PROMPTS`添加新建筑类型：

```python
BUILDING_PROMPTS = [
    "Your custom prompt 1",
    "Your custom prompt 2",
    # ...
]
```

### 条件生成（TODO）

未来可以添加文本条件：
- 修改DiT模型添加文本编码器
- 在训练时使用prompt作为条件
- 推理时提供文本描述生成对应建筑

## 📝 引用

如果使用此代码，请引用：

```bibtex
@article{peebles2023dit,
  title={Scalable Diffusion Models with Transformers},
  author={Peebles, William and Xie, Saining},
  journal={arXiv preprint arXiv:2212.09748},
  year={2023}
}
```

## 📄 许可证

MIT License

## 🙏 致谢

- DiT论文和实现
- Google Gemini API
- Minecraft社区
