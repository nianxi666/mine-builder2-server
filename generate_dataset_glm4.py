#!/usr/bin/env python3
"""
使用GLM-4.6生成Minecraft建筑数据集
通过ModelScope API，可以在远程GPU服务器直接运行（无需翻墙）
"""

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
from openai import OpenAI
from tqdm import tqdm


# Minecraft方块ID字典
BLOCK_IDS = {
    "stone": 1, "grass": 2, "dirt": 3, "cobblestone": 4, "planks": 5,
    "bedrock": 7, "water": 8, "lava": 10, "sand": 12, "gravel": 13,
    "gold_ore": 14, "iron_ore": 15, "coal_ore": 16, "log": 17, "leaves": 18,
    "glass": 20, "lapis_ore": 21, "sandstone": 24, "wool": 35, "gold_block": 41,
    "iron_block": 42, "stone_slab": 44, "brick_block": 45, "tnt": 46,
    "bookshelf": 47, "mossy_cobblestone": 48, "obsidian": 49, "torch": 50,
    "oak_stairs": 53, "chest": 54, "diamond_ore": 56, "diamond_block": 57,
    "crafting_table": 58, "farmland": 60, "furnace": 61, "ladder": 65,
    "stone_stairs": 67, "snow": 78, "ice": 79, "snow_block": 80, "cactus": 81,
    "clay": 82, "fence": 85, "netherrack": 87, "glowstone": 89, "stone_brick": 98,
    "glass_pane": 102, "melon": 103, "fence_gate": 107, "brick_stairs": 108,
    "stone_brick_stairs": 109, "nether_brick": 112, "nether_brick_stairs": 114,
    "quartz_ore": 153, "quartz_block": 155, "quartz_stairs": 156, "prismarine": 168,
    "sea_lantern": 169, "red_sandstone": 179, "purpur_block": 201, "end_stone": 121,
    "end_stone_bricks": 206, "concrete": 251
}


def create_glm4_client():
    """创建GLM-4.6客户端"""
    return OpenAI(
        base_url='https://api-inference.modelscope.cn/v1',
        api_key='ms-35a044f4-7e2c-4df3-8d97-c8ac7052cca8',
    )


def generate_minecraft_structure_glm4(client, structure_type: str, retry_count: int = 3):
    """使用GLM-4.6生成Minecraft建筑结构"""
    
    # 创建详细的提示词
    block_ids_str = ", ".join([f"{name}={id}" for name, id in list(BLOCK_IDS.items())[:20]])
    
    prompt = f"""你是一个Minecraft建筑专家。请生成一个{structure_type}的3D体素数据。

规格要求：
- 空间大小：16x16x16体素
- 坐标系：x,y,z都是0-15
- 方块ID：使用真实的Minecraft方块ID（{block_ids_str}等）
- 建筑要求：真实、美观、结构完整

请生成{structure_type}的方块列表，格式为JSON数组，每个方块包含：
- x, y, z：坐标（0-15）
- block_id：方块ID（使用上面列出的真实ID）
- meta_data：元数据（通常为0）

要求：
1. 方块数量：50-250个（不要太少也不要太多）
2. 结构合理：{structure_type}应该看起来真实
3. 使用多种方块：让建筑更丰富
4. 只返回JSON数组，不要其他解释

示例格式：
[
  {{"x": 7, "y": 0, "z": 7, "block_id": 1, "meta_data": 0}},
  {{"x": 7, "y": 1, "z": 7, "block_id": 5, "meta_data": 0}}
]

现在请生成{structure_type}："""

    for attempt in range(retry_count):
        try:
            response = client.chat.completions.create(
                model='ZhipuAI/GLM-4.6',
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个Minecraft建筑专家，精通体素建模和建筑设计。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.9,
                max_tokens=4000,
            )
            
            # 获取响应内容
            content = response.choices[0].message.content
            
            # 清理响应（移除可能的markdown标记）
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 解析JSON
            voxels = json.loads(content)
            
            # 验证数据
            if not isinstance(voxels, list) or len(voxels) < 10:
                raise ValueError(f"生成的方块太少: {len(voxels) if isinstance(voxels, list) else 0}")
            
            # 验证每个方块
            valid_voxels = []
            for v in voxels:
                if all(k in v for k in ['x', 'y', 'z', 'block_id']):
                    x, y, z = v['x'], v['y'], v['z']
                    if 0 <= x < 16 and 0 <= y < 16 and 0 <= z < 16:
                        valid_voxels.append({
                            'x': int(x),
                            'y': int(y),
                            'z': int(z),
                            'block_id': int(v['block_id']),
                            'meta_data': int(v.get('meta_data', 0))
                        })
            
            if len(valid_voxels) < 20:
                raise ValueError(f"有效方块太少: {len(valid_voxels)}")
            
            return valid_voxels
            
        except json.JSONDecodeError as e:
            print(f"  ⚠️  尝试 {attempt+1}/{retry_count}: JSON解析失败")
            if attempt == retry_count - 1:
                print(f"  响应内容: {content[:200]}...")
                raise
            time.sleep(2)
            
        except Exception as e:
            print(f"  ⚠️  尝试 {attempt+1}/{retry_count}: {str(e)}")
            if attempt == retry_count - 1:
                raise
            time.sleep(2)
    
    raise Exception(f"生成{structure_type}失败，已重试{retry_count}次")


def save_sample(voxels, structure_name, output_dir, sample_idx):
    """保存样本为NPZ和JSON格式"""
    sample_dir = output_dir / f"sample_{sample_idx:04d}"
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建16x16x16x2的数组
    voxel_array = np.zeros((16, 16, 16, 2), dtype=np.int16)
    
    for v in voxels:
        x, y, z = v['x'], v['y'], v['z']
        voxel_array[x, y, z, 0] = v['block_id']
        voxel_array[x, y, z, 1] = v.get('meta_data', 0)
    
    # 保存NPZ
    np.savez_compressed(
        sample_dir / "voxels.npz",
        voxels=voxel_array,
        prompt=structure_name
    )
    
    # 保存JSON元数据
    metadata = {
        "structure_name": structure_name,
        "description": f"Generated {structure_name} structure",
        "size": [16, 16, 16],
        "num_blocks": len(voxels),
        "generator": "GLM-4.6"
    }
    
    with open(sample_dir / "data.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return sample_dir


def generate_dataset(args):
    """生成数据集"""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("🚀 使用GLM-4.6生成Minecraft建筑数据集")
    print("=" * 70)
    print(f"📦 目标数量: {args.num_samples}")
    print(f"💾 输出目录: {output_dir}")
    print(f"🤖 模型: GLM-4.6 (ModelScope)")
    print("=" * 70)
    
    # 创建客户端
    client = create_glm4_client()
    
    # 建筑类型列表（丰富多样）
    structure_types = [
        "小木屋", "石塔", "玻璃房子", "金字塔", "喷泉",
        "树木", "桥梁", "城墙", "雕像", "灯塔",
        "花园", "井", "祭坛", "拱门", "平台",
        "楼梯", "栅栏", "小教堂", "市场摊位", "路灯",
        "石柱", "露台", "凉亭", "纪念碑", "哨塔",
        "瀑布", "熔岩池", "冰雕", "仙人掌园", "蘑菇屋"
    ]
    
    # 生成样本
    success_count = 0
    fail_count = 0
    
    pbar = tqdm(total=args.num_samples, desc="生成进度")
    
    while success_count < args.num_samples:
        # 选择结构类型
        structure_type = structure_types[success_count % len(structure_types)]
        
        try:
            # 生成结构
            voxels = generate_minecraft_structure_glm4(client, structure_type)
            
            # 保存样本
            sample_dir = save_sample(voxels, structure_type, output_dir, success_count)
            
            success_count += 1
            pbar.update(1)
            pbar.set_postfix({
                'type': structure_type,
                'blocks': len(voxels),
                'success': success_count,
                'fail': fail_count
            })
            
        except Exception as e:
            fail_count += 1
            print(f"\n❌ 失败: {structure_type} - {str(e)}")
            
            if fail_count > 10:
                print(f"\n⚠️  连续失败{fail_count}次，稍等30秒后继续...")
                time.sleep(30)
                fail_count = 0
            else:
                time.sleep(3)
    
    pbar.close()
    
    print("\n" + "=" * 70)
    print("✅ 数据集生成完成！")
    print(f"   成功: {success_count} 个样本")
    print(f"   输出: {output_dir}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="使用GLM-4.6生成Minecraft数据集")
    
    parser.add_argument('--num-samples', type=int, default=100,
                        help='生成样本数量')
    parser.add_argument('--output-dir', type=str, required=True,
                        help='输出目录')
    
    args = parser.parse_args()
    
    generate_dataset(args)


if __name__ == "__main__":
    main()
