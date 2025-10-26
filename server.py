import os
import base64
import logging
import threading
import webbrowser
import requests
import argparse
import json
import datetime
import tempfile
import zipfile
from urllib.parse import urlparse
from flask import Flask, jsonify, Response, request, render_template, send_file

# --- 配置 ---
PORT = 5000
INPUT_DIR = "input"
CACHE_DIR = "cache"
SAVE_DIR = "saves"  # 存档目录
API_KEY_FROM_FILE = None # 用于存储从 key.txt 读取的密钥
API_KEY_VALIDATED = False # 标记来自文件的密钥是否已验证成功
DOWNLOADED_MODEL_PATH = None # 用于存储从URL下载的模型路径

# 全局变量保存AI聊天记录和状态
CHAT_HISTORY = []
AGENT_STATE = {
    "is_running": False,
    "is_paused": False,
    "current_part_index": 0,
    "overall_analysis": "",
    "model_name": "gemini-2.5-flash"
}
INITIAL_SAVE_DATA = None # 用于存储从 --input_data 加载的存档


# --- 日志设置 ---
# 配置日志记录，所有日志将输出到终端
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SERVER] - %(levelname)s - %(message)s')

# --- Flask 应用初始化 ---
app = Flask(__name__)
# 禁用 Flask 的默认启动信息，以保持终端输出整洁
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# --- 后端核心功能 ---

def find_first_file(directory, extensions):
    """在指定目录中查找第一个具有给定扩展名的文件。"""
    if not os.path.isdir(directory):
        logging.warning(f"目录 '{directory}' 不存在。")
        return None
    logging.info(f"正在扫描目录 '{directory}'，查找文件类型: {extensions}")
    # 对文件进行排序以确保每次运行结果一致
    for filename in sorted(os.listdir(directory)):
        if any(filename.lower().endswith(ext) for ext in extensions):
            path = os.path.join(directory, filename)
            logging.info(f"找到文件: {path}")
            return path
    logging.warning(f"在 '{directory}' 中未找到类型为 {extensions} 的文件。")
    return None

def read_file_as_base64(filepath):
    """读取文件并将其内容作为 Base64 编码的字符串返回。"""
    if not filepath or not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"无法读取文件 {filepath}: {e}")
        return None

# --- 存档功能 ---

def create_save_data(voxel_data=None, chat_history=None, agent_state=None):
    """创建存档数据结构"""
    save_data = {
        "version": "1.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "voxel_data": voxel_data or {},
        "chat_history": chat_history or [],
        "agent_state": agent_state or {
            "is_running": False,
            "is_paused": False,
            "current_part_index": 0,
            "overall_analysis": "",
            "model_name": "gemini-2.5-flash"
        }
    }
    return save_data

def export_save_file(save_data):
    """导出存档文件为zip格式"""
    temp_dir = tempfile.mkdtemp()
    try:
        # 创建存档数据JSON文件
        save_json_path = os.path.join(temp_dir, "save_data.json")
        with open(save_json_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # 创建zip文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"mine_builder_save_{timestamp}.zip"
        zip_path = os.path.join(SAVE_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(save_json_path, "save_data.json")
        
        return zip_path
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

def import_save_file(zip_path_or_url):
    """导入存档文件"""
    try:
        # 如果是URL，先下载
        if zip_path_or_url.startswith(('http://', 'https://')):
            import requests
            response = requests.get(zip_path_or_url)
            response.raise_for_status()
            
            # 保存到临时文件
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_zip.write(response.content)
            temp_zip.close()
            zip_path = temp_zip.name
        else:
            zip_path = zip_path_or_url
        
        # 解压并读取存档数据
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            with zipf.open('save_data.json') as f:
                save_data = json.load(f)
        
        # 如果是临时文件，清理
        if zip_path_or_url.startswith(('http://', 'https://')):
            os.unlink(zip_path)
        
        return save_data
    except Exception as e:
        logging.error(f"导入存档失败: {e}")
        return None

# --- Flask 路由 ---
@app.route('/')
def index():
    """提供主HTML页面内容。"""
    # 将服务器端验证的密钥和状态传递给前端模板
    return render_template(
        'index.html',
        api_key_from_file=API_KEY_FROM_FILE if API_KEY_VALIDATED else '',
        is_key_pre_validated=API_KEY_VALIDATED,
        initial_save_data=INITIAL_SAVE_DATA
    )

@app.route('/api/files')
def get_initial_files():
    """API端点，用于扫描并提供初始的模型、材质和参考文件。"""
    logging.info("收到自动加载文件的请求...")

    # 1. 查找材质包 (.zip in current directory)
    texture_path = find_first_file('.', ['.zip'])

    # 2. 查找模型
    # 优先使用通过命令行参数提供的模型
    model_path = None
    if DOWNLOADED_MODEL_PATH:
        model_path = DOWNLOADED_MODEL_PATH
        logging.info(f"使用命令行提供的模型: {model_path}")
    else:
        # 否则，在 'input' 目录中查找
        model_path = find_first_file(INPUT_DIR, ['.glb', '.gltf'])

    # 3. 查找参考图 (in INPUT_DIR)
    ref_image_path = find_first_file(INPUT_DIR, ['.png', '.jpg', '.jpeg', '.webp', '.gif'])

    def prepare_file_data(path, default_mime='application/octet-stream'):
        """辅助函数，准备要发送到前端的文件数据。"""
        if not path:
            return None
        import mimetypes
        mime_type, _ = mimetypes.guess_type(path)
        return {
            "name": os.path.basename(path),
            "data": read_file_as_base64(path),
            "mimeType": mime_type or default_mime
        }

    response_data = {
        "model": prepare_file_data(model_path, 'model/gltf-binary'),
        "texture": prepare_file_data(texture_path, 'application/zip'),
        "reference": prepare_file_data(ref_image_path, 'image/png'),
    }

    # 发送前过滤掉未找到的文件
    final_response = {k: v for k, v in response_data.items() if v and v.get('data')}

    logging.info(f"文件扫描完成。结果: 模型={'找到' if 'model' in final_response else '未找到'}, "
                 f"材质包={'找到' if 'texture' in final_response else '未找到'}, "
                 f"参考图={'找到' if 'reference' in final_response else '未找到'}.")

    return jsonify(final_response)

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """API 端点，用于处理来自前端的聊天消息。"""
    data = request.get_json()
    api_key = data.get('apiKey')
    message = data.get('message')
    model = data.get('model', 'gemini-pro') # Default to gemini-pro if not provided

    if not api_key or not message:
        return jsonify({"error": "Missing API key or message."}), 400

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": message}]
        }]
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=45)
        response_data = response.json()

        if response.status_code == 200:
            try:
                reply = response_data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({"reply": reply})
            except (KeyError, IndexError) as e:
                logging.error(f"Error parsing successful Gemini response: {e} | Response: {response_data}")
                return jsonify({"error": "Could not parse AI response."}), 500
        else:
            error_message = response_data.get("error", {}).get("message", "Unknown API error.")
            logging.error(f"Gemini API error. Status: {response.status_code}, Message: {error_message}")
            return jsonify({"error": error_message}), response.status_code

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during chat request: {e}")
        return jsonify({"error": f"Network error: {e}"}), 500
    except Exception as e:
        logging.error(f"An unexpected error occurred in chat handler: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500

@app.route('/api/validate_key', methods=['POST'])
def validate_api_key():
    """API 端点，用于验证前端发送的 Gemini API 密钥。"""
    data = request.get_json()
    api_key = data.get('apiKey')

    if not api_key:
        return jsonify({"success": False, "message": "未提供 API 密钥。"}), 400

    # 使用一个轻量级的 API 调用来验证密钥，例如列出模型
    validation_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

    try:
        response = requests.get(validation_url)
        if response.status_code == 200:
            # 即使是一个空的模型列表也表示密钥是有效的
            logging.info("API 密钥验证成功。")
            return jsonify({"success": True})
        else:
            # API 返回了错误，说明密钥无效或存在其他问题
            logging.warning(f"API 密钥验证失败。状态码: {response.status_code}, 响应: {response.text}")
            return jsonify({"success": False, "message": "API 密钥无效或已过期。"}), 401
    except requests.exceptions.RequestException as e:
        # 网络问题或其他请求错误
        logging.error(f"验证 API 密钥时发生网络错误: {e}")
        return jsonify({"success": False, "message": f"无法连接到验证服务: {e}"}), 500


def _validate_key_on_server(api_key):
    """在服务器端内部验证 API 密钥。"""
    if not api_key:
        return False

    validation_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(validation_url, timeout=5) # 5秒超时
        if response.status_code == 200:
            logging.info("服务器端 API 密钥自动验证成功。")
            return True
        else:
            logging.warning(f"服务器端 API 密钥自动验证失败。状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"服务器端验证 API 密钥时发生网络错误: {e}")
        return False

# --- 存档相关API路由 ---

@app.route('/api/save/export', methods=['POST'])
def export_save():
    """导出存档文件API"""
    try:
        # 更新全局状态
        global CHAT_HISTORY, AGENT_STATE
        
        data = request.get_json()
        voxel_data = data.get('voxelData', {})
        chat_history = data.get('chatHistory', [])
        agent_state = data.get('agentState', AGENT_STATE)
        
        CHAT_HISTORY = chat_history
        AGENT_STATE.update(agent_state)
        
        # 创建存档数据
        save_data = create_save_data(voxel_data, chat_history, agent_state)
        
        # 导出为zip文件
        zip_path = export_save_file(save_data)
        
        if zip_path and os.path.exists(zip_path):
            logging.info(f"存档导出成功: {zip_path}")
            return send_file(zip_path, as_attachment=True, download_name=os.path.basename(zip_path))
        else:
            return jsonify({"success": False, "message": "导出存档失败"}), 500
            
    except Exception as e:
        logging.error(f"导出存档时发生错误: {e}")
        return jsonify({"success": False, "message": f"导出失败: {str(e)}"}), 500

@app.route('/api/save/import', methods=['POST'])
def import_save():
    """导入存档文件API"""
    try:
        # 检查是否有文件上传
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"success": False, "message": "未选择文件"}), 400
            
            # 保存到临时文件
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            file.save(temp_path.name)
            zip_path = temp_path.name
        else:
            # 检查是否有URL
            data = request.get_json()
            url = data.get('url') if data else None
            if not url:
                return jsonify({"success": False, "message": "未提供文件或URL"}), 400
            zip_path = url
        
        # 导入存档数据
        save_data = import_save_file(zip_path)
        
        if save_data:
            # 更新全局状态
            global CHAT_HISTORY, AGENT_STATE
            CHAT_HISTORY = save_data.get('chat_history', [])
            AGENT_STATE.update(save_data.get('agent_state', {}))
            
            logging.info("存档导入成功")
            return jsonify({
                "success": True,
                "data": save_data
            })
        else:
            return jsonify({"success": False, "message": "导入存档失败"}), 500
            
    except Exception as e:
        logging.error(f"导入存档时发生错误: {e}")
        return jsonify({"success": False, "message": f"导入失败: {str(e)}"}), 500

@app.route('/api/agent/pause', methods=['POST'])
def pause_agent():
    """暂停AI代理API"""
    try:
        global AGENT_STATE
        AGENT_STATE['is_paused'] = True
        AGENT_STATE['is_running'] = False
        logging.info("AI代理已暂停")
        return jsonify({"success": True, "message": "AI代理已暂停"})
    except Exception as e:
        logging.error(f"暂停AI代理时发生错误: {e}")
        return jsonify({"success": False, "message": f"暂停失败: {str(e)}"}), 500

@app.route('/api/agent/continue', methods=['POST'])
def continue_agent():
    """继续AI代理API"""
    try:
        global AGENT_STATE
        AGENT_STATE['is_paused'] = False
        AGENT_STATE['is_running'] = True
        logging.info("AI代理已继续")
        return jsonify({"success": True, "message": "AI代理已继续"})
    except Exception as e:
        logging.error(f"继续AI代理时发生错误: {e}")
        return jsonify({"success": False, "message": f"继续失败: {str(e)}"}), 500

@app.route('/api/agent/state', methods=['GET'])
def get_agent_state():
    """获取AI代理状态API"""
    try:
        return jsonify({
            "success": True,
            "state": AGENT_STATE,
            "chat_history": CHAT_HISTORY
        })
    except Exception as e:
        logging.error(f"获取AI代理状态时发生错误: {e}")
        return jsonify({"success": False, "message": f"获取状态失败: {str(e)}"}), 500

# --- 主程序入口 ---
def main():
    """主函数，用于设置并运行Web服务器。"""
    # --- 参数解析 ---
    parser = argparse.ArgumentParser(description="支持AI助手的3D体素查看器")
    parser.add_argument('--input_model', type=str, help='要加载的3D模型URL或本地路径。')
    parser.add_argument('--input_data', type=str, help='要导入的存档文件URL或本地路径。')
    args = parser.parse_args()

    # --- 存档导入逻辑 ---
    global CHAT_HISTORY, AGENT_STATE, INITIAL_SAVE_DATA
    if args.input_data:
        logging.info(f"检测到存档数据参数: {args.input_data}")
        save_data = import_save_file(args.input_data)
        if save_data:
            # 仅将数据存储在初始变量中，让前端处理
            INITIAL_SAVE_DATA = save_data
            logging.info("启动时成功加载存档数据，将传递给前端。")
        else:
            logging.warning("启动时导入存档数据失败")

    # --- 模型加载逻辑 ---
    global DOWNLOADED_MODEL_PATH
    if args.input_model:
        if args.input_model.startswith(('http://', 'https://')):
            # --- 处理URL ---
            url = args.input_model
            logging.info(f"检测到模型 URL: {url}")
            if not os.path.exists(CACHE_DIR):
                os.makedirs(CACHE_DIR)
                logging.info(f"创建缓存目录: '{CACHE_DIR}'")

            try:
                # 从URL提取文件名作为缓存文件名
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename: # 如果路径为空，则使用一个默认名称
                    filename = "cached_model.glb"

                cached_path = os.path.join(CACHE_DIR, filename)

                logging.info(f"正在从URL下载模型到 '{cached_path}'...")
                response = requests.get(url, stream=True)
                response.raise_for_status() # 如果请求失败则引发HTTPError

                with open(cached_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                DOWNLOADED_MODEL_PATH = cached_path
                logging.info(f"模型成功下载并缓存。")

            except requests.exceptions.RequestException as e:
                logging.error(f"从URL下载模型失败: {e}")
        else:
            # --- 处理本地文件路径 ---
            if os.path.exists(args.input_model):
                DOWNLOADED_MODEL_PATH = args.input_model
                logging.info(f"从本地路径加载模型: '{DOWNLOADED_MODEL_PATH}'")
            else:
                logging.warning(f"提供的本地模型路径不存在: '{args.input_model}'")


    # 检查并从 key.txt 文件加载 API 密钥
    global API_KEY_FROM_FILE, API_KEY_VALIDATED
    if os.path.exists('key.txt'):
        with open('key.txt', 'r') as f:
            API_KEY_FROM_FILE = f.read().strip()
        if API_KEY_FROM_FILE:
            logging.info("从 key.txt 文件成功加载 API 密钥，现在进行验证...")
            API_KEY_VALIDATED = _validate_key_on_server(API_KEY_FROM_FILE)
            if not API_KEY_VALIDATED:
                 logging.warning("从 key.txt 加载的密钥验证失败。应用将要求在网页中手动输入。")
        else:
            logging.warning("key.txt 文件存在但为空。")
    else:
        logging.info("未找到 key.txt 文件。应用将要求在网页中手动输入密钥。")

    # 确保input目录存在
    if not os.path.exists(INPUT_DIR):
        logging.info(f"正在创建 '{INPUT_DIR}' 目录，请将模型和参考图放入其中。")
        os.makedirs(INPUT_DIR)

    # 在终端打印使用说明
    print("\n" + "="*70)
    print("🚀 3D AI 助手查看器已启动")
    print(f"服务器正在 http://127.0.0.1:{PORT} 上运行")
    print("\n" + "-"*70)
    print("使用说明:")
    print(f"1. 模型加载: 将你的 .glb/.gltf 模型文件放入 '{INPUT_DIR}/' 文件夹中,")
    print(f"   或使用 `--input_model <URL或路径>` 命令行参数直接加载。")
    print(f"2. 将你的 .png/.jpg 参考图片放入 '{INPUT_DIR}/' 文件夹中。")
    print(f"3. 将你的 .zip 材质包放入与此脚本相同的文件夹中。")
    print("4. 程序已自动在浏览器中打开页面。")
    print("5. 所有文件扫描和服务器日志将显示在此终端窗口中。")
    print("="*70 + "\n")

    # 在新线程中延迟打开浏览器，以确保服务器有时间启动
    url = f"http://127.0.0.1:{PORT}"
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()

    # 启动 Flask 服务器
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == '__main__':
    main()
