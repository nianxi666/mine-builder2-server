#!/usr/bin/env python3
"""
测试HTML模板修复
"""
import os
import sys

print("="*70)
print("🔍 测试HTML模板修复")
print("="*70)

# 1. 检查templates目录
print("\n1️⃣  检查 templates 目录...")
if os.path.exists('templates'):
    print("   ✅ templates/ 目录存在")
    files = os.listdir('templates')
    print(f"   ✅ 包含文件: {files}")
else:
    print("   ❌ templates/ 目录不存在")
    sys.exit(1)

# 2. 检查index.html文件
print("\n2️⃣  检查 index.html 文件...")
template_path = 'templates/index.html'
if os.path.exists(template_path):
    size = os.path.getsize(template_path)
    print(f"   ✅ {template_path} 存在")
    print(f"   ✅ 文件大小: {size:,} 字节")
    if size > 100000:
        print("   ✅ 文件大小正常（>100KB）")
    else:
        print("   ⚠️  文件大小异常（<100KB）")
else:
    print(f"   ❌ {template_path} 不存在")
    sys.exit(1)

# 3. 测试模板加载
print("\n3️⃣  测试模板加载...")
try:
    from template_loader import load_html_template
    html = load_html_template()
    print(f"   ✅ 模板加载成功")
    print(f"   ✅ HTML长度: {len(html):,} 字符")
    
    # 验证内容
    checks = [
        ('<!DOCTYPE', 'DOCTYPE声明'),
        ('<html', 'HTML标签'),
        ('three.js', 'Three.js引用'),
        ('{{ is_key_pre_validated', 'Flask模板变量'),
        ('AI助手', '中文内容'),
    ]
    
    print("\n4️⃣  验证HTML内容...")
    all_passed = True
    for keyword, description in checks:
        if keyword.lower() in html.lower():
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ 缺少{description}")
            all_passed = False
    
    if all_passed:
        print("\n" + "="*70)
        print("✅ 所有测试通过！HTML模板修复成功！")
        print("="*70)
        print("\n现在可以正常启动服务器:")
        print("  python server.py")
    else:
        print("\n⚠️  部分测试失败，请检查HTML内容")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ 模板加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
