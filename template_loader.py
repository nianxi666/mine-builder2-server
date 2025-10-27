"""
模板加载器 - 加载HTML模板文件
"""
import os


def load_html_template():
    """加载HTML模板内容"""
    # 尝试多个可能的位置
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'templates', 'index.html'),
        os.path.join(os.path.dirname(__file__), 'server.py.backup'),
        os.path.join(os.path.dirname(__file__), 'server.py'),
    ]
    
    # 首先尝试从templates/index.html加载
    template_path = possible_paths[0]
    if os.path.exists(template_path):
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                # 移除可能的Python字符串标记
                html_content = html_content.strip()
                if html_content.startswith('"""'):
                    html_content = html_content[3:]
                if html_content.endswith('"""'):
                    html_content = html_content[:-3]
                return html_content.strip()
        except Exception as e:
            print(f"警告: 无法从templates/index.html加载HTML模板: {e}")
    
    # 尝试从备份文件或当前server.py提取
    for path in possible_paths[1:]:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 提取HTML_CONTENT字符串
                start_marker = 'HTML_CONTENT = """'
                end_marker = '"""'
                
                start_index = content.find(start_marker)
                if start_index == -1:
                    continue
                
                start_index += len(start_marker)
                end_index = content.find(end_marker, start_index)
                
                if end_index == -1:
                    continue
                
                html_content = content[start_index:end_index]
                return html_content
                
            except Exception as e:
                print(f"警告: 无法从{path}加载HTML模板: {e}")
                continue
    
    # 如果所有方法都失败，返回备用模板
    print("警告: 无法加载HTML模板，使用备用模板")
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
    <h1>HTML模板加载失败</h1>
    <p>请确保以下文件之一存在：</p>
    <ul>
        <li>templates/index.html</li>
        <li>server.py.backup（包含HTML_CONTENT）</li>
    </ul>
    <p>如果您刚从Git拉取代码，HTML模板文件应该已包含在 templates/ 目录中。</p>
</body>
</html>
"""
