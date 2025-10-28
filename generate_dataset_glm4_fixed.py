#!/usr/bin/env python3
"""
使用GLM-4.6生成Minecraft建筑数据集（修复版）
- 更强的JSON解析容错
- 自动修复截断的JSON
- 降低max_tokens避免截断
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

import numpy as np
from openai import OpenAI
from tqdm import tqdm


# Minecraft方块ID字典
BLOCK_IDS = {
    "stone": 1, "grass": 2, "dirt": 3, "cobblestone": 4, "planks": 5,
    "log": 17, "leaves": 18, "glass": 20, "sandstone": 24, "wool": 35,
    "gold_block": 41, "iron_block": 42, "brick_block": 45, "obsidian": 49,
    "torch": 50, "diamond_block": 57, "snow": 78, "ice": 79, "cactus": 81,
    "fence": 85, "glowstone": 89, "stone_brick": 98, "quartz_block": 155
}


def create_glm4_client():
    """创建GLM-4.6客户端"""
    return OpenAI(
        base_url='https://api-inference.modelscope.cn/v1',
        api_key='ms-35a044f4-7e2c-4df3-8d97-c8ac7052cca8',
    )


def fix_truncated_json(content: str) -> str:
    """修复截断的JSON"""
    # 移除markdown标记
    content = content.strip()
    if content.startswith('```json'):
        content = content[7:]
    if content.startswith('```'):
        content = content[3:]
    if content.endswith('```'):
        content = content[:-3]
    content = content.strip()
    
    # 如果JSON被截断，尝试修复
    if not content.endswith(']'):
        # 找到最后一个完整的对象
        last_complete = content.rfind('}')
        if last_complete > 0:
            content = content[:last_complete+1] + '\n]'
    
    return content


def generate_minecraft_structure_glm4(client, structure_type: str, retry_count: int = 3):
    """使用GLM-4.6生成Minecraft建筑结构"""
    
    block_ids_str = ", ".join([f"{name}={id}" for name, id in list(BLOCK_IDS.items())[:15]])
    
    # 简化提示词，要求更少的方块
    prompt = f"""生成一个{structure_type}的Minecraft 3D建筑。

要求：
- 空间：16x16x16（坐标0-15）
- 方块数：40-120个（不要太多）
- 使用真实方块ID：{block_ids_str}

返回JSON数组，每个方块：
{{"x": 坐标, "y": 坐标, "z": 坐标, "block_id": 方块ID, "meta_data": 0}}

只返回JSON数组，不要解释。示例：
[
  {{"x": 5, "y": 0, "z": 5, "block_id": 1, "meta_data": 0}},
  {{"x": 6, "y": 0, "z": 5, "block_id": 1, "meta_data": 0}}
]"""

    for attempt in range(retry_count):
        try:
            response = client.chat.completions.create(
                model='ZhipuAI/GLM-4.6',
                messages=[
                    {
                        'role': 'system',
                        'content': '你是Minecraft建筑专家，只返回JSON数组，不添加任何解释。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,  # 降低以避免截断
            )
            
            content = response.choices[0].message.content
            
            # 修复JSON
            content = fix_truncated_json(content)
            
            # 解析JSON
            try:
                voxels = json.loads(content)
            except json.JSONDecodeError as e:
                # 尝试提取JSON数组
                match = re.search(r'\[\s*\{.*?\}\s*\]', content, re.DOTALL)
                if match:
                    voxels = json.loads(match.group())
                else:
                    raise e
            
            # 验证数据
            if not isinstance(voxels, list) or len(voxels) < 10:
                raise ValueError(f"方块太少: {len(voxels) if isinstance(voxels, list) else 0}")
            
            # 验证并清理方块
            valid_voxels = []
            for v in voxels:
                if isinstance(v, dict) and all(k in v for k in ['x', 'y', 'z', 'block_id']):
                    x, y, z = int(v['x']), int(v['y']), int(v['z'])
                    if 0 <= x < 16 and 0 <= y < 16 and 0 <= z < 16:
                        block_id = int(v['block_id'])
                        if 1 <= block_id <= 255:  # 有效的方块ID
                            valid_voxels.append({
                                'x': x,
                                'y': y,
                                'z': z,
                                'block_id': block_id,
                                'meta_data': int(v.get('meta_data', 0))
                            })
            
            if len(valid_voxels) < 20:
                raise ValueError(f"有效方块太少: {len(valid_voxels)}")
            
            # 限制方块数量（避免太多）
            if len(valid_voxels) > 150:
                valid_voxels = valid_voxels[:150]
            
            return valid_voxels
            
        except Exception as e:
            print(f"  ⚠️  尝试 {attempt+1}/{retry_count}: {str(e)[:100]}")
            if attempt == retry_count - 1:
                raise
            time.sleep(3)
    
    raise Exception(f"生成{structure_type}失败")


def save_sample(voxels, structure_name, output_dir, sample_idx):
    """保存样本"""
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
        "generator": "GLM-4.6-Fixed"
    }
    
    with open(sample_dir / "data.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return sample_dir


def generate_dataset(args):
    """生成数据集"""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("🚀 使用GLM-4.6生成Minecraft建筑数据集（修复版）")
    print("=" * 70)
    print(f"📦 目标数量: {args.num_samples}")
    print(f"💾 输出目录: {output_dir}")
    print(f"🤖 模型: GLM-4.6 (ModelScope)")
    print("=" * 70)
    
    # 创建客户端
    client = create_glm4_client()
    
    # 建筑类型列表（简化版）
    structure_types = [
        "木屋", "石塔", "桥", "井", "塔",
        "树", "墙", "门", "亭", "台",
        "柱", "坛", "路", "灯", "栏"
    ] * 10  # 重复以达到足够数量
    
    # 生成样本
    success_count = 0
    fail_count = 0
    consecutive_fails = 0
    
    pbar = tqdm(total=args.num_samples, desc="生成进度")
    
    while success_count < args.num_samples:
        structure_type = structure_types[success_count % len(structure_types)]
        
        try:
            voxels = generate_minecraft_structure_glm4(client, structure_type)
            sample_dir = save_sample(voxels, structure_type, output_dir, success_count)
            
            success_count += 1
            consecutive_fails = 0
            pbar.update(1)
            pbar.set_postfix({
                'type': structure_type,
                'blocks': len(voxels),
                'fail': fail_count
            })
            
        except Exception as e:
            fail_count += 1
            consecutive_fails += 1
            print(f"\n❌ 失败 {fail_count}: {structure_type} - {str(e)[:80]}")
            
            if consecutive_fails >= 5:
                print(f"\n⚠️  连续失败{consecutive_fails}次，等待60秒...")
                time.sleep(60)
                consecutive_fails = 0
            else:
                time.sleep(5)
    
    pbar.close()
    
    print("\n" + "=" * 70)
    print("✅ 数据集生成完成！")
    print(f"   成功: {success_count} 个样本")
    print(f"   失败: {fail_count} 次")
    print(f"   输出: {output_dir}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="使用GLM-4.6生成Minecraft数据集（修复版）")
    parser.add_argument('--num-samples', type=int, default=100, help='生成样本数量')
    parser.add_argument('--output-dir', type=str, required=True, help='输出目录')
    args = parser.parse_args()
    generate_dataset(args)


if __name__ == "__main__":
    main()
