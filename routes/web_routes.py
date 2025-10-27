"""
Web路由模块 - 处理页面渲染
"""
from flask import render_template_string, send_file
import os
import config


def register_web_routes(app, html_content):
    """注册Web页面路由"""
    
    @app.route('/')
    def index():
        """提供主HTML页面内容。"""
        # 将服务器端验证的密钥和状态传递给前端模板
        return render_template_string(
            html_content,
            api_key_from_file=config.API_KEY_FROM_FILE if config.API_KEY_VALIDATED else '',
            is_key_pre_validated=config.API_KEY_VALIDATED,
            initial_save_data=config.INITIAL_SAVE_DATA
        )
    
    @app.route('/test-texture')
    def test_texture():
        """材质包测试页面"""
        test_page = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_texture_frontend.html')
        if os.path.exists(test_page):
            return send_file(test_page)
        return "测试页面不存在", 404
