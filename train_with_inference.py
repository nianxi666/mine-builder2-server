#!/usr/bin/env python3
"""
DiT训练脚本 - 带每N步推理功能
保存所有文件到指定目录
"""

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

# 导入模型和推理
from dit_model import DiT3D
from inference import DDIMSampler, DDPMSampler


class VoxelDataset(Dataset):
    """16x16x16体素数据集"""
    
    def __init__(self, dataset_dir: str):
        self.dataset_dir = Path(dataset_dir)
        self.samples = sorted(list(self.dataset_dir.glob("sample_*")))
        
        if len(self.samples) == 0:
            raise ValueError(f"No samples found in {dataset_dir}")
        
        print(f"Found {len(self.samples)} samples")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample_dir = self.samples[idx]
        npz_file = sample_dir / "voxels.npz"
        
        # 加载NPZ
        data = np.load(npz_file, allow_pickle=True)
        voxels = torch.from_numpy(data['voxels']).float()  # (16,16,16,2)
        prompt = str(data.get('prompt', ''))
        
        # 转换为(2,16,16,16)
        voxels = voxels.permute(3, 0, 1, 2)
        
        # 归一化到[-1, 1]
        voxels = voxels / 127.5 - 1.0
        
        return voxels, prompt


def save_inference_result(voxel_array, output_path, step, sample_idx):
    """保存推理结果"""
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 反归一化
    voxel_array = ((voxel_array + 1.0) * 127.5).clamp(0, 255).cpu().numpy()
    voxel_array = voxel_array.astype(np.int16)
    
    # (2, 16, 16, 16) -> (16, 16, 16, 2)
    voxel_array = voxel_array.transpose(1, 2, 3, 0)
    
    # 保存JSON
    voxels_list = []
    for x in range(16):
        for y in range(16):
            for z in range(16):
                block_id = int(voxel_array[x, y, z, 0])
                meta_data = int(voxel_array[x, y, z, 1])
                if block_id > 0:
                    voxels_list.append({
                        "x": int(x),
                        "y": int(y),
                        "z": int(z),
                        "block_id": block_id,
                        "meta_data": meta_data
                    })
    
    result = {
        "structure_name": f"inference_step_{step}_sample_{sample_idx}",
        "description": f"Generated at training step {step}",
        "voxels": voxels_list
    }
    
    json_file = output_path / f"step_{step:06d}_sample_{sample_idx}.json"
    with open(json_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    return json_file


def inference_during_training(model, device, output_dir, step, num_samples=2, num_steps=10):
    """训练中推理"""
    model.eval()
    
    sampler = DDIMSampler(model, num_steps=num_steps)
    
    print(f"\n🎨 Step {step}: 生成 {num_samples} 个样本...")
    
    with torch.no_grad():
        for i in range(num_samples):
            # 生成
            sample = sampler.sample(
                shape=(2, 16, 16, 16),
                device=device
            )
            
            # 保存
            save_inference_result(
                sample[0],
                output_dir,
                step,
                i
            )
    
    model.train()
    print(f"✅ 推理完成，保存到 {output_dir}")


def train(args):
    """训练函数"""
    
    # 设置输出目录 - 所有文件都在/gemini/code
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    inference_dir = output_dir / "inference_samples"
    inference_dir.mkdir(parents=True, exist_ok=True)
    
    # 设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"🖥️  使用设备: {device}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   显存: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    # 数据集
    print(f"\n📦 加载数据集: {args.dataset_dir}")
    dataset = VoxelDataset(args.dataset_dir)
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    # 模型
    print(f"\n🏗️  创建模型: {args.model_size}")
    if args.model_size == 'small':
        model = DiT3D(hidden_size=384, depth=12, num_heads=6)
    elif args.model_size == 'base':
        model = DiT3D(hidden_size=768, depth=12, num_heads=12)
    elif args.model_size == 'large':
        model = DiT3D(hidden_size=1024, depth=24, num_heads=16)
    else:
        raise ValueError(f"Unknown model size: {args.model_size}")
    
    model = model.to(device)
    
    # 统计参数
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"   总参数: {total_params:,}")
    print(f"   可训练: {trainable_params:,}")
    
    # 优化器
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=0.01,
        betas=(0.9, 0.999)
    )
    
    # AMP
    scaler = torch.cuda.amp.GradScaler() if args.use_amp and torch.cuda.is_available() else None
    
    # 训练循环
    print(f"\n🚀 开始训练...")
    print(f"   Epochs: {args.epochs}")
    print(f"   Batch size: {args.batch_size}")
    print(f"   Learning rate: {args.lr}")
    print(f"   每 {args.inference_every} 步推理一次")
    print("=" * 60)
    
    global_step = 0
    start_time = time.time()
    
    for epoch in range(args.epochs):
        model.train()
        epoch_loss = 0
        
        pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{args.epochs}")
        
        for batch_idx, (voxels, prompts) in enumerate(pbar):
            voxels = voxels.to(device)
            
            # 随机时间步
            batch_size = voxels.shape[0]
            t = torch.randint(0, 1000, (batch_size,), device=device)
            
            # 添加噪声
            noise = torch.randn_like(voxels)
            alpha = (1 - t.float() / 1000).view(-1, 1, 1, 1, 1)
            noisy_voxels = alpha.sqrt() * voxels + (1 - alpha).sqrt() * noise
            
            # 前向传播
            with torch.cuda.amp.autocast(enabled=(scaler is not None)):
                pred_noise = model(noisy_voxels, t)
                loss = nn.functional.mse_loss(pred_noise, noise)
            
            # 反向传播
            optimizer.zero_grad()
            if scaler is not None:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()
            
            epoch_loss += loss.item()
            global_step += 1
            
            # 更新进度条
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'step': global_step
            })
            
            # 每N步推理一次
            if global_step % args.inference_every == 0:
                inference_during_training(
                    model,
                    device,
                    inference_dir,
                    global_step,
                    num_samples=args.inference_samples,
                    num_steps=args.inference_steps
                )
            
            # 保存checkpoint
            if global_step % args.save_every == 0:
                checkpoint_path = checkpoint_dir / f"step_{global_step:06d}.pt"
                torch.save({
                    'step': global_step,
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'loss': loss.item(),
                }, checkpoint_path)
                print(f"💾 保存checkpoint: {checkpoint_path}")
        
        avg_loss = epoch_loss / len(dataloader)
        elapsed = time.time() - start_time
        
        print(f"Epoch {epoch+1}/{args.epochs} - Loss: {avg_loss:.4f} - Time: {elapsed/60:.1f}min")
        
        # 保存最新
        latest_path = checkpoint_dir / "latest.pt"
        torch.save({
            'step': global_step,
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': avg_loss,
        }, latest_path)
    
    print("\n✅ 训练完成！")
    print(f"   总步数: {global_step}")
    print(f"   总时间: {(time.time() - start_time)/3600:.2f} 小时")
    print(f"   Checkpoints: {checkpoint_dir}")
    print(f"   推理样本: {inference_dir}")


def main():
    parser = argparse.ArgumentParser(description="DiT训练 - 带推理测试")
    
    # 数据
    parser.add_argument('--dataset-dir', type=str, default='/gemini/code/dataset',
                        help='数据集目录')
    parser.add_argument('--output-dir', type=str, default='/gemini/code/outputs',
                        help='输出目录（所有文件都保存这里）')
    
    # 模型
    parser.add_argument('--model-size', type=str, default='small',
                        choices=['small', 'base', 'large'],
                        help='模型大小')
    
    # 训练
    parser.add_argument('--batch-size', type=int, default=8,
                        help='批次大小')
    parser.add_argument('--epochs', type=int, default=50,
                        help='训练轮数')
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='学习率')
    parser.add_argument('--num-workers', type=int, default=4,
                        help='数据加载线程数')
    parser.add_argument('--use-amp', action='store_true',
                        help='使用混合精度训练')
    
    # 保存和推理
    parser.add_argument('--save-every', type=int, default=100,
                        help='每N步保存一次checkpoint')
    parser.add_argument('--inference-every', type=int, default=5,
                        help='每N步推理一次')
    parser.add_argument('--inference-samples', type=int, default=2,
                        help='推理时生成的样本数')
    parser.add_argument('--inference-steps', type=int, default=10,
                        help='推理时的采样步数')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("DiT Minecraft 体素生成 - 训练")
    print("=" * 60)
    print(f"配置:")
    for key, value in vars(args).items():
        print(f"  {key}: {value}")
    print("=" * 60)
    
    train(args)


if __name__ == "__main__":
    main()
