#!/usr/bin/env python3
"""
创建合成数据集用于测试训练流程
不需要API调用，直接生成规则化的Minecraft建筑
"""

import json
import random
import numpy as np
from pathlib import Path
from tqdm import tqdm


def generate_cube(size=4, block_id=1):
    """生成立方体"""
    voxels = []
    offset = (16 - size) // 2
    for x in range(size):
        for y in range(size):
            for z in range(size):
                # 只在表面
                if x in [0, size-1] or y in [0, size-1] or z in [0, size-1]:
                    voxels.append({
                        'x': offset + x,
                        'y': y,
                        'z': offset + z,
                        'block_id': block_id,
                        'meta_data': 0
                    })
    return voxels


def generate_tower(height=12, width=6, block_id=4):
    """生成塔"""
    voxels = []
    offset = (16 - width) // 2
    for y in range(height):
        for x in range(width):
            for z in range(width):
                # 墙壁
                if x in [0, width-1] or z in [0, width-1]:
                    voxels.append({
                        'x': offset + x,
                        'y': y,
                        'z': offset + z,
                        'block_id': block_id,
                        'meta_data': 0
                    })
    return voxels


def generate_pyramid(height=8, block_id=24):
    """生成金字塔"""
    voxels = []
    for y in range(height):
        size = height - y
        offset = (16 - size) // 2
        for x in range(size):
            for z in range(size):
                voxels.append({
                    'x': offset + x,
                    'y': y,
                    'z': offset + z,
                    'block_id': block_id,
                    'meta_data': 0
                })
    return voxels


def generate_house():
    """生成简单房屋"""
    voxels = []
    # 地基
    for x in range(4, 12):
        for z in range(4, 12):
            voxels.append({'x': x, 'y': 0, 'z': z, 'block_id': 1, 'meta_data': 0})
    
    # 墙
    for y in range(1, 5):
        for x in range(4, 12):
            for z in range(4, 12):
                if x in [4, 11] or z in [4, 11]:
                    voxels.append({'x': x, 'y': y, 'z': z, 'block_id': 5, 'meta_data': 0})
    
    # 屋顶
    for x in range(4, 12):
        for z in range(4, 12):
            voxels.append({'x': x, 'y': 5, 'z': z, 'block_id': 17, 'meta_data': 0})
    
    return voxels


def generate_tree():
    """生成树"""
    voxels = []
    # 树干
    for y in range(4):
        voxels.append({'x': 8, 'y': y, 'z': 8, 'block_id': 17, 'meta_data': 0})
    
    # 树叶
    for x in range(6, 11):
        for y in range(3, 7):
            for z in range(6, 11):
                dist = abs(x - 8) + abs(z - 8)
                if dist <= 3 and random.random() > 0.3:
                    voxels.append({'x': x, 'y': y, 'z': z, 'block_id': 18, 'meta_data': 0})
    
    return voxels


def generate_wall(length=12, height=6, block_id=4):
    """生成墙"""
    voxels = []
    offset = (16 - length) // 2
    for y in range(height):
        for x in range(length):
            voxels.append({
                'x': offset + x,
                'y': y,
                'z': 8,
                'block_id': block_id,
                'meta_data': 0
            })
    return voxels


def generate_arch():
    """生成拱门"""
    voxels = []
    # 两侧柱子
    for y in range(6):
        voxels.append({'x': 6, 'y': y, 'z': 8, 'block_id': 98, 'meta_data': 0})
        voxels.append({'x': 10, 'y': y, 'z': 8, 'block_id': 98, 'meta_data': 0})
    
    # 拱顶
    for x in range(7, 10):
        voxels.append({'x': x, 'y': 5, 'z': 8, 'block_id': 98, 'meta_data': 0})
    
    return voxels


# 生成器列表
GENERATORS = [
    (generate_cube, "cube"),
    (generate_tower, "tower"),
    (generate_pyramid, "pyramid"),
    (generate_house, "house"),
    (generate_tree, "tree"),
    (generate_wall, "wall"),
    (generate_arch, "arch"),
]


def create_dataset(output_dir: str, num_samples: int = 1000):
    """创建合成数据集"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating synthetic dataset: {num_samples} samples")
    print(f"Output directory: {output_path}")
    print("=" * 60)
    
    for i in tqdm(range(num_samples), desc="Generating"):
        # 随机选择生成器
        gen_func, gen_name = random.choice(GENERATORS)
        
        # 生成voxels
        voxels = gen_func()
        
        # 添加随机变化
        if random.random() > 0.5:
            # 随机旋转
            angle = random.choice([0, 90, 180, 270])
            if angle > 0:
                for v in voxels:
                    x, z = v['x'] - 8, v['z'] - 8
                    if angle == 90:
                        v['x'], v['z'] = 8 - z, 8 + x
                    elif angle == 180:
                        v['x'], v['z'] = 8 - x, 8 - z
                    elif angle == 270:
                        v['x'], v['z'] = 8 + z, 8 - x
        
        # 创建数据
        data = {
            'prompt': f"A {gen_name} structure variant {i % 10}",
            'structure_name': gen_name,
            'voxels': voxels
        }
        
        # 保存
        sample_dir = output_path / f"sample_{i:04d}"
        sample_dir.mkdir(exist_ok=True)
        
        # JSON
        with open(sample_dir / "data.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        # NPZ
        voxel_array = np.zeros((16, 16, 16, 2), dtype=np.int16)
        for v in voxels:
            if 0 <= v['x'] < 16 and 0 <= v['y'] < 16 and 0 <= v['z'] < 16:
                voxel_array[v['x'], v['y'], v['z'], 0] = v['block_id']
                voxel_array[v['x'], v['y'], v['z'], 1] = v['meta_data']
        
        np.savez_compressed(
            sample_dir / "voxels.npz",
            voxels=voxel_array,
            prompt=data['prompt']
        )
    
    # 元数据
    metadata = {
        'total_samples': num_samples,
        'type': 'synthetic',
        'generators': [name for _, name in GENERATORS]
    }
    with open(output_path / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nDataset created: {num_samples} samples")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='dataset')
    parser.add_argument('--num-samples', type=int, default=1000)
    args = parser.parse_args()
    
    create_dataset(args.output_dir, args.num_samples)
