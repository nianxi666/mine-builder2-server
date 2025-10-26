"""
Web路由模块 - 处理页面渲染
"""
from flask import render_template_string
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
