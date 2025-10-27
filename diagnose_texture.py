#!/usr/bin/env python3
"""
材质包功能诊断工具
"""
import json
import base64
import zipfile
import io
from pathlib import Path

print("="*70)
print("🔍 材质包功能诊断")
print("="*70)

# 1. 检查材质包文件
print("\n1️⃣  检查材质包文件")
texture_file = Path("faithful32pack.zip")

if texture_file.exists():
    size = texture_file.stat().st_size
    print(f"   ✅ 材质包文件存在")
    print(f"   ✅ 文件大小: {size:,} 字节")
    
    # 2. 检查ZIP内容
    print("\n2️⃣  检查ZIP内容")
    try:
        with zipfile.ZipFile(texture_file, 'r') as zf:
            namelist = zf.namelist()
            print(f"   ✅ ZIP文件有效")
            print(f"   ✅ 包含 {len(namelist)} 个文件")
            
            # 查找材质文件
            texture_files = [
                name for name in namelist 
                if name.startswith('assets/minecraft/textures/blocks/') 
                and name.endswith('.png')
            ]
            print(f"   ✅ 找到 {len(texture_files)} 个材质文件")
            
            # 显示前10个材质
            if texture_files:
                print("\n   前10个材质文件:")
                for i, name in enumerate(texture_files[:10]):
                    texture_name = name.split('/')[-1].replace('.png', '')
                    print(f"      {i+1}. {texture_name}")
    except Exception as e:
        print(f"   ❌ ZIP读取失败: {e}")
else:
    print(f"   ❌ 材质包文件不存在")

# 3. 模拟API响应
print("\n3️⃣  模拟API响应")
if texture_file.exists():
    with open(texture_file, 'rb') as f:
        data = f.read()
        base64_data = base64.b64encode(data).decode('utf-8')
        
    print(f"   ✅ Base64编码成功")
    print(f"   ✅ Base64长度: {len(base64_data):,} 字符")
    
    # 创建模拟响应
    mock_response = {
        "texture": {
            "name": "faithful32pack.zip",
            "mimeType": "application/zip",
            "data": base64_data[:100] + "..." + base64_data[-100:]  # 只显示头尾
        }
    }
    
    print("\n   模拟API响应结构:")
    print(f"      名称: {mock_response['texture']['name']}")
    print(f"      类型: {mock_response['texture']['mimeType']}")
    print(f"      数据长度: {len(base64_data):,} 字符")

# 4. 检查解码
print("\n4️⃣  测试Base64解码")
if texture_file.exists():
    try:
        # 重新读取并解码
        with open(texture_file, 'rb') as f:
            original_data = f.read()
        
        encoded = base64.b64encode(original_data).decode('utf-8')
        decoded = base64.b64decode(encoded)
        
        if decoded == original_data:
            print("   ✅ Base64编解码正确")
            print(f"   ✅ 原始大小: {len(original_data):,} 字节")
            print(f"   ✅ 解码大小: {len(decoded):,} 字节")
            
            # 测试ZIP解析
            try:
                with zipfile.ZipFile(io.BytesIO(decoded), 'r') as zf:
                    print(f"   ✅ 解码后的ZIP可以正常打开")
            except Exception as e:
                print(f"   ❌ 解码后的ZIP无法打开: {e}")
        else:
            print("   ❌ Base64编解码不一致")
    except Exception as e:
        print(f"   ❌ Base64测试失败: {e}")

# 5. 检查API端点
print("\n5️⃣  检查API是否返回完整数据")
try:
    import requests
    response = requests.get('http://127.0.0.1:5000/api/files', timeout=5)
    if response.status_code == 200:
        data = response.json()
        if 'texture' in data:
            tex = data['texture']
            print(f"   ✅ API返回材质包数据")
            print(f"   ✅ 名称: {tex.get('name')}")
            print(f"   ✅ 类型: {tex.get('mimeType')}")
            print(f"   ✅ 数据长度: {len(tex.get('data', '')):,} 字符")
            
            # 尝试解码API返回的数据
            try:
                api_decoded = base64.b64decode(tex['data'])
                print(f"   ✅ API数据可以解码")
                print(f"   ✅ 解码后大小: {len(api_decoded):,} 字节")
                
                # 测试是否是有效的ZIP
                try:
                    with zipfile.ZipFile(io.BytesIO(api_decoded), 'r') as zf:
                        texture_count = len([
                            n for n in zf.namelist() 
                            if n.startswith('assets/minecraft/textures/blocks/') 
                            and n.endswith('.png')
                        ])
                        print(f"   ✅ API返回的ZIP包含 {texture_count} 个材质")
                except Exception as e:
                    print(f"   ❌ API返回的数据不是有效的ZIP: {e}")
            except Exception as e:
                print(f"   ❌ API数据解码失败: {e}")
        else:
            print(f"   ❌ API未返回材质包数据")
    else:
        print(f"   ❌ API请求失败: {response.status_code}")
except ImportError:
    print(f"   ⚠️  requests模块未安装，跳过API测试")
except Exception as e:
    print(f"   ❌ API测试失败: {e}")

print("\n" + "="*70)
print("诊断完成")
print("="*70)
