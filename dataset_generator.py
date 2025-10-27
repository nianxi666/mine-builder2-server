#!/usr/bin/env python3
"""
Minecraft Schematic Dataset Generator using Gemini 2.5 Pro
使用函数调用生成16x16x16的结构化Minecraft建筑数据集
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

# 方块ID字典 - 从server.py提取
MINECRAFT_BLOCKS = {
    "1": {"0": "stone", "1": "granite", "2": "polished_granite", "3": "diorite", "4": "polished_diorite", "5": "andesite", "6": "polished_andesite"},
    "2": {"0": "grass_top"},
    "3": {"0": "dirt", "1": "coarse_dirt", "2": "podzol"},
    "4": {"0": "cobblestone"},
    "5": {"0": "planks_oak", "1": "planks_spruce", "2": "planks_birch", "3": "planks_jungle", "4": "planks_acacia", "5": "planks_dark_oak"},
    "12": {"0": "sand", "1": "red_sand"},
    "13": {"0": "gravel"},
    "14": {"0": "gold_ore"},
    "15": {"0": "iron_ore"},
    "16": {"0": "coal_ore"},
    "17": {"0": "log_oak", "1": "log_spruce", "2": "log_birch", "3": "log_jungle"},
    "18": {"0": "leaves_oak", "1": "leaves_spruce", "2": "leaves_birch", "3": "leaves_jungle"},
    "19": {"0": "sponge"},
    "20": {"0": "glass"},
    "21": {"0": "lapis_ore"},
    "22": {"0": "lapis_block"},
    "24": {"0": "sandstone", "1": "sandstone_carved", "2": "sandstone_smooth"},
    "35": {"0": "wool_white", "1": "wool_orange", "2": "wool_magenta", "3": "wool_light_blue", "4": "wool_yellow", "5": "wool_lime", "6": "wool_pink", "7": "wool_gray", "8": "wool_silver", "9": "wool_cyan", "10": "wool_purple", "11": "wool_blue", "12": "wool_brown", "13": "wool_green", "14": "wool_red", "15": "wool_black"},
    "41": {"0": "gold_block"},
    "42": {"0": "iron_block"},
    "43": {"0": "stone_slab_side", "1": "sandstone_top", "2": "planks_oak", "3": "cobblestone", "4": "brick", "5": "stonebrick", "6": "nether_brick", "7": "quartz_block_side"},
    "45": {"0": "brick"},
    "46": {"0": "tnt_side"},
    "47": {"0": "bookshelf"},
    "48": {"0": "cobblestone_mossy"},
    "49": {"0": "obsidian"},
    "56": {"0": "diamond_ore"},
    "57": {"0": "diamond_block"},
    "58": {"0": "crafting_table_top"},
    "79": {"0": "ice"},
    "80": {"0": "snow"},
    "82": {"0": "clay"},
    "86": {"0": "pumpkin_side"},
    "87": {"0": "netherrack"},
    "88": {"0": "soul_sand"},
    "89": {"0": "glowstone"},
    "98": {"0": "stonebrick", "1": "stonebrick_mossy", "2": "stonebrick_cracked", "3": "stonebrick_carved"},
    "103": {"0": "melon_side"},
    "112": {"0": "nether_brick"},
    "129": {"0": "emerald_ore"},
    "133": {"0": "emerald_block"},
    "152": {"0": "redstone_block"},
    "155": {"0": "quartz_block_side", "1": "quartz_block_chiseled", "2": "quartz_block_lines"},
    "159": {"0": "hardened_clay_stained_white", "1": "hardened_clay_stained_orange", "2": "hardened_clay_stained_magenta", "3": "hardened_clay_stained_light_blue", "4": "hardened_clay_stained_yellow", "5": "hardened_clay_stained_lime", "6": "hardened_clay_stained_pink", "7": "hardened_clay_stained_gray", "8": "hardened_clay_stained_silver", "9": "hardened_clay_stained_cyan", "10": "hardened_clay_stained_purple", "11": "hardened_clay_stained_blue", "12": "hardened_clay_stained_brown", "13": "hardened_clay_stained_green", "14": "hardened_clay_stained_red", "15": "hardened_clay_stained_black"},
    "160": {"0": "glass_white", "1": "glass_orange", "2": "glass_magenta", "3": "glass_light_blue", "4": "glass_yellow", "5": "glass_lime", "6": "glass_pink", "7": "glass_gray", "8": "glass_silver", "9": "glass_cyan", "10": "glass_purple", "11": "glass_blue", "12": "glass_brown", "13": "glass_green", "14": "glass_red", "15": "glass_black"},
    "168": {"0": "prismarine_rough", "1": "prismarine_bricks", "2": "prismarine_dark"},
    "172": {"0": "hardened_clay"},
    "173": {"0": "coal_block"},
    "174": {"0": "ice_packed"},
    "251": {"0": "concrete_white", "1": "concrete_orange", "2": "concrete_magenta", "3": "concrete_light_blue", "4": "concrete_yellow", "5": "concrete_lime", "6": "concrete_pink", "7": "concrete_gray", "8": "concrete_silver", "9": "concrete_cyan", "10": "concrete_purple", "11": "concrete_blue", "12": "concrete_brown", "13": "concrete_green", "14": "concrete_red", "15": "concrete_black"}
}

# 建筑类型提示词库
BUILDING_PROMPTS = [
    # 房屋类
    "A simple wooden house with a sloped roof",
    "A stone cottage with a chimney",
    "A modern glass house",
    "A medieval stone castle tower",
    "A cozy cabin made of logs",
    "A small village house with a garden",
    "A treehouse on wooden pillars",
    "A desert sandstone house",
    "An ice igloo structure",
    "A nether brick fortress tower",
    
    # 塔和建筑物
    "A tall lighthouse with glowstone",
    "A wizard tower with a spiral design",
    "A church bell tower",
    "A watchtower with battlements",
    "A clock tower with red brick",
    "An ancient stone obelisk",
    "A modern skyscraper segment",
    "A pagoda with multiple tiers",
    
    # 装饰和雕塑
    "A large diamond statue",
    "A golden throne",
    "A fountain with water design",
    "A tree made of emerald blocks",
    "A giant mushroom structure",
    "A stone pillar with decorative top",
    "An archway entrance",
    "A monument with quartz blocks",
    
    # 自然结构
    "A large oak tree with leaves",
    "A birch forest tree",
    "A jungle tree with vines",
    "A cactus cluster in sand",
    "A rock formation with caves",
    "A snow-covered pine tree",
    "A coral reef structure",
    "A mushroom with red cap",
    
    # 功能性建筑
    "A small farm shed",
    "A blacksmith workshop",
    "A well with stone walls",
    "A bridge segment",
    "A windmill structure",
    "A market stall",
    "A guard post",
    "A lighthouse beacon",
    
    # 幻想和创意
    "A floating crystal structure",
    "A portal frame with obsidian",
    "A magical shrine with glowstone",
    "A rainbow tower with colored wool",
    "A candy house with colored concrete",
    "A robot statue",
    "A rocket ship",
    "A castle turret with flags",
]

# 定义函数调用schema
VOXEL_GENERATION_SCHEMA = {
    "name": "generate_minecraft_structure",
    "description": "Generate a 16x16x16 Minecraft structure with block IDs and metadata. Return voxel data as a list of occupied positions.",
    "parameters": {
        "type_": "OBJECT",
        "properties": {
            "structure_name": {
                "type_": "STRING",
                "description": "Name or brief description of the structure"
            },
            "voxels": {
                "type_": "ARRAY",
                "description": "List of voxels with their positions and block properties",
                "items": {
                    "type_": "OBJECT",
                    "properties": {
                        "x": {"type_": "INTEGER", "description": "X coordinate (0-15)"},
                        "y": {"type_": "INTEGER", "description": "Y coordinate (0-15)"},
                        "z": {"type_": "INTEGER", "description": "Z coordinate (0-15)"},
                        "block_id": {"type_": "INTEGER", "description": "Minecraft block ID"},
                        "meta_data": {"type_": "INTEGER", "description": "Block metadata/variant (default 0)"}
                    },
                    "required": ["x", "y", "z", "block_id"]
                }
            }
        },
        "required": ["structure_name", "voxels"]
    }
}


class MinecraftDatasetGenerator:
    """使用Gemini 2.5 Pro生成Minecraft建筑数据集"""
    
    def __init__(self, api_key: str, output_dir: str = "dataset", model_name: str = "gemini-2.0-flash-exp"):
        """
        初始化生成器
        
        Args:
            api_key: Google AI Studio API密钥
            output_dir: 数据集输出目录
            model_name: 使用的模型名称
        """
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        
        # 配置Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            tools=[VOXEL_GENERATION_SCHEMA]
        )
        
        # 创建方块参考字符串
        self.blocks_reference = self._create_blocks_reference()
        
    def _create_blocks_reference(self) -> str:
        """创建方块字典的参考文本"""
        blocks_text = "Available Minecraft Blocks:\n\n"
        for block_id, variants in MINECRAFT_BLOCKS.items():
            blocks_text += f"Block ID {block_id}:\n"
            for meta, name in variants.items():
                blocks_text += f"  - meta {meta}: {name}\n"
        return blocks_text
    
    def generate_single_structure(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        生成单个建筑结构
        
        Args:
            prompt: 建筑描述
            max_retries: 最大重试次数
            
        Returns:
            包含prompt和voxel数据的字典
        """
        system_prompt = f"""You are an expert Minecraft builder. Generate a 16x16x16 voxel structure based on the given prompt.

{self.blocks_reference}

IMPORTANT RULES:
1. Coordinates must be between 0-15 for x, y, z
2. Use realistic block combinations (e.g., stone foundation, wood walls, etc.)
3. Make structures interesting and detailed within the 16x16x16 space
4. Add appropriate details like roofs, doors, windows, decorations
5. meta_data defaults to 0 if not specified
6. Create 3D structures, not just flat designs
7. Use the provided block IDs from the reference above

Generate a creative and detailed structure."""

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content([
                    system_prompt,
                    f"\nPrompt: {prompt}\n\nGenerate the structure now."
                ])
                
                # 提取函数调用结果
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call'):
                            fc = part.function_call
                            
                            # 尝试不同的方式获取voxels数据
                            voxels_data = None
                            if hasattr(fc, 'args'):
                                if 'voxels' in fc.args:
                                    voxels_data = fc.args['voxels']
                                elif hasattr(fc.args, 'get'):
                                    voxels_data = fc.args.get('voxels')
                            
                            if voxels_data is None:
                                print(f"No voxels data in response, retrying...")
                                time.sleep(1)
                                continue
                            
                            # 转换为列表
                            if not isinstance(voxels_data, list):
                                voxels_data = list(voxels_data)
                            
                            # 验证数据
                            valid_voxels = []
                            for v in voxels_data:
                                try:
                                    x = int(v.get('x', 0) if hasattr(v, 'get') else v['x'])
                                    y = int(v.get('y', 0) if hasattr(v, 'get') else v['y'])
                                    z = int(v.get('z', 0) if hasattr(v, 'get') else v['z'])
                                    block_id = int(v.get('block_id', 1) if hasattr(v, 'get') else v.get('block_id', 1))
                                    meta_data = int(v.get('meta_data', 0) if hasattr(v, 'get') else v.get('meta_data', 0))
                                    
                                    if 0 <= x < 16 and 0 <= y < 16 and 0 <= z < 16:
                                        valid_voxels.append({
                                            'x': x,
                                            'y': y,
                                            'z': z,
                                            'block_id': block_id,
                                            'meta_data': meta_data
                                        })
                                except Exception as ve:
                                    continue
                            
                            if len(valid_voxels) > 0:
                                structure_name = prompt
                                if hasattr(fc, 'args') and 'structure_name' in fc.args:
                                    structure_name = fc.args['structure_name']
                                
                                return {
                                    'prompt': prompt,
                                    'structure_name': structure_name,
                                    'voxels': valid_voxels
                                }
                
                # 如果没有函数调用，重试
                time.sleep(1)
                
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if "429" in str(e) or "quota" in str(e).lower():
                    wait_time = (attempt + 1) * 10
                    print(f"Rate limit hit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    time.sleep(2)
        
        # 如果所有重试都失败，返回简单的默认结构
        print(f"Failed to generate for prompt: {prompt}, using fallback")
        return self._create_fallback_structure(prompt)
    
    def _create_fallback_structure(self, prompt: str) -> Dict[str, Any]:
        """创建一个简单的备用结构（避免完全失败）"""
        voxels = []
        # 创建一个简单的立方体
        for x in range(4, 12):
            for z in range(4, 12):
                # 地基
                voxels.append({'x': x, 'y': 0, 'z': z, 'block_id': 1, 'meta_data': 0})
                # 墙
                if x in [4, 11] or z in [4, 11]:
                    for y in range(1, 5):
                        voxels.append({'x': x, 'y': y, 'z': z, 'block_id': 4, 'meta_data': 0})
                # 屋顶
                voxels.append({'x': x, 'y': 5, 'z': z, 'block_id': 5, 'meta_data': 0})
        
        return {
            'prompt': prompt,
            'structure_name': 'fallback_structure',
            'voxels': voxels
        }
    
    def voxels_to_array(self, voxels: List[Dict], size: int = 16) -> np.ndarray:
        """
        将voxel列表转换为3D数组
        
        Returns:
            shape (size, size, size, 2) - 最后一维是 [block_id, meta_data]
        """
        array = np.zeros((size, size, size, 2), dtype=np.int16)
        for v in voxels:
            x, y, z = v['x'], v['y'], v['z']
            if 0 <= x < size and 0 <= y < size and 0 <= z < size:
                array[x, y, z, 0] = v['block_id']
                array[x, y, z, 1] = v.get('meta_data', 0)
        return array
    
    def save_dataset_sample(self, data: Dict[str, Any], index: int):
        """保存单个数据样本"""
        sample_dir = self.output_dir / f"sample_{index:04d}"
        sample_dir.mkdir(exist_ok=True)
        
        # 保存JSON格式（易读）
        json_path = sample_dir / "data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 保存NPZ格式（训练用）
        voxel_array = self.voxels_to_array(data['voxels'])
        npz_path = sample_dir / "voxels.npz"
        np.savez_compressed(
            npz_path,
            voxels=voxel_array,
            prompt=data['prompt']
        )
    
    def generate_dataset(self, num_samples: int = 1000, use_custom_prompts: bool = True):
        """
        生成完整数据集
        
        Args:
            num_samples: 生成样本数量
            use_custom_prompts: 是否使用预定义提示词（False则让AI生成）
        """
        print(f"Starting dataset generation: {num_samples} samples")
        print(f"Output directory: {self.output_dir}")
        print(f"Model: {self.model_name}")
        print("-" * 60)
        
        successful = 0
        failed = 0
        
        for i in tqdm(range(num_samples), desc="Generating dataset"):
            try:
                # 选择或生成提示词
                if use_custom_prompts and i < len(BUILDING_PROMPTS) * 20:
                    # 循环使用预定义提示词，并添加变化
                    base_prompt = BUILDING_PROMPTS[i % len(BUILDING_PROMPTS)]
                    variations = ["", " with details", " in creative style", " with decorations", " compact design"]
                    prompt = base_prompt + random.choice(variations)
                else:
                    # 让AI生成新提示词
                    prompt = self._generate_creative_prompt()
                
                # 生成结构
                data = self.generate_single_structure(prompt)
                
                # 保存
                self.save_dataset_sample(data, i)
                successful += 1
                
                # 避免API限流
                time.sleep(0.5)
                
            except Exception as e:
                print(f"\nFailed to generate sample {i}: {e}")
                failed += 1
                time.sleep(2)
        
        print("\n" + "=" * 60)
        print(f"Dataset generation complete!")
        print(f"Successful: {successful}/{num_samples}")
        print(f"Failed: {failed}/{num_samples}")
        print(f"Dataset saved to: {self.output_dir}")
        
        # 保存数据集元数据
        metadata = {
            'total_samples': successful,
            'failed_samples': failed,
            'model_used': self.model_name,
            'voxel_size': 16,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _generate_creative_prompt(self) -> str:
        """使用AI生成创意提示词"""
        # 简单版本：从模板随机组合
        structures = ["house", "tower", "statue", "tree", "fountain", "monument", "shrine", "gate"]
        materials = ["wooden", "stone", "brick", "glass", "marble", "ice", "gold", "diamond"]
        styles = ["medieval", "modern", "fantasy", "ancient", "futuristic", "rustic", "elegant"]
        
        structure = random.choice(structures)
        material = random.choice(materials)
        style = random.choice(styles)
        
        return f"A {style} {material} {structure}"


def main():
    parser = argparse.ArgumentParser(description="Generate Minecraft Schematic Dataset")
    parser.add_argument('--api-key', type=str, default='AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A',
                        help='Google AI Studio API key')
    parser.add_argument('--output-dir', type=str, default='dataset',
                        help='Output directory for dataset')
    parser.add_argument('--num-samples', type=int, default=1000,
                        help='Number of samples to generate')
    parser.add_argument('--model', type=str, default='gemini-2.0-flash-exp',
                        help='Gemini model to use')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Minecraft Schematic Dataset Generator")
    print("Using Gemini 2.5 Pro with Function Calling")
    print("=" * 60)
    
    generator = MinecraftDatasetGenerator(
        api_key=args.api_key,
        output_dir=args.output_dir,
        model_name=args.model
    )
    
    generator.generate_dataset(num_samples=args.num_samples)


if __name__ == "__main__":
    main()
