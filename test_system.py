#!/usr/bin/env python3
"""
快速测试整个系统的功能
"""

import sys
import torch
import numpy as np
from pathlib import Path

print("="*60)
print("System Test for DiT Minecraft Voxel Generation")
print("="*60)
print()

# 测试1: 检查依赖
print("Test 1: Checking dependencies...")
try:
    import torch
    import numpy as np
    import google.generativeai as genai
    from tqdm import tqdm
    print(f"  ✓ PyTorch {torch.__version__}")
    print(f"  ✓ NumPy {np.__version__}")
    print(f"  ✓ Google Generative AI")
    print(f"  ✓ tqdm")
except ImportError as e:
    print(f"  ✗ Missing dependency: {e}")
    sys.exit(1)

# 测试2: 检查CUDA
print("\nTest 2: Checking GPU...")
if torch.cuda.is_available():
    print(f"  ✓ CUDA available")
    print(f"  ✓ GPU: {torch.cuda.get_device_name(0)}")
    print(f"  ✓ CUDA Version: {torch.version.cuda}")
    print(f"  ✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print(f"  ⚠ CUDA not available, will use CPU (much slower)")

# 测试3: 测试DiT模型
print("\nTest 3: Testing DiT model...")
try:
    from dit_model import create_dit_small
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = create_dit_small(voxel_size=16, patch_size=2, in_channels=2).to(device)
    
    # 测试前向传播
    batch_size = 2
    x = torch.randn(batch_size, 2, 16, 16, 16).to(device)
    t = torch.randint(0, 1000, (batch_size,)).to(device)
    
    with torch.no_grad():
        output = model(x, t)
    
    assert output.shape == x.shape, f"Output shape mismatch: {output.shape} != {x.shape}"
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  ✓ DiT model created successfully")
    print(f"  ✓ Forward pass works")
    print(f"  ✓ Total parameters: {total_params:,}")
    print(f"  ✓ Input shape: {x.shape}")
    print(f"  ✓ Output shape: {output.shape}")
    
except Exception as e:
    print(f"  ✗ DiT model test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试4: 测试数据集加载
print("\nTest 4: Testing dataset functionality...")
try:
    from dataset_generator import MinecraftDatasetGenerator
    
    print(f"  ✓ Dataset generator imported")
    print(f"  ✓ Ready to generate dataset")
    
except Exception as e:
    print(f"  ✗ Dataset test failed: {e}")
    sys.exit(1)

# 测试5: 测试训练组件
print("\nTest 5: Testing training components...")
try:
    from train import DiffusionScheduler, MinecraftVoxelDataset
    
    scheduler = DiffusionScheduler(num_timesteps=100)
    
    # 测试噪声添加
    x0 = torch.randn(2, 2, 16, 16, 16)
    t = torch.tensor([50, 75])
    xt = scheduler.add_noise(x0, t)
    
    assert xt.shape == x0.shape
    print(f"  ✓ Diffusion scheduler works")
    print(f"  ✓ Training components ready")
    
except Exception as e:
    print(f"  ✗ Training test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试6: 测试推理组件
print("\nTest 6: Testing inference components...")
try:
    from inference import DDPMSampler, DDIMSampler, voxels_to_schematic
    
    # 测试schematic转换
    test_voxels = torch.randn(2, 16, 16, 16)
    schematic = voxels_to_schematic(test_voxels)
    
    assert 'voxels' in schematic
    assert 'size' in schematic
    print(f"  ✓ DDPM sampler ready")
    print(f"  ✓ DDIM sampler ready")
    print(f"  ✓ Schematic conversion works")
    
except Exception as e:
    print(f"  ✗ Inference test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试7: 估算内存需求
print("\nTest 7: Memory estimation...")
model_size = sum(p.numel() * p.element_size() for p in model.parameters()) / 1e9
print(f"  Model size: ~{model_size:.2f} GB")
print(f"  Recommended GPU memory: >={model_size * 4:.0f} GB (for batch training)")

if torch.cuda.is_available():
    gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
    if gpu_mem >= model_size * 4:
        print(f"  ✓ GPU memory sufficient")
    else:
        print(f"  ⚠ GPU memory may be tight, consider smaller batch size")

print("\n" + "="*60)
print("All tests passed! ✓")
print("="*60)
print("\nSystem is ready for:")
print("  1. Dataset generation: python dataset_generator.py")
print("  2. Model training: python train.py")
print("  3. Inference: python inference.py")
print("\nOr run the full pipeline: ./run_pipeline.sh")
print("="*60)
