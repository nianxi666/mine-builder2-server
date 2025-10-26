"""
Mine Builder 2 Server - 主应用程序入口
这是一个Flask应用，提供3D体素模型查看器与AI助手功能

重构说明：原始的单文件应用已被拆分为多个模块，以提高可维护性：
- config.py: 配置和全局状态
- utils/: 工具函数模块
  - file_utils.py: 文件操作
  - save_manager.py: 存档管理
  - api_validator.py: API密钥验证
- routes/: 路由模块
  - web_routes.py: Web页面路由
  - api_routes.py: API端点路由
- template_loader.py: HTML模板加载
"""
import os
import logging
import threading
import webbrowser
import argparse
import requests
from urllib.parse import urlparse
from flask import Flask

# 导入配置和模块
import config
from utils.file_utils import find_first_file
from utils.save_manager import import_save_file
from utils.api_validator import validate_api_key
from routes.web_routes import register_web_routes
from routes.api_routes import register_api_routes
from template_loader import load_html_template


# --- 日志设置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SERVER] - %(levelname)s - %(message)s'
)

# --- Flask 应用初始化 ---
app = Flask(__name__)

# 禁用 Flask 的默认启动信息，以保持终端输出整洁
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def initialize_app():
    """初始化应用程序，加载HTML模板并注册路由"""
    # 加载HTML模板
    html_content = load_html_template()
    
    # 注册路由
    register_web_routes(app, html_content)
    register_api_routes(app)
    
    logging.info("应用程序初始化完成")


def load_model_from_argument(input_model):
    """从命令行参数加载模型"""
    if input_model.startswith(('http://', 'https://')):
        # --- 处理URL ---
        url = input_model
        logging.info(f"检测到模型 URL: {url}")
        if not os.path.exists(config.CACHE_DIR):
            os.makedirs(config.CACHE_DIR)
            logging.info(f"创建缓存目录: '{config.CACHE_DIR}'")

        try:
            # 从URL提取文件名作为缓存文件名
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:  # 如果路径为空，则使用一个默认名称
                filename = "cached_model.glb"

            cached_path = os.path.join(config.CACHE_DIR, filename)

            logging.info(f"正在从URL下载模型到 '{cached_path}'...")
            response = requests.get(url, stream=True)
            response.raise_for_status()  # 如果请求失败则引发HTTPError

            with open(cached_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            config.DOWNLOADED_MODEL_PATH = cached_path
            logging.info(f"模型成功下载并缓存。")

        except requests.exceptions.RequestException as e:
            logging.error(f"从URL下载模型失败: {e}")
    else:
        # --- 处理本地文件路径 ---
        if os.path.exists(input_model):
            config.DOWNLOADED_MODEL_PATH = input_model
            logging.info(f"从本地路径加载模型: '{config.DOWNLOADED_MODEL_PATH}'")
        else:
            logging.warning(f"提供的本地模型路径不存在: '{input_model}'")


def load_api_key_from_file():
    """从key.txt文件加载并验证API密钥"""
    if os.path.exists('key.txt'):
        with open('key.txt', 'r') as f:
            config.API_KEY_FROM_FILE = f.read().strip()
        if config.API_KEY_FROM_FILE:
            logging.info("从 key.txt 文件成功加载 API 密钥，现在进行验证...")
            config.API_KEY_VALIDATED = validate_api_key(config.API_KEY_FROM_FILE)
            if not config.API_KEY_VALIDATED:
                logging.warning("从 key.txt 加载的密钥验证失败。应用将要求在网页中手动输入。")
        else:
            logging.warning("key.txt 文件存在但为空。")
    else:
        logging.info("未找到 key.txt 文件。应用将要求在网页中手动输入密钥。")


def ensure_directories():
    """确保必要的目录存在"""
    if not os.path.exists(config.INPUT_DIR):
        logging.info(f"正在创建 '{config.INPUT_DIR}' 目录，请将模型和参考图放入其中。")
        os.makedirs(config.INPUT_DIR)
    
    if not os.path.exists(config.SAVE_DIR):
        logging.info(f"正在创建 '{config.SAVE_DIR}' 目录用于存储存档文件。")
        os.makedirs(config.SAVE_DIR)


def print_startup_info():
    """在终端打印启动信息"""
    print("\n" + "="*70)
    print("🚀 3D AI 助手查看器已启动")
    print(f"服务器正在 http://127.0.0.1:{config.PORT} 上运行")
    print("\n" + "-"*70)
    print("使用说明:")
    print(f"1. 模型加载: 将你的 .glb/.gltf 模型文件放入 '{config.INPUT_DIR}/' 文件夹中,")
    print(f"   或使用 `--input_model <URL或路径>` 命令行参数直接加载。")
    print(f"2. 将你的 .png/.jpg 参考图片放入 '{config.INPUT_DIR}/' 文件夹中。")
    print(f"3. 将你的 .zip 材质包放入与此脚本相同的文件夹中。")
    print("4. 程序已自动在浏览器中打开页面。")
    print("5. 所有文件扫描和服务器日志将显示在此终端窗口中。")
    print("="*70 + "\n")


def main():
    """主函数，用于设置并运行Web服务器。"""
    # --- 参数解析 ---
    parser = argparse.ArgumentParser(description="支持AI助手的3D体素查看器")
    parser.add_argument('--input_model', type=str, help='要加载的3D模型URL或本地路径。')
    parser.add_argument('--input_data', type=str, help='要导入的存档文件URL或本地路径。')
    args = parser.parse_args()

    # --- 存档导入逻辑 ---
    if args.input_data:
        logging.info(f"检测到存档数据参数: {args.input_data}")
        save_data = import_save_file(args.input_data)
        if save_data:
            # 仅将数据存储在初始变量中，让前端处理
            config.INITIAL_SAVE_DATA = save_data
            logging.info("启动时成功加载存档数据，将传递给前端。")
        else:
            logging.warning("启动时导入存档数据失败")

    # --- 模型加载逻辑 ---
    if args.input_model:
        load_model_from_argument(args.input_model)

    # --- 加载API密钥 ---
    load_api_key_from_file()

    # --- 确保必要目录存在 ---
    ensure_directories()

    # --- 初始化应用 ---
    initialize_app()

    # --- 打印启动信息 ---
    print_startup_info()

    # 在新线程中延迟打开浏览器，以确保服务器有时间启动
    url = f"http://127.0.0.1:{config.PORT}"
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()

    # 启动 Flask 服务器
    app.run(host='0.0.0.0', port=config.PORT, debug=False)


if __name__ == '__main__':
    main()
