"""
模板加载器 - 从server.py中提取HTML内容
"""
import os


def load_html_template():
    """从原始server.py文件中提取HTML模板内容"""
    # 尝试从server.py文件中读取HTML_CONTENT
    server_py_path = os.path.join(os.path.dirname(__file__), 'server.py.backup')
    
    # 如果备份不存在，读取当前的server.py
    if not os.path.exists(server_py_path):
        server_py_path = os.path.join(os.path.dirname(__file__), 'server.py')
    
    try:
        with open(server_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取HTML_CONTENT字符串
        start_marker = 'HTML_CONTENT = """'
        end_marker = '"""'
        
        start_index = content.find(start_marker)
        if start_index == -1:
            raise ValueError("无法找到HTML_CONTENT标记")
        
        start_index += len(start_marker)
        end_index = content.find(end_marker, start_index)
        
        if end_index == -1:
            raise ValueError("无法找到HTML_CONTENT结束标记")
        
        html_content = content[start_index:end_index]
        return html_content
        
    except Exception as e:
        # 如果无法读取，返回一个基本的HTML模板
        print(f"警告: 无法从server.py加载HTML模板: {e}")
        return get_fallback_template()


def get_fallback_template():
    """返回一个备用的基本HTML模板"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>支持AI助手的3D体素查看器</title>
</head>
<body>
    <h1>加载HTML模板失败</h1>
    <p>请确保server.py.backup文件存在，或者原始server.py文件包含HTML_CONTENT。</p>
</body>
</html>
"""
