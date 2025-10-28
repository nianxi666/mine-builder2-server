#!/usr/bin/env python3
"""
Diffusion Transformer (DiT) for 3D Minecraft Voxel Generation
基于DiT架构的3D体素扩散模型
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple


class TimestepEmbedding(nn.Module):
    """时间步嵌入层"""
    def __init__(self, dim: int, max_period: int = 10000):
        super().__init__()
        self.dim = dim
        self.max_period = max_period
        
    def forward(self, timesteps: torch.Tensor) -> torch.Tensor:
        """
        Args:
            timesteps: (batch_size,)
        Returns:
            (batch_size, dim)
        """
        half = self.dim // 2
        freqs = torch.exp(
            -math.log(self.max_period) * torch.arange(0, half, dtype=torch.float32) / half
        ).to(timesteps.device)
        args = timesteps[:, None].float() * freqs[None]
        embedding = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)
        if self.dim % 2:
            embedding = torch.cat([embedding, torch.zeros_like(embedding[:, :1])], dim=-1)
        return embedding


class PatchEmbed3D(nn.Module):
    """3D Patch Embedding层"""
    def __init__(self, voxel_size: int = 16, patch_size: int = 2, in_channels: int = 2, embed_dim: int = 384):
        super().__init__()
        self.voxel_size = voxel_size
        self.patch_size = patch_size
        self.num_patches = (voxel_size // patch_size) ** 3
        self.embed_dim = embed_dim
        
        # 3D卷积进行patch embedding
        self.proj = nn.Conv3d(in_channels, embed_dim, kernel_size=patch_size, stride=patch_size)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch_size, channels, D, H, W)
        Returns:
            (batch_size, num_patches, embed_dim)
        """
        x = self.proj(x)  # (B, embed_dim, D', H', W')
        x = x.flatten(2)  # (B, embed_dim, num_patches)
        x = x.transpose(1, 2)  # (B, num_patches, embed_dim)
        return x


class MultiHeadAttention3D(nn.Module):
    """多头注意力机制"""
    def __init__(self, dim: int, num_heads: int = 8, dropout: float = 0.0):
        super().__init__()
        assert dim % num_heads == 0
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim ** -0.5
        
        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.proj = nn.Linear(dim, dim)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, N, C = x.shape
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        
        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        attn = self.dropout(attn)
        
        x = (attn @ v).transpose(1, 2).reshape(B, N, C)
        x = self.proj(x)
        x = self.dropout(x)
        return x


class MLP(nn.Module):
    """前馈神经网络"""
    def __init__(self, dim: int, hidden_dim: int, dropout: float = 0.0):
        super().__init__()
        self.fc1 = nn.Linear(dim, hidden_dim)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden_dim, dim)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return x


class DiTBlock(nn.Module):
    """DiT Transformer Block with adaptive layer norm"""
    def __init__(self, dim: int, num_heads: int, mlp_ratio: float = 4.0, dropout: float = 0.0):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = MultiHeadAttention3D(dim, num_heads, dropout)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = MLP(dim, int(dim * mlp_ratio), dropout)
        
        # Adaptive layer norm parameters (conditioned on timestep)
        self.adaLN_modulation = nn.Sequential(
            nn.SiLU(),
            nn.Linear(dim, 6 * dim, bias=True)
        )
        
    def forward(self, x: torch.Tensor, c: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch_size, num_patches, dim)
            c: (batch_size, dim) - timestep conditioning
        """
        # Get modulation parameters
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = \
            self.adaLN_modulation(c).chunk(6, dim=1)
        
        # Self-attention with adaptive layer norm
        x = x + gate_msa.unsqueeze(1) * self.attn(
            self._modulate(self.norm1(x), shift_msa, scale_msa)
        )
        
        # MLP with adaptive layer norm
        x = x + gate_mlp.unsqueeze(1) * self.mlp(
            self._modulate(self.norm2(x), shift_mlp, scale_mlp)
        )
        
        return x
    
    def _modulate(self, x: torch.Tensor, shift: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
        return x * (1 + scale.unsqueeze(1)) + shift.unsqueeze(1)


class FinalLayer(nn.Module):
    """最终输出层"""
    def __init__(self, hidden_size: int, patch_size: int, out_channels: int):
        super().__init__()
        self.norm_final = nn.LayerNorm(hidden_size)
        self.linear = nn.Linear(hidden_size, patch_size ** 3 * out_channels, bias=True)
        self.adaLN_modulation = nn.Sequential(
            nn.SiLU(),
            nn.Linear(hidden_size, 2 * hidden_size, bias=True)
        )
        
    def forward(self, x: torch.Tensor, c: torch.Tensor) -> torch.Tensor:
        shift, scale = self.adaLN_modulation(c).chunk(2, dim=1)
        x = self._modulate(self.norm_final(x), shift, scale)
        x = self.linear(x)
        return x
    
    def _modulate(self, x: torch.Tensor, shift: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
        return x * (1 + scale.unsqueeze(1)) + shift.unsqueeze(1)


class DiT3D(nn.Module):
    """
    Diffusion Transformer for 3D Voxel Generation
    """
    def __init__(
        self,
        voxel_size: int = 16,
        patch_size: int = 2,
        in_channels: int = 2,  # block_id + meta_data
        hidden_size: int = 384,
        depth: int = 12,
        num_heads: int = 6,
        mlp_ratio: float = 4.0,
        dropout: float = 0.1,
        num_classes: int = 0,  # 暂不使用类别条件
    ):
        super().__init__()
        self.voxel_size = voxel_size
        self.patch_size = patch_size
        self.in_channels = in_channels
        self.out_channels = in_channels
        self.num_heads = num_heads
        
        # Patch embedding
        self.patch_embed = PatchEmbed3D(voxel_size, patch_size, in_channels, hidden_size)
        num_patches = self.patch_embed.num_patches
        
        # Timestep embedding
        self.time_embed = nn.Sequential(
            TimestepEmbedding(hidden_size),
            nn.Linear(hidden_size, hidden_size),
            nn.SiLU(),
            nn.Linear(hidden_size, hidden_size),
        )
        
        # Positional embedding
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches, hidden_size))
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            DiTBlock(hidden_size, num_heads, mlp_ratio, dropout)
            for _ in range(depth)
        ])
        
        # Final layer
        self.final_layer = FinalLayer(hidden_size, patch_size, self.out_channels)
        
        self.initialize_weights()
        
    def initialize_weights(self):
        """初始化权重"""
        # Initialize patch_embed like nn.Linear
        w = self.patch_embed.proj.weight.data
        nn.init.xavier_uniform_(w.view([w.shape[0], -1]))
        nn.init.constant_(self.patch_embed.proj.bias, 0)
        
        # Initialize positional embedding
        nn.init.normal_(self.pos_embed, std=0.02)
        
        # Initialize timestep embedding
        for module in self.time_embed.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, std=0.02)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
        
        # Initialize transformer blocks
        for block in self.blocks:
            nn.init.constant_(block.adaLN_modulation[-1].weight, 0)
            nn.init.constant_(block.adaLN_modulation[-1].bias, 0)
        
        # Zero-out final layer
        nn.init.constant_(self.final_layer.adaLN_modulation[-1].weight, 0)
        nn.init.constant_(self.final_layer.adaLN_modulation[-1].bias, 0)
        nn.init.constant_(self.final_layer.linear.weight, 0)
        nn.init.constant_(self.final_layer.linear.bias, 0)
    
    def unpatchify(self, x: torch.Tensor) -> torch.Tensor:
        """
        将patch序列转换回3D体素
        Args:
            x: (batch_size, num_patches, patch_size^3 * channels)
        Returns:
            (batch_size, channels, D, H, W)
        """
        c = self.out_channels
        p = self.patch_size
        d = h = w = self.voxel_size // p
        
        x = x.reshape(shape=(x.shape[0], d, h, w, p, p, p, c))
        x = torch.einsum('ndhwpqrc->ncdphqwr', x)
        voxels = x.reshape(shape=(x.shape[0], c, d * p, h * p, w * p))
        return voxels
    
    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch_size, channels, D, H, W) - noisy voxels
            t: (batch_size,) - timesteps
        Returns:
            (batch_size, channels, D, H, W) - predicted noise
        """
        # Embed patches
        x = self.patch_embed(x)  # (B, num_patches, hidden_size)
        x = x + self.pos_embed  # Add positional embedding
        
        # Embed timesteps
        t = self.time_embed(t)  # (B, hidden_size)
        
        # Apply DiT blocks
        for block in self.blocks:
            x = block(x, t)
        
        # Final layer
        x = self.final_layer(x, t)  # (B, num_patches, patch_size^3 * out_channels)
        
        # Unpatchify
        x = self.unpatchify(x)  # (B, out_channels, D, H, W)
        
        return x


def create_dit_small(**kwargs):
    """创建小型DiT模型"""
    return DiT3D(hidden_size=384, depth=12, num_heads=6, **kwargs)


def create_dit_base(**kwargs):
    """创建基础DiT模型"""
    return DiT3D(hidden_size=512, depth=16, num_heads=8, **kwargs)


def create_dit_large(**kwargs):
    """创建大型DiT模型"""
    return DiT3D(hidden_size=768, depth=24, num_heads=12, **kwargs)


if __name__ == "__main__":
    # 测试模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = create_dit_small(voxel_size=16, patch_size=2, in_channels=2).to(device)
    
    # 打印模型信息
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"DiT-S/2 Model")
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    
    # 测试前向传播
    batch_size = 2
    x = torch.randn(batch_size, 2, 16, 16, 16).to(device)
    t = torch.randint(0, 1000, (batch_size,)).to(device)
    
    with torch.no_grad():
        output = model(x, t)
    
    print(f"\nInput shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print("\nModel test passed!")
