#!/usr/bin/env python3
"""
测试Gemini 2.5 Pro生成质量 - 改进版
处理JSON注释问题
"""

import json
import re
import google.generativeai as genai

API_KEY = "AIzaSyB3xn379AZKVmCEIywishHGo_57GDj1o9A"

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

SUPER_PROMPT = """你是世界顶级Minecraft建筑大师，擅长创造精美的体素艺术作品。

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

def clean_json_comments(text):
    """移除JSON中的注释"""
    # 移除 // 单行注释
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    # 移除 /* */ 多行注释
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    # 移除多余空行
    text = '\n'.join(line for line in text.split('\n') if line.strip())
    return text

def test_generation():
    """测试生成"""
    genai.configure(api_key=API_KEY)
    
    print("=" * 70)
    print("Gemini 2.5 Pro - 高质量Minecraft建筑生成测试")
    print("=" * 70)
    print()
    
    test_cases = [
        "一座精美的中世纪石塔，高大雄伟，有多层窗户和旗帜",
        "一个现代化的玻璃别墅，简约时尚",
        "一棵巨大的橡树，树干粗壮，树叶茂密",
    ]
    
    for i, building_type in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"测试 {i}/{len(test_cases)}: {building_type}")
        print('='*70)
        
        try:
            # 使用最新模型
            model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-1219")
            
            prompt = SUPER_PROMPT.format(
                block_guide=BLOCK_GUIDE,
                building_type=building_type
            )
            
            print("🚀 正在调用 Gemini 2.5 Pro...")
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            print(f"✓ 收到响应，长度: {len(text)} 字符")
            
            # 清理markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # 移除注释
            text = clean_json_comments(text)
            
            # 解析JSON
            data = json.loads(text)
            
            # 验证数据
            voxels = data.get('voxels', [])
            structure_name = data.get('structure_name', 'Unknown')
            description = data.get('description', 'No description')
            
            print(f"\n✅ 生成成功！")
            print(f"📦 建筑名称: {structure_name}")
            print(f"📝 描述: {description}")
            print(f"🧱 方块数量: {len(voxels)}")
            
            if len(voxels) > 0:
                # 分析质量
                block_types = {}
                y_min, y_max = 15, 0
                x_coords, z_coords = [], []
                
                for v in voxels:
                    bid = v.get('block_id')
                    block_types[bid] = block_types.get(bid, 0) + 1
                    y = v.get('y', 0)
                    y_min = min(y_min, y)
                    y_max = max(y_max, y)
                    x_coords.append(v.get('x', 0))
                    z_coords.append(v.get('z', 0))
                
                height = y_max - y_min + 1
                width_x = max(x_coords) - min(x_coords) + 1
                width_z = max(z_coords) - min(z_coords) + 1
                
                print(f"\n📊 质量分析：")
                print(f"   - 方块种类: {len(block_types)} 种")
                print(f"   - 建筑高度: {height} 层 (y={y_min}~{y_max})")
                print(f"   - 占地面积: {width_x}x{width_z}")
                print(f"   - 方块分布: {dict(list(block_types.items())[:5])}")
                
                # 质量评估
                quality_score = 0
                if len(voxels) >= 100: quality_score += 1
                if len(block_types) >= 3: quality_score += 1
                if height >= 5: quality_score += 1
                if y_min == 0: quality_score += 1
                
                quality = ["较差", "一般", "良好", "优秀", "卓越"][quality_score]
                print(f"   - 质量评分: {quality_score}/4 - {quality}")
            
            # 保存
            output_file = f"sample_quality_{i}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 已保存到: {output_file}")
            
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON解析失败！")
            print(f"错误: {e}")
            print(f"\n原始输出（前800字符）：")
            print(text[:800])
            print("\n需要改进提示词！")
            
        except Exception as e:
            print(f"\n❌ 生成失败: {e}")
    
    print("\n" + "=" * 70)
    print("测试完成！请人工检查生成的样本质量")
    print("如果质量不够好，需要继续优化提示词")
    print("=" * 70)

if __name__ == "__main__":
    test_generation()
