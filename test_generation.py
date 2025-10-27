#!/usr/bin/env python3
"""
测试Gemini 2.5 Pro生成质量
先生成一个样本，检查质量
"""

import json
import google.generativeai as genai

API_KEY = "AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A"

# 方块字典（最常用的）
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
- 35: wool (羊毛，有16种颜色meta 0-15)
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
- 159: stained_clay (染色粘土，meta 0-15不同颜色)
- 251: concrete (混凝土，meta 0-15不同颜色)
"""

ADVANCED_PROMPT = """你是一位专业的Minecraft建筑大师。请生成一个精美、有创意的16x16x16体素建筑。

{block_guide}

任务要求：
1. **创意性**：设计独特、有特色的建筑，不要简单的方块
2. **细节丰富**：添加装饰、窗户、门、屋顶等细节
3. **合理结构**：
   - 建筑要有地基（y=0-1层）
   - 主体结构（墙壁、柱子）
   - 屋顶或顶部装饰
   - 适当的空间分布
4. **材质搭配**：使用2-4种不同方块，颜色搭配和谐
5. **比例适当**：建筑占用空间合理，不要太小也不要完全填满
6. **真实感**：像真实的Minecraft建筑，不是随机方块

建筑类型：{building_type}

输出格式要求（纯JSON，不要任何解释）：
{{
  "structure_name": "建筑名称",
  "description": "简短描述这个建筑的特点",
  "voxels": [
    {{"x": 坐标0-15, "y": 坐标0-15, "z": 坐标0-15, "block_id": 方块ID, "meta_data": 变体(默认0)}}
  ]
}}

要求：
- 至少50个方块（有实质内容）
- 最多500个方块（不要太密集）
- 所有坐标必须在0-15范围内
- 只使用上面列出的方块ID

现在开始生成！输出纯JSON："""

def test_generation():
    """测试生成一个样本"""
    genai.configure(api_key=API_KEY)
    
    # 使用最新的 2.5 Pro
    print("=" * 60)
    print("测试 Gemini 2.5 Pro 生成质量")
    print("=" * 60)
    print()
    
    # 尝试几种建筑类型
    test_cases = [
        "一座精美的中世纪石塔，带有窗户和旗帜",
        "一个现代风格的玻璃房屋",
        "一棵大橡树，有树干和茂密的树叶",
    ]
    
    for i, building_type in enumerate(test_cases, 1):
        print(f"测试 {i}/{len(test_cases)}: {building_type}")
        print("-" * 60)
        
        try:
            model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-1219")
            
            prompt = ADVANCED_PROMPT.format(
                block_guide=BLOCK_GUIDE,
                building_type=building_type
            )
            
            print("正在生成...")
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # 清理markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # 解析JSON
            data = json.loads(text)
            
            # 验证
            num_voxels = len(data.get('voxels', []))
            structure_name = data.get('structure_name', 'Unknown')
            description = data.get('description', 'No description')
            
            print(f"✓ 成功生成！")
            print(f"  建筑名称: {structure_name}")
            print(f"  描述: {description}")
            print(f"  方块数量: {num_voxels}")
            
            # 分析方块分布
            if num_voxels > 0:
                block_types = {}
                y_levels = set()
                for v in data['voxels']:
                    bid = v.get('block_id')
                    block_types[bid] = block_types.get(bid, 0) + 1
                    y_levels.add(v.get('y', 0))
                
                print(f"  使用的方块类型: {len(block_types)} 种")
                print(f"  高度范围: {min(y_levels)} - {max(y_levels)}")
                print(f"  方块分布: {dict(list(block_types.items())[:5])}")
            
            # 保存样本
            output_file = f"test_sample_{i}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  已保存到: {output_file}")
            
            print()
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析失败")
            print(f"  错误: {e}")
            print(f"  原始输出前500字符:")
            print(text[:500])
            print()
        except Exception as e:
            print(f"✗ 生成失败: {e}")
            print()
    
    print("=" * 60)
    print("测试完成！请检查生成的样本质量")
    print("如果质量不好，我们需要改进提示词")
    print("=" * 60)

if __name__ == "__main__":
    test_generation()
