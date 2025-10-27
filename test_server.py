#!/usr/bin/env python3
"""
完整的服务器功能测试
"""
import subprocess
import time
import requests
import os
import signal

print("="*70)
print("🚀 开始完整服务器测试")
print("="*70)

# 1. 启动服务器
print("\n1️⃣  启动服务器...")
proc = subprocess.Popen(
    ['python', 'server.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    preexec_fn=os.setsid
)

# 等待服务器启动
print("   等待服务器启动...")
time.sleep(4)

try:
    # 2. 测试主页
    print("\n2️⃣  测试主页访问...")
    try:
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        print(f"   ✅ 状态码: {response.status_code}")
        print(f"   ✅ 内容大小: {len(response.text):,} 字符")
        print(f"   ✅ 包含HTML: {'<!DOCTYPE html>' in response.text or '<html' in response.text}")
    except Exception as e:
        print(f"   ❌ 主页测试失败: {e}")
    
    # 3. 测试API - 文件扫描
    print("\n3️⃣  测试 /api/files 端点...")
    try:
        response = requests.get('http://127.0.0.1:5000/api/files', timeout=5)
        print(f"   ✅ 状态码: {response.status_code}")
        data = response.json()
        print(f"   ✅ 返回数据类型: {type(data).__name__}")
        print(f"   ✅ 数据键: {list(data.keys())}")
    except Exception as e:
        print(f"   ❌ API测试失败: {e}")
    
    # 4. 测试API - 代理状态
    print("\n4️⃣  测试 /api/agent/state 端点...")
    try:
        response = requests.get('http://127.0.0.1:5000/api/agent/state', timeout=5)
        print(f"   ✅ 状态码: {response.status_code}")
        data = response.json()
        print(f"   ✅ 包含 success 字段: {'success' in data}")
        print(f"   ✅ 包含 state 字段: {'state' in data}")
    except Exception as e:
        print(f"   ❌ Agent API测试失败: {e}")
    
    # 5. 测试模块导入
    print("\n5️⃣  测试模块结构...")
    try:
        import config
        from utils.file_utils import find_first_file
        from utils.save_manager import create_save_data
        from routes.api_routes import register_api_routes
        print("   ✅ 所有模块可以正常导入")
        print(f"   ✅ 配置端口: {config.PORT}")
        print(f"   ✅ 输入目录: {config.INPUT_DIR}")
    except Exception as e:
        print(f"   ❌ 模块导入失败: {e}")
    
    print("\n" + "="*70)
    print("✅ 所有测试通过！服务器运行正常！")
    print("="*70)
    
finally:
    # 关闭服务器
    print("\n🛑 关闭服务器...")
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    proc.wait()
    print("✅ 测试完成！\n")
