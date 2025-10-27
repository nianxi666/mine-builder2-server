#!/usr/bin/env python3
"""
Inference script for DiT 3D Voxel Diffusion Model
使用训练好的模型生成Minecraft建筑
"""

import os
import json
import argparse
import numpy as np
from pathlib import Path
import torch
import torch.nn as nn
from tqdm import tqdm

from dit_model import create_dit_small, create_dit_base, create_dit_large


class DDPMSampler:
    """DDPM采样器"""
    
    def __init__(self, num_timesteps: int = 1000, beta_start: float = 0.0001, beta_end: float = 0.02):
        self.num_timesteps = num_timesteps
        
        # Beta schedule
        self.betas = torch.linspace(beta_start, beta_end, num_timesteps)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alphas_cumprod_prev = torch.cat([torch.tensor([1.0]), self.alphas_cumprod[:-1]])
        
        # 采样所需的系数
        self.sqrt_recip_alphas = torch.sqrt(1.0 / self.alphas)
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - self.alphas_cumprod)
        self.posterior_variance = self.betas * (1.0 - self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)
    
    @torch.no_grad()
    def sample(
        self,
        model: nn.Module,
        shape: tuple,
        device: torch.device,
        return_all_timesteps: bool = False
    ) -> torch.Tensor:
        """
        使用DDPM采样生成体素
        
        Args:
            model: 训练好的DiT模型
            shape: 输出形状 (batch_size, channels, D, H, W)
            device: 设备
            return_all_timesteps: 是否返回所有时间步的结果
            
        Returns:
            生成的体素数据
        """
        batch_size = shape[0]
        
        # 从纯噪声开始
        img = torch.randn(shape, device=device)
        
        imgs = []
        
        # 逐步去噪
        for t in tqdm(reversed(range(self.num_timesteps)), desc='Sampling', total=self.num_timesteps):
            t_batch = torch.full((batch_size,), t, device=device, dtype=torch.long)
            
            # 预测噪声
            predicted_noise = model(img, t_batch)
            
            # 计算去噪后的图像
            beta_t = self.betas[t].to(device)
            sqrt_recip_alpha_t = self.sqrt_recip_alphas[t].to(device)
            sqrt_one_minus_alpha_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t].to(device)
            
            # x_{t-1} = sqrt(1/alpha_t) * (x_t - (beta_t / sqrt(1 - alpha_cumprod_t)) * predicted_noise)
            img = sqrt_recip_alpha_t * (img - beta_t / sqrt_one_minus_alpha_cumprod_t * predicted_noise)
            
            # 添加噪声（除了最后一步）
            if t > 0:
                noise = torch.randn_like(img)
                posterior_variance_t = self.posterior_variance[t].to(device)
                img = img + torch.sqrt(posterior_variance_t) * noise
            
            if return_all_timesteps:
                imgs.append(img.cpu())
        
        if return_all_timesteps:
            return torch.stack(imgs, dim=0)
        
        return img


class DDIMSampler:
    """DDIM采样器（更快的采样）"""
    
    def __init__(self, num_timesteps: int = 1000, beta_start: float = 0.0001, beta_end: float = 0.02):
        self.num_timesteps = num_timesteps
        
        # Beta schedule
        self.betas = torch.linspace(beta_start, beta_end, num_timesteps)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - self.alphas_cumprod)
    
    @torch.no_grad()
    def sample(
        self,
        model: nn.Module,
        shape: tuple,
        device: torch.device,
        num_steps: int = 50,
        eta: float = 0.0
    ) -> torch.Tensor:
        """
        使用DDIM采样（可以用更少的步数）
        
        Args:
            model: 训练好的DiT模型
            shape: 输出形状
            device: 设备
            num_steps: 采样步数（可以远小于训练时的timesteps）
            eta: 随机性参数（0=确定性采样）
        """
        batch_size = shape[0]
        
        # 选择采样时间步
        skip = self.num_timesteps // num_steps
        seq = range(0, self.num_timesteps, skip)
        seq_next = [-1] + list(seq[:-1])
        
        # 从纯噪声开始
        img = torch.randn(shape, device=device)
        
        # 逐步去噪
        for i, j in tqdm(zip(reversed(seq), reversed(seq_next)), desc='DDIM Sampling', total=len(seq)):
            t = torch.full((batch_size,), i, device=device, dtype=torch.long)
            
            # 预测噪声
            predicted_noise = model(img, t)
            
            # 获取alpha值
            alpha_t = self.alphas_cumprod[i].to(device)
            alpha_t_prev = self.alphas_cumprod[j].to(device) if j >= 0 else torch.tensor(1.0).to(device)
            
            sqrt_alpha_t = torch.sqrt(alpha_t)
            sqrt_one_minus_alpha_t = torch.sqrt(1.0 - alpha_t)
            
            # 预测x0
            pred_x0 = (img - sqrt_one_minus_alpha_t * predicted_noise) / sqrt_alpha_t
            
            # 方向指向xt
            dir_xt = torch.sqrt(1.0 - alpha_t_prev - eta ** 2) * predicted_noise
            
            # 添加噪声
            if eta > 0 and j >= 0:
                noise = torch.randn_like(img)
                sigma_t = eta * torch.sqrt((1 - alpha_t_prev) / (1 - alpha_t)) * torch.sqrt(1 - alpha_t / alpha_t_prev)
            else:
                noise = 0
                sigma_t = 0
            
            # 计算x_{t-1}
            img = torch.sqrt(alpha_t_prev) * pred_x0 + dir_xt + sigma_t * noise
        
        return img


def voxels_to_schematic(voxels: torch.Tensor) -> dict:
    """
    将体素数组转换为schematic格式
    
    Args:
        voxels: (channels, D, H, W) tensor
        
    Returns:
        schematic字典
    """
    # 反归一化
    voxels = ((voxels + 1.0) * 127.5).clamp(0, 255).cpu().numpy().astype(np.uint8)
    
    # 转换为 (D, H, W, 2) 格式
    voxels = np.transpose(voxels, (1, 2, 3, 0))
    
    # 提取非空体素
    voxel_list = []
    for x in range(voxels.shape[0]):
        for y in range(voxels.shape[1]):
            for z in range(voxels.shape[2]):
                block_id = int(voxels[x, y, z, 0])
                meta_data = int(voxels[x, y, z, 1])
                
                # 跳过空气方块（ID=0）
                if block_id > 0:
                    voxel_list.append({
                        'x': int(x),
                        'y': int(y),
                        'z': int(z),
                        'block_id': block_id,
                        'meta_data': meta_data
                    })
    
    return {
        'size': list(voxels.shape[:3]),
        'voxels': voxel_list
    }


def save_schematic(schematic: dict, output_path: str, prompt: str = ""):
    """保存schematic到文件"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        'prompt': prompt,
        'schematic': schematic
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # 同时保存为NPZ格式
    npz_path = output_path.with_suffix('.npz')
    voxel_array = np.zeros((16, 16, 16, 2), dtype=np.int16)
    for v in schematic['voxels']:
        voxel_array[v['x'], v['y'], v['z'], 0] = v['block_id']
        voxel_array[v['x'], v['y'], v['z'], 1] = v['meta_data']
    np.savez_compressed(npz_path, voxels=voxel_array, prompt=prompt)


def main():
    parser = argparse.ArgumentParser(description="Generate Minecraft structures using DiT")
    
    # Model
    parser.add_argument('--checkpoint', type=str, required=True, help='Model checkpoint path')
    parser.add_argument('--model-size', type=str, default='small', choices=['small', 'base', 'large'])
    parser.add_argument('--voxel-size', type=int, default=16)
    parser.add_argument('--patch-size', type=int, default=2)
    
    # Sampling
    parser.add_argument('--num-samples', type=int, default=4, help='Number of samples to generate')
    parser.add_argument('--batch-size', type=int, default=1, help='Batch size for sampling')
    parser.add_argument('--sampler', type=str, default='ddim', choices=['ddpm', 'ddim'])
    parser.add_argument('--num-steps', type=int, default=50, help='Number of sampling steps (DDIM only)')
    parser.add_argument('--num-timesteps', type=int, default=1000, help='Total diffusion timesteps')
    
    # Output
    parser.add_argument('--output-dir', type=str, default='generated', help='Output directory')
    parser.add_argument('--prompt', type=str, default='', help='Optional prompt for logging')
    
    args = parser.parse_args()
    
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load model
    print(f"\nLoading DiT-{args.model_size.upper()} model...")
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
    
    # Load checkpoint
    checkpoint = torch.load(args.checkpoint, map_location=device)
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    
    model.eval()
    print("Model loaded successfully!")
    
    # Create sampler
    if args.sampler == 'ddpm':
        sampler = DDPMSampler(num_timesteps=args.num_timesteps)
        print(f"\nUsing DDPM sampler with {args.num_timesteps} steps")
    else:
        sampler = DDIMSampler(num_timesteps=args.num_timesteps)
        print(f"\nUsing DDIM sampler with {args.num_steps} steps")
    
    # Generate samples
    print(f"\nGenerating {args.num_samples} samples...")
    print("=" * 60)
    
    num_batches = (args.num_samples + args.batch_size - 1) // args.batch_size
    sample_idx = 0
    
    for batch_idx in range(num_batches):
        current_batch_size = min(args.batch_size, args.num_samples - sample_idx)
        shape = (current_batch_size, 2, args.voxel_size, args.voxel_size, args.voxel_size)
        
        print(f"\nBatch {batch_idx + 1}/{num_batches}")
        
        # Sample
        if args.sampler == 'ddpm':
            samples = sampler.sample(model, shape, device)
        else:
            samples = sampler.sample(model, shape, device, num_steps=args.num_steps)
        
        # Save each sample
        for i in range(current_batch_size):
            voxels = samples[i]
            schematic = voxels_to_schematic(voxels)
            
            output_path = output_dir / f"sample_{sample_idx:04d}.json"
            save_schematic(schematic, output_path, args.prompt)
            
            num_blocks = len(schematic['voxels'])
            print(f"  Sample {sample_idx}: {num_blocks} blocks -> {output_path}")
            
            sample_idx += 1
    
    print("\n" + "=" * 60)
    print(f"Generation complete! {args.num_samples} samples saved to {output_dir}")


if __name__ == "__main__":
    main()
