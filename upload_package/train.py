#!/usr/bin/env python3
"""
Training script for DiT 3D Voxel Diffusion Model
训练DiT模型生成Minecraft建筑
"""

import os
import json
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import autocast, GradScaler
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

from dit_model import create_dit_small, create_dit_base, create_dit_large


class MinecraftVoxelDataset(Dataset):
    """Minecraft体素数据集"""
    
    def __init__(self, dataset_dir: str, voxel_size: int = 16):
        self.dataset_dir = Path(dataset_dir)
        self.voxel_size = voxel_size
        
        # 扫描所有样本
        self.samples = []
        for sample_dir in sorted(self.dataset_dir.glob("sample_*")):
            npz_path = sample_dir / "voxels.npz"
            if npz_path.exists():
                self.samples.append(npz_path)
        
        print(f"Found {len(self.samples)} samples in {dataset_dir}")
        
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """
        Returns:
            voxels: (2, D, H, W) - block_id and meta_data channels
            prompt: str
        """
        data = np.load(self.samples[idx], allow_pickle=True)
        voxels = data['voxels']  # (D, H, W, 2)
        prompt = str(data['prompt'])
        
        # 转换为 (channels, D, H, W) 格式
        voxels = torch.from_numpy(voxels).permute(3, 0, 1, 2).float()
        
        # 归一化到 [-1, 1]
        voxels = voxels / 127.5 - 1.0
        
        return voxels, prompt


class DiffusionScheduler:
    """扩散过程调度器（DDPM）"""
    
    def __init__(self, num_timesteps: int = 1000, beta_start: float = 0.0001, beta_end: float = 0.02):
        self.num_timesteps = num_timesteps
        
        # 线性beta schedule
        self.betas = torch.linspace(beta_start, beta_end, num_timesteps)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alphas_cumprod_prev = torch.cat([torch.tensor([1.0]), self.alphas_cumprod[:-1]])
        
        # 用于前向扩散
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - self.alphas_cumprod)
        
        # 用于反向采样
        self.posterior_variance = self.betas * (1.0 - self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)
    
    def add_noise(self, x0: torch.Tensor, t: torch.Tensor, noise: torch.Tensor = None) -> torch.Tensor:
        """
        前向扩散：添加噪声
        q(x_t | x_0) = sqrt(alpha_cumprod_t) * x_0 + sqrt(1 - alpha_cumprod_t) * noise
        """
        if noise is None:
            noise = torch.randn_like(x0)
        
        sqrt_alpha_prod = self.sqrt_alphas_cumprod[t].to(x0.device)
        sqrt_one_minus_alpha_prod = self.sqrt_one_minus_alphas_cumprod[t].to(x0.device)
        
        # Reshape for broadcasting
        while len(sqrt_alpha_prod.shape) < len(x0.shape):
            sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)
            sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)
        
        return sqrt_alpha_prod * x0 + sqrt_one_minus_alpha_prod * noise
    
    def sample_timesteps(self, batch_size: int) -> torch.Tensor:
        """随机采样时间步"""
        return torch.randint(0, self.num_timesteps, (batch_size,))


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: optim.Optimizer,
    scheduler: DiffusionScheduler,
    scaler: GradScaler,
    device: torch.device,
    epoch: int,
    args
):
    """训练一个epoch"""
    model.train()
    total_loss = 0
    num_batches = 0
    
    pbar = tqdm(dataloader, desc=f"Epoch {epoch}")
    for batch_idx, (voxels, prompts) in enumerate(pbar):
        voxels = voxels.to(device)  # (B, 2, D, H, W)
        batch_size = voxels.shape[0]
        
        # 随机采样时间步
        t = scheduler.sample_timesteps(batch_size).to(device)
        
        # 添加噪声
        noise = torch.randn_like(voxels)
        noisy_voxels = scheduler.add_noise(voxels, t, noise)
        
        # 前向传播（使用混合精度）
        with autocast(enabled=args.use_amp):
            predicted_noise = model(noisy_voxels, t)
            loss = nn.functional.mse_loss(predicted_noise, noise)
        
        # 反向传播
        optimizer.zero_grad()
        if args.use_amp:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
            optimizer.step()
        
        total_loss += loss.item()
        num_batches += 1
        
        # 更新进度条
        pbar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        # 定期保存检查点
        if (batch_idx + 1) % args.save_every == 0:
            save_checkpoint(model, optimizer, epoch, batch_idx, args)
    
    avg_loss = total_loss / num_batches
    return avg_loss


def save_checkpoint(model: nn.Module, optimizer: optim.Optimizer, epoch: int, batch: int, args):
    """保存检查点"""
    checkpoint_dir = Path(args.output_dir) / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    checkpoint = {
        'epoch': epoch,
        'batch': batch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'args': vars(args)
    }
    
    # 保存最新检查点
    checkpoint_path = checkpoint_dir / f"checkpoint_epoch{epoch}_batch{batch}.pt"
    torch.save(checkpoint, checkpoint_path)
    
    # 保存latest链接
    latest_path = checkpoint_dir / "latest.pt"
    torch.save(checkpoint, latest_path)
    
    print(f"\nCheckpoint saved: {checkpoint_path}")


def load_checkpoint(model: nn.Module, optimizer: optim.Optimizer, checkpoint_path: str):
    """加载检查点"""
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    batch = checkpoint['batch']
    print(f"Loaded checkpoint from epoch {epoch}, batch {batch}")
    return epoch, batch


def main():
    parser = argparse.ArgumentParser(description="Train DiT 3D Voxel Diffusion Model")
    
    # Data
    parser.add_argument('--dataset-dir', type=str, default='dataset', help='Dataset directory')
    parser.add_argument('--output-dir', type=str, default='outputs', help='Output directory')
    
    # Model
    parser.add_argument('--model-size', type=str, default='small', choices=['small', 'base', 'large'],
                        help='DiT model size')
    parser.add_argument('--voxel-size', type=int, default=16, help='Voxel grid size')
    parser.add_argument('--patch-size', type=int, default=2, help='Patch size')
    
    # Training
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=8, help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--weight-decay', type=float, default=0.01, help='Weight decay')
    parser.add_argument('--grad-clip', type=float, default=1.0, help='Gradient clipping')
    parser.add_argument('--use-amp', action='store_true', help='Use automatic mixed precision')
    parser.add_argument('--num-workers', type=int, default=4, help='DataLoader workers')
    
    # Diffusion
    parser.add_argument('--num-timesteps', type=int, default=1000, help='Number of diffusion timesteps')
    
    # Checkpointing
    parser.add_argument('--resume', type=str, default=None, help='Resume from checkpoint')
    parser.add_argument('--save-every', type=int, default=500, help='Save checkpoint every N batches')
    
    args = parser.parse_args()
    
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save config
    with open(output_dir / 'config.json', 'w') as f:
        json.dump(vars(args), f, indent=2)
    
    # Create dataset
    print("\nLoading dataset...")
    dataset = MinecraftVoxelDataset(args.dataset_dir, args.voxel_size)
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=True
    )
    
    # Create model
    print(f"\nCreating DiT-{args.model_size.upper()} model...")
    model_constructors = {
        'small': create_dit_small,
        'base': create_dit_base,
        'large': create_dit_large
    }
    model = model_constructors[args.model_size](
        voxel_size=args.voxel_size,
        patch_size=args.patch_size,
        in_channels=2
    ).to(device)
    
    # Print model info
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    
    # Create optimizer
    optimizer = optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay,
        betas=(0.9, 0.999)
    )
    
    # Create diffusion scheduler
    scheduler = DiffusionScheduler(num_timesteps=args.num_timesteps)
    
    # Create gradient scaler for mixed precision
    scaler = GradScaler(enabled=args.use_amp)
    
    # Resume from checkpoint if specified
    start_epoch = 0
    if args.resume:
        start_epoch, _ = load_checkpoint(model, optimizer, args.resume)
        start_epoch += 1
    
    # Training loop
    print("\n" + "="*60)
    print("Starting training...")
    print("="*60)
    
    for epoch in range(start_epoch, args.epochs):
        print(f"\nEpoch {epoch + 1}/{args.epochs}")
        
        avg_loss = train_one_epoch(
            model, dataloader, optimizer, scheduler, scaler, device, epoch, args
        )
        
        print(f"Epoch {epoch + 1} - Average Loss: {avg_loss:.4f}")
        
        # Save checkpoint at end of epoch
        save_checkpoint(model, optimizer, epoch, len(dataloader) - 1, args)
    
    print("\n" + "="*60)
    print("Training complete!")
    print("="*60)
    
    # Save final model
    final_model_path = output_dir / "final_model.pt"
    torch.save(model.state_dict(), final_model_path)
    print(f"\nFinal model saved: {final_model_path}")


if __name__ == "__main__":
    main()
