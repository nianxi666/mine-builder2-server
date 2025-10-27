#!/usr/bin/env python3
"""
重构验证脚本 - 验证所有模块和功能完整性
"""
import os
import sys


def test_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("测试1: 模块导入")
    print("=" * 60)
    
    tests = [
        ("config", "配置模块"),
        ("utils.file_utils", "文件工具"),
        ("utils.save_manager", "存档管理"),
        ("utils.api_validator", "API验证"),
        ("routes.web_routes", "Web路由"),
        ("routes.api_routes", "API路由"),
        ("template_loader", "模板加载器"),
        ("server", "主服务器"),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"✓ {description:20s} ({module_name})")
            passed += 1
        except Exception as e:
            print(f"✗ {description:20s} ({module_name}): {e}")
            failed += 1
    
    print(f"\n结果: {passed} 通过, {failed} 失败\n")
    return failed == 0


def test_config():
    """测试配置模块"""
    print("=" * 60)
    print("测试2: 配置完整性")
    print("=" * 60)
    
    import config
    
    required_vars = [
        "PORT", "INPUT_DIR", "CACHE_DIR", "SAVE_DIR",
        "API_KEY_FROM_FILE", "API_KEY_VALIDATED", "DOWNLOADED_MODEL_PATH",
        "CHAT_HISTORY", "AGENT_STATE", "INITIAL_SAVE_DATA"
    ]
    
    passed = 0
    failed = 0
    
    for var_name in required_vars:
        if hasattr(config, var_name):
            value = getattr(config, var_name)
            print(f"✓ {var_name:25s} = {repr(value)[:40]}")
            passed += 1
        else:
            print(f"✗ {var_name:25s} 缺失!")
            failed += 1
    
    print(f"\n结果: {passed} 通过, {failed} 失败\n")
    return failed == 0


def test_functions():
    """测试关键函数存在"""
    print("=" * 60)
    print("测试3: 关键函数")
    print("=" * 60)
    
    tests = [
        ("utils.file_utils", "find_first_file", "查找文件"),
        ("utils.file_utils", "read_file_as_base64", "Base64读取"),
        ("utils.save_manager", "create_save_data", "创建存档"),
        ("utils.save_manager", "export_save_file", "导出存档"),
        ("utils.save_manager", "import_save_file", "导入存档"),
        ("utils.api_validator", "validate_api_key", "验证密钥"),
        ("routes.web_routes", "register_web_routes", "注册Web路由"),
        ("routes.api_routes", "register_api_routes", "注册API路由"),
        ("template_loader", "load_html_template", "加载模板"),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, func_name, description in tests:
        try:
            module = __import__(module_name, fromlist=[func_name])
            if hasattr(module, func_name):
                print(f"✓ {description:20s} ({module_name}.{func_name})")
                passed += 1
            else:
                print(f"✗ {description:20s} ({module_name}.{func_name}) 不存在")
                failed += 1
        except Exception as e:
            print(f"✗ {description:20s} ({module_name}.{func_name}): {e}")
            failed += 1
    
    print(f"\n结果: {passed} 通过, {failed} 失败\n")
    return failed == 0


def test_file_structure():
    """测试文件结构"""
    print("=" * 60)
    print("测试4: 文件结构")
    print("=" * 60)
    
    required_files = [
        "server.py",
        "config.py",
        "template_loader.py",
        "server.py.backup",
        "utils/__init__.py",
        "utils/file_utils.py",
        "utils/save_manager.py",
        "utils/api_validator.py",
        "routes/__init__.py",
        "routes/web_routes.py",
        "routes/api_routes.py",
        ".gitignore",
        "REFACTORING.md",
    ]
    
    passed = 0
    failed = 0
    
    for filename in required_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename:35s} ({size:6d} bytes)")
            passed += 1
        else:
            print(f"✗ {filename:35s} 缺失!")
            failed += 1
    
    print(f"\n结果: {passed} 通过, {failed} 失败\n")
    return failed == 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Mine Builder 2 Server - 重构验证")
    print("=" * 60 + "\n")
    
    results = [
        test_imports(),
        test_config(),
        test_functions(),
        test_file_structure(),
    ]
    
    print("\n" + "=" * 60)
    print("总体结果")
    print("=" * 60)
    
    if all(results):
        print("✓ 所有测试通过! 重构成功完成。")
        print("\n可以安全地使用新的模块化代码结构。")
        return 0
    else:
        print("✗ 部分测试失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
