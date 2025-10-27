#!/usr/bin/env python3
"""
使用Gemini 2.5 Pro生成高质量Minecraft建筑数据集
基于验证的优质提示词
"""

import json
import re
import time
import random
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm
import google.generativeai as genai

# 方块字典
BLOCK_GUIDE = """
常用Minecraft方块ID参考：
- 1: stone (石头)
- 2: grass_block (草方块)  
- 3: dirt (泥土)
- 4: cobblestone (圆石)
- 5: oak_planks (橡木板)
- 17: oak_log (橡木原木)
- 18: oak_leaves (橡木树叶)
- 20: glass (玻璃)
- 24: sandstone (砂岩)
- 35: wool (羊毛，meta 0-15不同颜色)
- 41: gold_block (金块)
- 42: iron_block (铁块)
- 45: bricks (红砖)
- 48: mossy_cobblestone (苔石)
- 49: obsidian (黑曜石)
- 57: diamond_block (钻石块)
- 79: ice (冰)
- 80: snow_block (雪块)
- 89: glowstone (荧石，发光)
- 98: stone_bricks (石砖)
- 155: quartz_block (石英块，白色)
- 159: stained_clay (染色粘土)
- 251: concrete (混凝土)
"""

# 高质量提示词模板
PREMIUM_PROMPT = """你是世界顶级Minecraft建筑大师，擅长创造精美的体素艺术作品。

{block_guide}

建筑类型：{building_type}

设计要求：
1. **专业级设计**：像真正的Minecraft玩家建造的作品
2. **结构完整**：
   - 稳固的地基（y=0层）
   - 清晰的墙体和支撑结构
   - 精美的屋顶或顶部设计
3. **细节丰富**：窗户、门、装饰、纹理变化
4. **材质搭配**：至少使用3种不同材质，颜色协调
5. **空间利用**：建筑占据合适的空间，有内部结构
6. **美学价值**：整体美观，有艺术感

技术规格：
- 坐标范围：x, y, z 都在 0-15
- 方块数量：100-400个（既有细节又不过度密集）
- 只使用上面列出的方块ID
- meta_data默认为0（除非需要特定颜色）

输出格式（纯JSON，绝对不要注释，不要//，不要任何解释）：
{{
  "structure_name": "建筑名称",
  "description": "20字内的描述",
  "voxels": [
    {{"x": 0, "y": 0, "z": 0, "block_id": 1, "meta_data": 0}}
  ]
}}

关键：输出纯净的JSON，不要添加任何注释符号（//）或markdown标记！

开始生成："""

# 丰富的建筑类型库
BUILDING_TYPES = [
    # 塔类
    "一座雄伟的中世纪石塔，多层窗户，顶部有旗帜",
    "一座魔法师塔，螺旋设计，荧石照明",
    "一座灯塔，红白相间，顶部发光",
    "一座钟楼，开放式设计，可见钟摆",
    "一座守望塔，防御工事，射击孔",
    
    # 房屋类
    "一个现代化玻璃别墅，简约风格",
    "一座中世纪木屋，斜屋顶，烟囱",
    "一个沙漠风格的砂岩房屋",
    "一座冰雪主题的冰屋",
    "一个地下掩体，部分露出地面",
    
    # 自然类
    "一棵巨大的橡树，粗壮树干，茂密树冠",
    "一棵白桦树林中的树",
    "一棵丛林大树，藤蔓缠绕",
    "一个蘑菇结构，巨型蘑菇",
    "一座小型山丘，草地和石头",
    
    # 装饰类
    "一个喷泉，中央水柱设计",
    "一座雕像，人形或动物",
    "一个拱门，装饰性入口",
    "一座纪念碑，高耸的柱子",
    "一个花园亭子，开放式",
    
    # 功能性建筑
    "一座小桥，石拱桥设计",
    "一个井，石头围墙",
    "一座风车，木制结构",
    "一个市场摊位，遮阳棚",
    "一座城堡墙段，垛口设计",
    
    # 幻想建筑
    "一个传送门框架，黑曜石材质",
    "一座水晶塔，钻石和玻璃",
    "一个魔法圈，荧石和特殊方块",
    "一座浮空岛，悬浮设计",
    "一个龙巢，山顶结构",
    
    # 现代建筑
    "一座现代摩天楼底部，玻璃幕墙",
    "一个加油站，简约设计",
    "一座现代雕塑，抽象艺术",
    "一个公共座椅区，公园设施",
    "一座现代博物馆入口",
]

def clean_json_comments(text):
    """移除JSON中的注释"""
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = '\n'.join(line for line in text.split('\n') if line.strip())
    return text

class PremiumDatasetGenerator:
    """高质量数据集生成器"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-thinking-exp-1219"):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)
        
    def generate_single(self, building_type: str, max_retries: int = 3) -> dict:
        """生成单个高质量样本"""
        
        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(self.model_name)
                
                prompt = PREMIUM_PROMPT.format(
                    block_guide=BLOCK_GUIDE,
                    building_type=building_type
                )
                
                response = model.generate_content(prompt)
                text = response.text.strip()
                
                # 清理markdown
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                
                # 移除注释
                text = clean_json_comments(text)
                
                # 解析JSON
                data = json.loads(text)
                
                # 验证
                voxels = data.get('voxels', [])
                if len(voxels) < 50:
                    raise ValueError(f"Too few voxels: {len(voxels)}")
                
                # 添加prompt字段
                data['prompt'] = building_type
                
                return data
                
            except json.JSONDecodeError as e:
                print(f"  ⚠ JSON解析失败 (attempt {attempt+1}/{max_retries})")
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠ 生成失败 (attempt {attempt+1}/{max_retries}): {e}")
                if "429" in str(e) or "quota" in str(e).lower():
                    wait_time = (attempt + 1) * 15
                    print(f"  ⏳ Rate limit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    time.sleep(3)
        
        raise Exception(f"Failed after {max_retries} attempts")
    
    def save_sample(self, data: dict, output_dir: Path, index: int):
        """保存样本"""
        sample_dir = output_dir / f"sample_{index:04d}"
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON
        with open(sample_dir / "data.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # NPZ
        voxel_array = np.zeros((16, 16, 16, 2), dtype=np.int16)
        for v in data['voxels']:
            x, y, z = v['x'], v['y'], v['z']
            if 0 <= x < 16 and 0 <= y < 16 and 0 <= z < 16:
                voxel_array[x, y, z, 0] = v.get('block_id', 1)
                voxel_array[x, y, z, 1] = v.get('meta_data', 0)
        
        np.savez_compressed(
            sample_dir / "voxels.npz",
            voxels=voxel_array,
            prompt=data.get('prompt', '')
        )
    
    def generate_dataset(self, output_dir: str, num_samples: int = 1000):
        """生成完整数据集"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("=" * 70)
        print(f"🚀 生成高质量Minecraft建筑数据集")
        print(f"📦 目标数量: {num_samples}")
        print(f"💾 输出目录: {output_dir}")
        print(f"🤖 模型: {self.model_name}")
        print("=" * 70)
        print()
        
        successful = 0
        failed = 0
        
        for i in tqdm(range(num_samples), desc="生成进度"):
            # 选择建筑类型
            if i < len(BUILDING_TYPES) * 3:
                building_type = BUILDING_TYPES[i % len(BUILDING_TYPES)]
            else:
                building_type = random.choice(BUILDING_TYPES)
            
            try:
                data = self.generate_single(building_type)
                self.save_sample(data, output_path, i)
                successful += 1
                
                # 避免限流
                time.sleep(1)
                
            except Exception as e:
                failed += 1
                tqdm.write(f"❌ 样本 {i} 失败: {e}")
                time.sleep(2)
        
        # 保存元数据
        metadata = {
            'total_samples': successful,
            'failed_samples': failed,
            'model': self.model_name,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'quality': 'premium'
        }
        with open(output_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print()
        print("=" * 70)
        print(f"✅ 数据集生成完成！")
        print(f"   成功: {successful}/{num_samples}")
        print(f"   失败: {failed}/{num_samples}")
        print(f"   保存位置: {output_path}")
        print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="生成高质量Minecraft数据集")
    parser.add_argument('--api-key', default='AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A')
    parser.add_argument('--output-dir', default='dataset_premium')
    parser.add_argument('--num-samples', type=int, default=1000)
    parser.add_argument('--model', default='gemini-2.0-flash-thinking-exp-1219')
    args = parser.parse_args()
    
    generator = PremiumDatasetGenerator(args.api_key, args.model)
    generator.generate_dataset(args.output_dir, args.num_samples)

if __name__ == "__main__":
    main()
