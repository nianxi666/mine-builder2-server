#!/usr/bin/env python3
"""
简化版Minecraft Schematic数据集生成器
使用Gemini生成JSON格式的建筑数据
"""

import os
import json
import time
import random
import argparse
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai
from tqdm import tqdm

# 方块ID简化列表（最常用的方块）
COMMON_BLOCKS = {
    1: "stone", 2: "grass", 3: "dirt", 4: "cobblestone", 5: "oak_planks",
    12: "sand", 17: "oak_log", 18: "oak_leaves", 20: "glass", 24: "sandstone",
    35: "wool", 41: "gold_block", 42: "iron_block", 45: "bricks", 48: "mossy_cobblestone",
    49: "obsidian", 57: "diamond_block", 79: "ice", 80: "snow", 82: "clay",
    98: "stone_bricks", 155: "quartz_block", 251: "concrete"
}

# 建筑类型提示词
BUILDING_PROMPTS = [
    "A simple 8x8x8 wooden house with a roof",
    "A stone tower 6x6x12 blocks tall",
    "A small cottage made of bricks and wood",
    "A modern glass building",
    "A medieval castle wall segment",
    "A simple tree with leaves",
    "A fountain structure",
    "A small pyramid made of sandstone",
    "An archway entrance",
    "A lighthouse tower",
    "A windmill structure",
    "A bridge segment",
    "A small farm shed",
    "A guard tower",
    "An igloo made of snow and ice",
    "A nether portal frame",
    "A simple statue",
    "A market stall",
    "A well with stone walls",
    "A beacon structure",
]


class SimpleMinecraftGenerator:
    """简化的Minecraft建筑生成器"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.blocks_info = "\n".join([f"ID {bid}: {name}" for bid, name in COMMON_BLOCKS.items()])
    
    def generate_structure(self, prompt: str, max_retries: int = 3) -> Dict:
        """生成单个建筑结构"""
        
        system_prompt = f"""You are a Minecraft builder AI. Generate a 16x16x16 voxel structure.

AVAILABLE BLOCKS:
{self.blocks_info}

OUTPUT FORMAT (JSON only, no explanations):
{{
  "voxels": [
    {{"x": 0, "y": 0, "z": 0, "block_id": 1, "meta_data": 0}},
    ...
  ]
}}

RULES:
- Coordinates must be 0-15 for x, y, z
- Use block_id from the list above
- meta_data is usually 0
- Create interesting 3D structures
- Output ONLY valid JSON, no markdown or explanations

Prompt: {prompt}

Generate the JSON now:"""

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(system_prompt)
                text = response.text.strip()
                
                # 清理markdown代码块
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                
                # 解析JSON
                data = json.loads(text)
                
                if 'voxels' in data and len(data['voxels']) > 0:
                    # 验证并清理数据
                    valid_voxels = []
                    for v in data['voxels']:
                        x, y, z = int(v.get('x', 0)), int(v.get('y', 0)), int(v.get('z', 0))
                        block_id = int(v.get('block_id', 1))
                        meta_data = int(v.get('meta_data', 0))
                        
                        if 0 <= x < 16 and 0 <= y < 16 and 0 <= z < 16:
                            valid_voxels.append({
                                'x': x, 'y': y, 'z': z,
                                'block_id': block_id,
                                'meta_data': meta_data
                            })
                    
                    if len(valid_voxels) > 0:
                        return {
                            'prompt': prompt,
                            'structure_name': prompt,
                            'voxels': valid_voxels
                        }
                
                time.sleep(1)
                
            except json.JSONDecodeError as e:
                print(f"  JSON parse error on attempt {attempt + 1}, retrying...")
                time.sleep(1)
            except Exception as e:
                print(f"  Error on attempt {attempt + 1}: {e}")
                if "429" in str(e) or "quota" in str(e).lower():
                    wait_time = (attempt + 1) * 10
                    print(f"  Rate limit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    time.sleep(2)
        
        # 备用：生成简单结构
        print(f"  Using fallback structure for: {prompt}")
        return self._create_fallback(prompt)
    
    def _create_fallback(self, prompt: str) -> Dict:
        """创建备用结构（简单立方体）"""
        voxels = []
        # 4x4x4立方体
        for x in range(4, 8):
            for y in range(0, 4):
                for z in range(4, 8):
                    # 只在边界放置方块
                    if x in [4, 7] or y in [0, 3] or z in [4, 7]:
                        voxels.append({
                            'x': x, 'y': y, 'z': z,
                            'block_id': random.choice([1, 4, 5, 45]),
                            'meta_data': 0
                        })
        
        return {
            'prompt': prompt,
            'structure_name': 'fallback_cube',
            'voxels': voxels
        }
    
    def save_sample(self, data: Dict, output_dir: Path, index: int):
        """保存样本"""
        sample_dir = output_dir / f"sample_{index:04d}"
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON格式
        with open(sample_dir / "data.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        # NPZ格式
        voxel_array = np.zeros((16, 16, 16, 2), dtype=np.int16)
        for v in data['voxels']:
            voxel_array[v['x'], v['y'], v['z'], 0] = v['block_id']
            voxel_array[v['x'], v['y'], v['z'], 1] = v['meta_data']
        
        np.savez_compressed(
            sample_dir / "voxels.npz",
            voxels=voxel_array,
            prompt=data['prompt']
        )
    
    def generate_dataset(self, output_dir: str, num_samples: int = 1000):
        """生成数据集"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Generating {num_samples} samples to {output_dir}")
        print("=" * 60)
        
        successful = 0
        
        for i in tqdm(range(num_samples), desc="Generating"):
            # 选择提示词
            if i < len(BUILDING_PROMPTS) * 10:
                base_prompt = BUILDING_PROMPTS[i % len(BUILDING_PROMPTS)]
                variations = ["", " with details", " compact", " tall", " wide"]
                prompt = base_prompt + random.choice(variations)
            else:
                # 随机组合
                styles = ["simple", "complex", "modern", "medieval", "fantasy"]
                materials = ["stone", "wood", "brick", "glass", "mixed"]
                structures = ["house", "tower", "statue", "wall", "decoration"]
                prompt = f"A {random.choice(styles)} {random.choice(materials)} {random.choice(structures)}"
            
            try:
                data = self.generate_structure(prompt)
                self.save_sample(data, output_path, i)
                successful += 1
                time.sleep(0.5)  # 避免限流
            except Exception as e:
                print(f"\nFailed sample {i}: {e}")
                time.sleep(2)
        
        # 保存元数据
        metadata = {
            'total_samples': successful,
            'failed_samples': num_samples - successful,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(output_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("\n" + "=" * 60)
        print(f"Dataset complete: {successful}/{num_samples} samples")
        print(f"Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-key', default='AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A')
    parser.add_argument('--output-dir', default='dataset')
    parser.add_argument('--num-samples', type=int, default=1000)
    parser.add_argument('--model', default='gemini-2.0-flash-exp')
    args = parser.parse_args()
    
    generator = SimpleMinecraftGenerator(args.api_key, args.model)
    generator.generate_dataset(args.output_dir, args.num_samples)


if __name__ == "__main__":
    main()
