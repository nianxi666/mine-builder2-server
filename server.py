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
from flask import Flask, jsonify, Response, request, render_template_string, send_file

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

# --- HTML/JavaScript 前端内容 ---
# 将您的前端代码完整地嵌入到一个 Python 字符串中
# 我已经修改了其中的 JavaScript 部分以与后端 API 通信
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>支持AI助手的3D体素查看器</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.7.1/jszip.min.js"></script>
    <style>
        body { background-color: #111827; color: #f3f4f6; overflow: hidden; margin: 0; padding: 0; font-family: sans-serif; }
        #main-container { position: relative; width: 100vw; height: 100vh; }
        #mount { width: 100%; height: 100%; display: block; }
        .custom-scrollbar::-webkit-scrollbar { width: 8px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #374151; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #6b7280; }
        .sparkle-button::before { content: '✨'; position: absolute; top: -5px; right: -5px; animation: sparkle 1.5s infinite; }
        @keyframes sparkle { 0%, 100% { transform: scale(1); opacity: 0.7; } 50% { transform: scale(1.5); opacity: 1; } }
    </style>
</head>
<body>
    <!-- 全屏API密钥模态框 -->
    <div id="api-key-modal" class="fixed inset-0 bg-gray-900 bg-opacity-80 flex items-center justify-center z-50">
        <div class="bg-gray-800 p-8 rounded-lg shadow-2xl w-full max-w-md mx-4">
            <h2 class="text-2xl font-bold text-white mb-4">需要 Gemini API 密钥</h2>
            <p class="text-gray-400 mb-6">请输入您的 Gemini API 密钥以继续。AI 功能需要此密钥才能运行。</p>
            <div>
                <label for="modal-api-key-input" class="block text-sm font-medium text-gray-300 mb-2">API 密钥</label>
                <input id="modal-api-key-input" type="password" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md text-gray-200 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="在此处粘贴您的密钥">
            </div>
            <p id="api-key-error-msg" class="text-red-400 text-sm mt-2 h-5"></p>
            <button id="validate-api-key-btn" class="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-md text-base transition-all duration-300 disabled:opacity-50 disabled:cursor-wait">
                <span id="validate-btn-text">验证并开始</span>
                <span id="validate-btn-spinner" class="hidden">
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    验证中...
                </span>
            </button>
        </div>
    </div>
    <div id="main-container" class="opacity-20 pointer-events-none">
        <div id="mount"></div>

        <div class="absolute top-2.5 left-2.5 bg-gray-800 bg-opacity-80 p-3 rounded-lg shadow-xl z-20 max-h-[calc(100vh-20px)] overflow-y-auto w-44 md:w-52 custom-scrollbar">
            <div class="mb-3">
                <label for="modelInput" class="block text-xs font-semibold mb-1.5 text-gray-300">1. 加载模型 (.glb):</label>
                <input type="file" id="modelInput" accept=".glb,.gltf" class="block w-full text-xs text-gray-300 file:mr-2 file:py-1.5 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700" disabled>
            </div>
            <div class="mb-3">
                <label for="texturePackInput" class="block text-xs font-semibold mb-1.5 text-gray-300">2. 加载材质包 (.zip):</label>
                <input type="file" id="texturePackInput" accept=".zip" class="block w-full text-xs text-gray-300 file:mr-2 file:py-1.5 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700" disabled>
            </div>
             <div class="mb-3">
                <label for="reference-image-input" class="block text-xs font-semibold mb-1.5 text-gray-300">3. 上传参考图:</label>
                <input type="file" id="reference-image-input" accept="image/*" class="block w-full text-xs text-gray-300 file:mr-2 file:py-1.5 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700" disabled>
            </div>

            <div class="mt-3 pt-3 border-t border-gray-700">
                <h3 class="text-xs font-semibold mb-1 text-gray-300">镜头控制</h3>
                <div class="grid grid-cols-2 gap-1 mt-2">
                    <button id="view-front" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-3 rounded-md text-xs" disabled>前</button>
                    <button id="view-back" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-3 rounded-md text-xs" disabled>后</button>
                    <button id="view-left" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-3 rounded-md text-xs" disabled>左</button>
                    <button id="view-right" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-3 rounded-md text-xs" disabled>右</button>
                    <button id="view-top" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-3 rounded-md text-xs" disabled>顶</button>
                    <button id="view-bottom" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-3 rounded-md text-xs" disabled>底</button>
                </div>
            </div>

            <div class="mt-3 pt-3 border-t border-gray-700">
                <h3 class="text-xs font-semibold mb-1 text-gray-300">截图 & 导出</h3>
                <button id="screenshot-btn" class="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full" disabled>单视角截图</button>
                <button id="multi-screenshot-btn" class="bg-teal-600 hover:bg-teal-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full mt-1.5 disabled:opacity-50 disabled:cursor-wait" disabled>多视角拼贴图</button>
                <button id="export-txt-btn" class="bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full mt-1.5 disabled:opacity-50" disabled>导出为 TXT</button>
            </div>

            <div class="mt-3 pt-3 border-t border-gray-700">
                <h3 class="text-xs font-semibold mb-1 text-gray-300">编辑体素</h3>
                <button id="delete-selection-btn" class="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full mb-1.5 disabled:opacity-50 disabled:cursor-not-allowed" disabled>删除选中</button>
                <button id="material-inventory-btn" class="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full mb-1.5" disabled>选择材质</button>
                <button id="apply-material-btn" class="bg-teal-600 hover:bg-teal-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full disabled:opacity-50 disabled:cursor-not-allowed" disabled>应用到选中</button>
            </div>

            <div class="mt-3 pt-3 border-t border-gray-700">
                <h3 class="text-xs font-semibold mb-1 text-gray-300">存档功能</h3>
                <button id="export-save-btn" class="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full mb-1.5" disabled>💾 导出存档</button>
                <input type="file" id="import-save-input" accept=".zip" class="hidden">
                <button id="import-save-btn" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full mb-1.5" disabled>📁 导入存档</button>
                <input type="text" id="save-url-input" placeholder="存档直链URL..." class="w-full p-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 text-xs mb-1.5" disabled>
                <button id="import-url-btn" class="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full mb-1.5" disabled>🔗 从URL导入</button>
            </div>

            <div class="mt-3 pt-3 border-t border-gray-700">
                <h3 class="text-xs font-semibold mb-1 text-gray-300">动画</h3>
                <button id="play-animation-btn" class="bg-cyan-600 hover:bg-cyan-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full" disabled>播放动画</button>
                <div class="mt-2">
                    <label for="animation-speed-slider" class="block text-xs font-medium text-gray-400">速度</label>
                    <input type="range" id="animation-speed-slider" min="1" max="100" value="50" class="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer">
                </div>
            </div>

            <div class="mt-3 pt-3 border-t border-gray-700">
                <h3 class="text-xs font-semibold mb-1 text-gray-300">AI 工具</h3>
                <button id="ai-assistant-btn" class="relative bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-3 rounded-md text-xs w-full sparkle-button" disabled>
                    ✨ AI 助手
                </button>
                <button id="ai-agent-btn" class="mt-1.5 w-full bg-cyan-600 hover:bg-cyan-700 text-white font-medium py-2 px-3 rounded-md text-xs disabled:opacity-50 disabled:cursor-not-allowed" disabled>🤖 启动 AI 代理</button>
                <div id="ai-agent-controls" class="hidden mt-1.5 w-full flex space-x-2">
                    <button id="ai-agent-pause-btn" class="flex-grow bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-3 rounded-md text-xs">⏸️ 暂停代理</button>
                    <button id="ai-agent-continue-btn" class="hidden flex-grow bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-3 rounded-md text-xs">▶️ 继续运行</button>
                    <button id="ai-agent-stop-btn" class="flex-shrink-0 bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-3 rounded-md text-xs">⏹️</button>
                </div>
            </div>
        </div>

        <div id="scene-inspector" class="absolute top-2.5 right-2.5 bg-gray-800 bg-opacity-80 p-3 rounded-lg shadow-xl z-20 max-h-[calc(100vh-20px)] w-44 md:w-52">
            <div class="flex justify-between items-center mb-2">
                <h3 class="text-xs font-semibold text-gray-300">模型部件</h3>
                <button id="toggle-inspector-btn" class="text-gray-400 hover:text-white p-1 rounded-full" title="收起/展开" disabled>
                    <svg class="w-4 h-4" id="inspector-chevron-up" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                       <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
                    </svg>
                    <svg class="w-4 h-4 hidden" id="inspector-chevron-down" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                    </svg>
                </button>
            </div>
             <div id="model-parts-list" class="text-xs text-gray-400 custom-scrollbar overflow-y-auto transition-all duration-300">加载模型以查看其部件。</div>
        </div>

        <div id="material-inventory-panel" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-30">
            <div class="bg-gray-800 p-4 rounded-lg shadow-xl max-w-md w-full max-h-[80vh] overflow-y-auto custom-scrollbar">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-gray-200">选择材质</h2>
                    <button id="close-material-panel-btn" class="text-gray-400 hover:text-white text-2xl">&times;</button>
                </div>
                <div id="material-grid" class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                    </div>
            </div>
        </div>

        <div id="ai-assistant-panel" class="hidden fixed inset-x-2 bottom-2 bg-gray-800 bg-opacity-90 border border-gray-700 rounded-lg shadow-xl w-auto h-[65vh] max-h-[65vh] flex flex-col z-40 md:inset-auto md:w-96 md:h-[500px] md:max-h-[calc(100vh-2rem)] md:right-4 md:bottom-4">
            <header class="flex items-center justify-between p-3 border-b border-gray-700">
                <h2 class="text-md font-semibold text-gray-200">✨ AI 助手</h2>
                <div class="flex items-center space-x-2">
                    <button id="ai-clear-chat-btn" title="清空聊天记录" class="text-gray-400 hover:text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                    <button id="ai-model-toggle-btn" title="点击切换 AI 模型" class="bg-gray-700 hover:bg-gray-600 text-white font-medium py-1 px-2.5 rounded-md text-xs transition-colors flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M12 6V3m0 18v-3m6-9h3m-3 6h3M6 9H3m3 6H3" />
                        </svg>
                        <span id="ai-model-name-display"></span>
                    </button>
                     <div class="relative inline-block">
                          <button id="api-key-manager-btn" class="bg-gray-700 hover:bg-gray-600 text-white font-medium py-1 px-2.5 rounded-md text-xs transition-colors flex items-center">
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path></svg>
                              API 密钥
                          </button>
                          <div id="api-key-popup" class="hidden absolute right-0 bottom-full mb-2 w-64 bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-3 z-50">
                              <label for="api-key-input" class="block text-sm font-medium text-gray-300 mb-1">Gemini API 密钥</label>
                              <input id="api-key-input" type="password" class="w-full p-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 text-sm" placeholder="输入您的 API 密钥">
                              <div class="flex justify-end space-x-2 mt-2">
                                  <button id="api-key-cancel" class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-1 px-3 rounded-md text-sm">取消</button>
                                  <button id="api-key-save" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-1 px-3 rounded-md text-sm">保存</button>
                              </div>
                          </div>
                     </div>
                    <button id="ai-panel-close-btn" class="text-gray-400 hover:text-white text-2xl">&times;</button>
                </div>
            </header>
            <div id="ai-chat-history" class="flex-grow p-3 overflow-y-auto space-y-3 custom-scrollbar">
                </div>
            <div class="p-3 border-t border-gray-700">
                <textarea id="ai-user-input" placeholder="与AI助手自由对话..." class="w-full p-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 text-sm resize-none" rows="2" disabled></textarea>
                <button id="ai-send-btn" class="w-full mt-2 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md text-sm disabled:opacity-50" disabled>发送</button>
            </div>
        </div>

    </div>

    <script>
        // 将 Flask 模板变量传递到全局 JavaScript 作用域
        window.isKeyPreValidated = {{ is_key_pre_validated | tojson }};
        window.apiKeyFromFile = "{{ api_key_from_file }}";
        window.initialSaveData = {{ initial_save_data | tojson }};
    </script>
    <script type="module">
        // ====================================================================
        // Constants and Data
        // ====================================================================
        const VOXEL_RESOLUTION = 32;
        const GRID_SIZE = 10;
        const VOXEL_SIZE = GRID_SIZE / VOXEL_RESOLUTION;
        const DEFAULT_VOXEL_PROPERTIES = { blockId: 1, metaData: 0 };
        const FLASH_MODEL_NAME = 'gemini-2.5-flash';
        const PRO_MODEL_NAME = 'gemini-2.5-pro';
        const AGENT_MAX_RETRIES_PER_PART = 2;
        const DEFAULT_BLOCK_ID_LIST = { "1": { "0": "stone", "1": "granite", "2": "polished_granite", "3": "stone_diorite", "4": "polished_diorite", "5": "andersite", "6": "polished_andersite" }, "2": { "0": { "top": "dirt", "bottom": "dirt", "*": "dirt" } }, "3": { "0": "dirt", "1": "coarse_dirt", "2": "podzol" }, "4": { "0": "cobblestone" }, "5": { "0": "planks_oak", "1": "planks_spruce", "3": "planks_jungle", "4": "planks_acacia", "5": "planks_big_oak" }, "7": { "0": "cobblestone" }, "12": { "0": "sand", "1": "red_sand" }, "13": { "0": "gravel" }, "14": { "0": "gold_ore" }, "15": { "0": "iron_ore" }, "16": { "0": "coal_ore" }, "17": { "0": { "top": "log_oak_top", "bottom": "log_oak_top", "*": "log_oak" }, "1": { "top": "log_spruce_top", "bottom": "log_spruce_top", "*": "log_spruce" }, "2": { "top": "log_birch_top", "bottom": "log_birch_top", "*": "log_birch" }, "3": { "top": "log_jungle_top", "bottom": "log_jungle_top", "*": "log_jungle" }, "4": { "east": "log_oak_top:180", "west": "log_oak_top", "top": "log_oak:270", "bottom": "log_oak:270", "north": "log_oak:90", "south": "log_oak:270" }, "5": { "east": "log_spruce_top:180", "west": "log_spruce_top", "top": "log_spruce:270", "bottom": "log_spruce:270", "north": "log_spruce:90", "south": "log_spruce:270" }, "6": { "east": "log_birch_top:180", "west": "log_birch_top", "top": "log_birch:270", "bottom": "log_birch:270", "north": "log_birch:90", "south": "log_birch:270" }, "7": { "east": "log_jungle_top:180", "west": "log_jungle_top", "top": "log_jungle:270", "bottom": "log_jungle:270", "north": "log_jungle:90", "south": "log_jungle:270" }, "8": { "north": "log_oak_top:180", "south": "log_oak_top", "top": "log_oak", "bottom": "log_oak:180", "east": "log_oak:270", "west": "log_oak:90" }, "9": { "north": "log_spruce_top:180", "south": "log_spruce_top", "top": "log_spruce", "bottom": "log_spruce:180", "east": "log_spruce:270", "west": "log_spruce:90" }, "10": { "north": "log_birch_top:180", "south": "log_birch_top", "top": "log_birch", "bottom": "log_birch:180", "east": "log_birch:270", "west": "log_birch:90" }, "11": { "north": "log_jungle_top:180", "south": "log_jungle_top", "top": "log_jungle", "bottom": "log_jungle:180", "east": "log_jungle:270", "west": "log_jungle:90" }, "12": { "*": "log_oak" }, "13": { "*": "log_spruce" }, "14": { "*": "log_birch" }, "15": { "*": "log_jungle" } }, "19": { "0": "sponge", "1": "wet_sponge" }, "21": { "0": "lapis_ore" }, "22": { "0": "lapis_block" }, "23": { "0": { "bottom": "dispenser_front_vertical", "top": "furnace_top", "*": "furnace_side:180" }, "1": { "top": "dispenser_front_vertical", "bottom": "furnace_top", "*": "furnace_side" }, "2": { "north": "dispenser_front_horizontal:0", "south": "furnace_top:0", "top": "furnace_side:0", "east": "furnace_side:270", "bottom": "furnace_side:180", "west": "furnace_side:90" }, "3": { "south": "dispenser_front_horizontal:180", "north": "furnace_top:180", "top": "furnace_side:180", "east": "furnace_side:90", "bottom": "furnace_side:0", "west": "furnace_side:270" }, "4": { "east": "dispenser_front_horizontal:270", "west": "furnace_top:90", "top": "furnace_side:90", "bottom": "furnace_side:270", "north": "furnace_side:90", "south": "furnace_side:270" }, "5": { "west": "dispenser_front_horizontal:90", "east": "furnace_top:270", "top": "furnace_side:270", "bottom": "furnace_side:90", "north": "furnace_side:270", "south": "furnace_side:90" } }, "24": { "0": { "top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_normal" }, "1": { "top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_carved" }, "2": { "top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_smooth" } }, "25": { "0": "noteblock" }, "29": { "0": { "bottom": "piston_top_normal", "top": "piston_bottom", "*": "piston_side:180" }, "1": { "top": "piston_top_normal", "bottom": "piston_bottom", "*": "piston_side" }, "2": { "north": "piston_top_normal:180", "south": "piston_bottom:0", "top": "piston_side:0", "east": "piston_side:270", "bottom": "piston_side:180", "west": "piston_side:90" }, "3": { "south": "piston_top_normal:0", "north": "piston_bottom:180", "top": "piston_side:180", "east": "piston_side:90", "bottom": "piston_side:0", "west": "piston_side:270" }, "4": { "east": "piston_top_normal:90", "west": "piston_bottom:90", "top": "piston_side:90", "bottom": "piston_side:270", "north": "piston_side:90", "south": "piston_side:270" }, "5": { "west": "piston_top_normal:270", "east": "piston_bottom:270", "top": "piston_side:270", "bottom": "piston_side:90", "north": "piston_side:270", "south": "piston_side:90" }, "8": { "bottom": "piston_inner", "top": "piston_bottom", "*": "piston_side:180" }, "9": { "top": "piston_inner", "bottom": "piston_bottom", "*": "piston_side" }, "10": { "north": "piston_inner:180", "south": "piston_bottom:0", "top": "piston_side:0", "east": "piston_side:270", "bottom": "piston_side:180", "west": "piston_side:90" }, "11": { "south": "piston_inner:0", "north": "piston_bottom:180", "top": "piston_side:180", "east": "piston_side:90", "bottom": "piston_side:0", "west": "piston_side:270" }, "12": { "east": "piston_inner:90", "west": "piston_bottom:90", "top": "piston_side:90", "bottom": "piston_side:270", "north": "piston_side:90", "south": "piston_side:270" }, "13": { "west": "piston_inner:270", "east": "piston_bottom:270", "top": "piston_side:270", "bottom": "piston_side:90", "north": "piston_side:270", "south": "piston_side:90" } }, "33": { "0": { "bottom": "piston_top_sticky", "top": "piston_bottom", "*": "piston_side:180" }, "1": { "top": "piston_top_sticky", "bottom": "piston_bottom", "*": "piston_side" }, "2": { "north": "piston_top_sticky:180", "south": "piston_bottom:0", "top": "piston_side:0", "east": "piston_side:270", "bottom": "piston_side:180", "west": "piston_side:90" }, "3": { "south": "piston_top_sticky:0", "north": "piston_bottom:180", "top": "piston_side:180", "east": "piston_side:90", "bottom": "piston_side:0", "west": "piston_side:270" }, "4": { "east": "piston_top_sticky:90", "west": "piston_bottom:90", "top": "piston_side:90", "bottom": "piston_side:270", "north": "piston_side:90", "south": "piston_side:270" }, "5": { "west": "piston_top_sticky:270", "east": "piston_bottom:270", "top": "piston_side:270", "bottom": "piston_side:90", "north": "piston_side:270", "south": "piston_side:90" }, "8": { "bottom": "piston_inner", "top": "piston_bottom", "*": "piston_side:180" }, "9": { "top": "piston_inner", "bottom": "piston_bottom", "*": "piston_side" }, "10": { "north": "piston_inner:180", "south": "piston_bottom:0", "top": "piston_side:0", "east": "piston_side:270", "bottom": "piston_side:180", "west": "piston_side:90" }, "11": { "south": "piston_inner:0", "north": "piston_bottom:180", "top": "piston_side:180", "east": "piston_side:90", "bottom": "piston_side:0", "west": "piston_side:270" }, "12": { "east": "piston_inner:90", "west": "piston_bottom:90", "top": "piston_side:90", "bottom": "piston_side:270", "north": "piston_side:90", "south": "piston_side:270" }, "13": { "west": "piston_inner:270", "east": "piston_bottom:270", "top": "piston_side:270", "bottom": "piston_side:90", "north": "piston_side:270", "south": "piston_side:90" } }, "35": { "0": "wool_colored_white", "1": "wool_colored_orange", "2": "wool_colored_magenta", "3": "wool_colored_light_blue", "4": "wool_colored_yellow", "5": "wool_colored_lime", "6": "wool_colored_pink", "7": "wool_colored_gray", "8": "wool_colored_silver", "9": "wool_colored_cyan", "10": "wool_colored_purple", "11": "wool_colored_blue", "12": "wool_colored_brown", "13": "wool_colored_green", "14": "wool_colored_red", "15": "wool_colored_black" }, "41": { "0": "gold_block" }, "42": { "0": "iron_block" }, "43": { "0": { "top": "stone_slab_top", "bottom": "stone_slab_top", "*": "stone_slab_side" }, "1": { "top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_normal" }, "2": "planks_oak", "3": "cobblestone", "4": "brick", "5": "stonebrick", "6": "nether_brick", "7": "quartz_block_side" }, "45": { "0": "brick" }, "46": { "*": { "top": "tnt_top", "bottom": "tnt_bottom", "*": "tnt_side" } }, "47": { "0": { "top": "planks_oak", "bottom": "planks_oak", "*": "bookshelf" } }, "48": { "0": "cobblestone_mossy" }, "49": { "0": "obsidian" }, "56": { "0": "diamond_ore" }, "57": { "0": "diamond_block" }, "58": { "0": { "north": "crafting_table_side", "west": "crafting_table_side", "east": "crafting_table_front", "south": "crafting_table_front", "top": "crafting_table_top", "bottom": "planks_oak" } }, "60": { "0": "dirt" }, "61": { "2": { "top": "furnace_top", "bottom": "furnace_top", "north": "furnace_front_off", "*": "furnace_side" }, "3": { "top": "furnace_top", "bottom": "furnace_top", "south": "furnace_front_off", "*": "furnace_side" }, "4": { "top": "furnace_top", "bottom": "furnace_top", "west": "furnace_front_off", "*": "furnace_side" }, "5": { "top": "furnace_top", "bottom": "furnace_top", "east": "furnace_front_off", "*": "furnace_side" } }, "62": { "2": { "top": "furnace_top", "bottom": "furnace_top", "north": "furnace_front_on", "*": "furnace_side" }, "3": { "top": "furnace_top", "bottom": "furnace_top", "south": "furnace_front_on", "*": "furnace_side" }, "4": { "top": "furnace_top", "bottom": "furnace_top", "west": "furnace_front_on", "*": "furnace_side" }, "5": { "top": "furnace_top", "bottom": "furnace_top", "east": "furnace_front_on", "*": "furnace_side" } }, "73": { "0": "redstone_ore" }, "74": { "0": "redstone_ore" }, "78": { "0": "snow" }, "79": { "0": "ice" }, "80": { "0": "snow" }, "81": { "*": { "top": "cactus_top", "bottom": "cactus_bottom", "*": "cactus_side" } }, "82": { "0": "clay" }, "84": { "0": { "top": "jukebox_top", "*": "jukebox_side" }, "1": { "top": "jukebox_top", "*": "jukebox_side" } }, "86": { "0": { "top": "pumpkin_top", "bottom": "pumpkin_top", "south": "pumpkin_face_off", "*": "pumpkin_side" }, "1": { "top": "pumpkin_top", "bottom": "pumpkin_top", "west": "pumpkin_face_off", "*": "pumpkin_side" }, "2": { "top": "pumpkin_top", "bottom": "pumpkin_top", "north": "pumpkin_face_off", "*": "pumpkin_side" }, "3": { "top": "pumpkin_top", "bottom": "pumpkin_top", "east": "pumpkin_face_off", "*": "pumpkin_side" } }, "87": { "0": "netherrack" }, "88": { "0": "soul_sand" }, "89": { "0": "glowstone" }, "91": { "0": { "top": "pumpkin_top", "bottom": "pumpkin_top", "south": "pumpkin_face_on", "*": "pumpkin_side" }, "1": { "top": "pumpkin_top", "bottom": "pumpkin_top", "west": "pumpkin_face_on", "*": "pumpkin_side" }, "2": { "top": "pumpkin_top", "bottom": "pumpkin_top", "north": "pumpkin_face_on", "*": "pumpkin_side" }, "3": { "top": "pumpkin_top", "bottom": "pumpkin_top", "east": "pumpkin_face_on", "*": "pumpkin_side" } }, "95": { "0": "glass_white", "1": "glass_orange", "2": "glass_magenta", "3": "glass_light_blue", "4": "glass_yellow", "5": "glass_lime", "6": "glass_pink", "7": "glass_gray", "8": "glass_silver", "9": "glass_cyan", "10": "glass_purple", "11": "glass_blue", "12": "glass_brown", "13": "glass_green", "14": "glass_red", "15": "glass_black" }, "97": { "0": "stone", "1": "cobblestone", "2": "stonebrick", "3": "stonebrick_mossy", "4": "stonebrick_cracked", "5": "stonebrick_carved" }, "98": { "0": "stonebrick", "1": "stonebrick_mossy", "2": "stonebrick_cracked", "3": "stonebrick_carved" }, "99": { "0": "mushroom_block_skin_brown" }, "100": { "0": "mushroom_block_skin_red" }, "103": { "0": { "top": "melon_top", "bottom": "melon_bottom", "*": "melon_side" } }, "110": { "0": { "top": "mycelium_top", "bottom": "dirt", "*": "mycelium_side" } }, "112": { "0": "nether_brick" }, "120": { "0": { "top": "endframe_top", "bottom": "end_stone", "*": "endframe_side" } }, "123": { "0": "redstone_lamp_off" }, "124": { "0": "redstone_lamp_on" }, "125": { "0": "planks_oak", "1": "planks_spruce", "3": "planks_jungle", "4": "planks_acacia", "5": "planks_big_oak" }, "129": { "0": "emerald_ore" }, "133": { "0": "emerald_block" }, "152": { "0": "redstone_block" }, "153": { "0": "quartz_ore" }, "155": { "0": { "top": "quartz_block_top", "bottom": "quartz_block_bottom", "*": "quartz_block_side" }, "1": { "top": "quartz_block_chiseled_top", "bottom": "quartz_block_bottom", "*": "quartz_block_chiseled" }, "2": { "top": "quartz_block_lines_top", "bottom": "quartz_block_lines_top", "*": "quartz_block_lines" } }, "159": { "0": "hardened_clay_stained_white", "1": "hardened_clay_stained_orange", "2": "hardened_clay_stained_magenta", "3": "hardened_clay_stained_light_blue", "4": "hardened_clay_stained_yellow", "5": "hardened_clay_stained_lime", "6": "hardened_clay_stained_pink", "7": "hardened_clay_stained_gray", "8": "hardened_clay_stained_silver", "9": "hardened_clay_stained_cyan", "10": "hardened_clay_stained_purple", "11": "hardened_clay_stained_blue", "12": "hardened_clay_stained_brown", "13": "hardened_clay_stained_green", "14": "hardened_clay_stained_red", "15": "hardened_clay_stained_black" }, "160": { "0": "glass_white", "1": "glass_orange", "2": "glass_magenta", "3": "glass_light_blue", "4": "glass_yellow", "5": "glass_lime", "6": "glass_pink", "7": "glass_gray", "8": "glass_silver", "9": "glass_cyan", "10": "glass_purple", "11": "glass_blue", "12": "glass_brown", "13": "glass_green", "14": "glass_red", "15": "glass_black" }, "162": { "0": { "top": "log_acacia_top", "bottom": "log_acacia_top", "*": "log_acacia" }, "1": { "top": "log_big_oak_top", "bottom": "log_big_oak_top", "*": "log_big_oak" }, "4": { "east": "log_acacia_top:180", "west": "log_acacia_top", "top": "log_acacia:90", "bottom": "log_acacia:270", "north": "log_acacia:90", "south": "log_acacia:270" }, "5": { "east": "log_big_oak_top:180", "west": "log_big_oak_top", "top": "log_big_oak:90", "bottom": "log_big_oak:270", "north": "log_big_oak:90", "south": "log_big_oak:270" }, "8": { "north": "log_acacia_top:180", "south": "log_acacia_top", "top": "log_acacia", "bottom": "log_acacia:180", "east": "log_acacia:90", "west": "log_acacia:270" }, "9": { "north": "log_big_oak_top:180", "south": "log_big_oak_top", "top": "log_big_oak", "bottom": "log_big_oak:180", "east": "log_big_oak:90", "west": "log_big_oak:270" }, "12": { "*": "log_acacia" }, "13": { "*": "log_big_oak" } }, "168": { "0": "prismarine_rough", "1": "prismarine_bricks", "2": "prismarine_dark" }, "170": { "0": { "top": "hay_block_top", "bottom": "hay_block_top", "*": "hay_block_side" } }, "172": { "0": "hardened_clay" }, "173": { "0": "coal_block" }, "174": { "0": "ice_packed" }, "179": { "0": { "top": "red_sandstone_top", "bottom": "red_sandstone_bottom", "*": "red_sandstone_normal" }, "1": { "top": "red_sandstone_top", "bottom": "red_sandstone_bottom", "*": "red_sandstone_carved" }, "2": { "top": "red_sandstone_top", "bottom": "red_sandstone_bottom", "*": "red_sandstone_smooth" } }, "198": { "0": "end_rod" }, "201": { "0": "purpur_block" }, "202": { "0": { "top": "purpur_pillar_top", "bottom": "purpur_pillar_top", "*": "purpur_pillar" } }, "203": { "0": "purpur_block" }, "206": { "0": "end_bricks" }, "207": { "0": "beetroots_stage_3" }, "208": { "0": { "top": "grass_path_top", "bottom": "dirt", "*": "grass_path_side" } }, "209": { "0": "repeating_command_block" }, "210": { "0": "chain_command_block" }, "211": { "0": "command_block" }, "213": { "is_animated": "true", "0": "magma" }, "214": { "0": "nether_wart_block" }, "215": { "0": "red_nether_brick" }, "216": { "0": "bone_block" }, "218": { "0": { "bottom": "observer_front", "top": "observer_back", "north": "observer_top:180", "south": "observer_top:180", "east": "observer_side:180", "west": "observer_side:180" }, "1": { "top": "observer_front", "bottom": "observer_back", "north": "observer_top", "south": "observer_top", "east": "observer_side", "west": "observer_side" }, "2": { "north": "observer_front:180", "south": "observer_back:180", "top": "observer_top:0", "east": "observer_side:270", "bottom": "observer_top:180", "west": "observer_side:90" }, "3": { "south": "observer_front:0", "north": "observer_back:0", "top": "observer_top:180", "east": "observer_side:90", "bottom": "observer_top:0", "west": "observer_side:270" }, "4": { "east": "observer_front:90", "west": "observer_back:270", "top": "observer_top:90", "bottom": "observer_top:270", "north": "observer_side:90", "south": "observer_side:270" }, "5": { "west": "observer_front:270", "east": "observer_back:90", "top": "observer_top:270", "bottom": "observer_top:90", "north": "observer_side:270", "south": "observer_side:90" }, "8": { "bottom": "observer_front", "top": "observer_back_lit", "north": "observer_top:180", "south": "observer_top:180", "east": "observer_side:180", "west": "observer_side:180" }, "9": { "top": "observer_front", "bottom": "observer_back_lit", "north": "observer_top", "south": "observer_top", "east": "observer_side", "west": "observer_side" }, "10": { "north": "observer_front:180", "south": "observer_back_lit:180", "top": "observer_top:0", "east": "observer_side:270", "bottom": "observer_top:180", "west": "observer_side:90" }, "11": { "south": "observer_front:0", "north": "observer_back_lit:0", "top": "observer_top:180", "east": "observer_side:90", "bottom": "observer_top:0", "west": "observer_side:270" }, "12": { "east": "observer_front:90", "west": "observer_back_lit:270", "top": "observer_top:90", "bottom": "observer_top:270", "north": "observer_side:90", "south": "observer_side:270" }, "13": { "west": "observer_front:270", "east": "observer_back_lit:90", "top": "observer_top:270", "bottom": "observer_top:90", "north": "observer_side:270", "south": "observer_side:90" } }, "219": { "0": "shulker_box_white" }, "220": { "0": "shulker_box_orange" }, "221": { "0": "shulker_box_magenta" }, "222": { "0": "shulker_box_light_blue" }, "223": { "0": "shulker_box_yellow" }, "224": { "0": "shulker_box_lime" }, "225": { "0": "shulker_box_pink" }, "226": { "0": "shulker_box_gray" }, "227": { "0": "shulker_box_silver" }, "228": { "0": "shulker_box_cyan" }, "229": { "0": "shulker_box_purple" }, "230": { "0": "shulker_box_blue" }, "231": { "0": "shulker_box_brown" }, "232": { "0": "shulker_box_green" }, "233": { "0": "shulker_box_red" }, "234": { "0": "shulker_box_black" }, "235": { "0": "shulker_box" }, "251": { "0": "concrete_white", "1": "concrete_orange", "2": "concrete_magenta", "3": "concrete_light_blue", "4": "concrete_yellow", "5": "concrete_lime", "6": "concrete_pink", "7": "concrete_gray", "8": "concrete_silver", "9": "concrete_cyan", "10": "concrete_purple", "11": "concrete_blue", "12": "concrete_brown", "13": "concrete_green", "14": "concrete_red", "15": "concrete_black" }, "252": { "0": "concrete_powder_white", "1": "concrete_powder_orange", "2": "concrete_powder_magenta", "3": "concrete_powder_light_blue", "4": "concrete_powder_yellow", "5": "concrete_powder_lime", "6": "concrete_powder_pink", "7": "concrete_powder_gray", "8": "concrete_powder_silver", "9": "concrete_powder_cyan", "10": "concrete_powder_purple", "11": "concrete_powder_blue", "12": "concrete_powder_brown", "13": "concrete_powder_green", "14": "concrete_powder_red", "15": "concrete_powder_black" } };
        const TEXTURE_KEY_TO_COLOR_MAP = { 'stone': 0x888888, 'grass_top': 0x74b44a, 'grass_side': 0x90ac50, 'dirt': 0x8d6b4a, 'cobblestone': 0x7a7a7a, 'planks_oak': 0xaf8f58, 'planks_spruce': 0x806038, 'planks_birch': 0xdace9b, 'planks_jungle': 0xac7d5a, 'planks_acacia': 0xad6c49, 'planks_dark_oak': 0x4c331e, 'bedrock': 0x555555, 'sand': 0xe3dbac, 'gravel': 0x84807b, 'log_oak': 0x685133, 'log_oak_top': 0x9e8054, 'log_spruce': 0x513f27, 'log_spruce_top': 0x716041, 'log_birch': 0xd0cbb0, 'log_birch_top': 0xe0d6b5, 'log_jungle': 0x584c24, 'log_jungle_top': 0x84733c, 'log_acacia': 0x645c50, 'log_acacia_top': 0x918877, 'log_dark_oak': 0x3c2d1b, 'log_big_oak_top': 0x5f4931, 'leaves_oak': 0x44aa44, 'leaves_spruce': 0x4c784c, 'leaves_birch': 0x6aac6a, 'leaves_jungle': 0x48a048, 'leaves_acacia': 0x4c8c4c, 'leaves_dark_oak': 0x4c784c, 'glass': 0xeeeeff, 'glass_pane_top': 0xddddf0, 'brick': 0xa05050, 'obsidian': 0x1c1824, 'diamond_block': 0x7dedde, 'netherrack': 0x883333, 'glowstone': 0xfff055, 'unknown': 0xff00ff };

        // ====================================================================
        // Global State
        // ====================================================================
        let scene, camera, renderer, controls, raycaster;
        let voxelContainerGroup, selectionHighlightMesh;
        let loadedModel = null;
        let referenceImage = null;
        let modelParts = [];
        let currentVoxelCoords = new Set();
        let voxelProperties = new Map();
        let selectedVoxelCoords = new Set();
        let selectedPartId = null;
        let selectedMaterial = null;
        let loadedTextures = new Map();
        let geminiApiKey = '';
        let currentAiModel = FLASH_MODEL_NAME;
        const textureLoader = new THREE.TextureLoader();
        const mouseNdc = new THREE.Vector2();
        let isolateTimer = null;
        let allMaterialsCache = null;

        // --- Agent State ---
        let isAgentRunning = false;
        let isAgentPaused = false;
        let agentAbortController = null;
        let agentCurrentPartIndex = 0;
        let agentOverallAnalysis = "";

        // ====================================================================
        // NEW: Automated Loading and Data Processing
        // ====================================================================

        /**
         * 页面加载时调用，从后端API获取并加载初始文件。
         */
        async function loadInitialFilesFromServer(skipModel = false) {
            console.log(`Attempting to load initial files... (skipModel: ${skipModel})`);
            try {
                const response = await fetch('/api/files');
                if (!response.ok) throw new Error(`Server responded with ${response.status}`);
                const files = await response.json();
                console.log("Received file data:", files);

                // 总是尝试加载材质包和参考图
                if (files.texture && files.texture.data) {
                    addAiChatMessage('system', `正在自动加载材质包: ${files.texture.name}`);
                    const data = await fetch(`data:${files.texture.mimeType};base64,${files.texture.data}`).then(res => res.arrayBuffer());
                    await processTexturePackData(data);
                } else {
                    addAiChatMessage('system', `未找到 .zip 材质包，请手动加载。`);
                }

                if (files.reference && files.reference.data) {
                    addAiChatMessage('system', `正在自动加载参考图: ${files.reference.name}`);
                    const dataUrl = `data:${files.reference.mimeType};base64,${files.reference.data}`;
                    processReferenceImageData(dataUrl);
                } else {
                    addAiChatMessage('system', `未找到参考图，请手动上传。`);
                }

                // 仅在需要时加载模型
                if (!skipModel) {
                    if (files.model && files.model.data) {
                        addAiChatMessage('system', `正在自动加载模型: ${files.model.name}`);
                        const data = await fetch(`data:${files.model.mimeType};base64,${files.model.data}`).then(res => res.arrayBuffer());
                        processModelData(data);
                    } else {
                        addAiChatMessage('system', `未在 'input' 文件夹找到模型，请手动加载。`);
                    }
                }
            } catch (error) {
                console.error("Failed to load initial files:", error);
                addAiChatMessage('system', `自动加载文件失败: ${error.message}`);
            }
        }

        /**
         * 核心逻辑：处理GLB/GLTF模型数据 (ArrayBuffer)
         */
        function processModelData(arrayBuffer) {
            const loader = new THREE.GLTFLoader();
            loader.parse(arrayBuffer, '', (gltf) => {
                currentVoxelCoords.clear();
                voxelProperties.clear();
                loadedModel = gltf.scene;
                const parts = [];
                let partIndex = 1;
                gltf.scene.traverse((child) => {
                    if (child instanceof THREE.Mesh && child.geometry && child.geometry.attributes.position) {
                        parts.push({
                            uuid: child.uuid,
                            name: child.name || `部件 ${partIndex++}`,
                            visible: true,
                        });
                    }
                });
                modelParts = parts;
                voxelizeAndDisplay(gltf.scene);
                updateSceneInspector();
                updateAgentButtonState();
                addAiChatMessage('system', `模型已成功加载。它包含以下部件: ${modelParts.map(p => `"${p.name}"`).join(', ')}.`);
            }, (error) => {
                console.error('解析GLTF模型时出错:', error);
                alert('加载GLTF模型失败。');
                addAiChatMessage('system', `加载GLTF模型失败: ${error}`);
            });
        }

        /**
         * 核心逻辑：处理材质包数据 (ArrayBuffer)
         */
        async function processTexturePackData(arrayBuffer) {
            if (typeof JSZip === 'undefined') return;
            try {
                const zip = await JSZip.loadAsync(arrayBuffer);
                const newTextures = new Map();
                const texturePromises = [];
                const texturePathPrefix = 'assets/minecraft/textures/blocks/';
                loadedTextures.forEach(texture => texture.dispose());
                zip.forEach((relativePath, zipEntry) => {
                    if (relativePath.startsWith(texturePathPrefix) && relativePath.toLowerCase().endsWith('.png') && !zipEntry.dir) {
                        const textureName = relativePath.substring(texturePathPrefix.length).replace(/\\.png$/i, '');
                        if (textureName) {
                            texturePromises.push(
                                zipEntry.async('blob').then(blob => {
                                    const url = URL.createObjectURL(blob);
                                    return new Promise((resolve) => {
                                        textureLoader.load(url, (texture) => {
                                            texture.magFilter = THREE.NearestFilter;
                                            texture.minFilter = THREE.NearestFilter;
                                            newTextures.set(textureName, texture);
                                            URL.revokeObjectURL(url);
                                            resolve();
                                        }, undefined, (err) => { console.error(err); resolve(); });
                                    });
                                })
                            );
                        }
                    }
                });
                await Promise.all(texturePromises);
                loadedTextures = newTextures;
                allMaterialsCache = null;
                populateMaterialInventory();
                updateAgentButtonState();
                if (currentVoxelCoords.size > 0) displayVoxels();
                addAiChatMessage('system', '材质包已成功加载。');
            } catch (error) {
                console.error('加载材质包时出错:', error);
                alert('加载材质包失败。');
                addAiChatMessage('system', `加载材质包失败: ${error}`);
            }
        }

        /**
         * 核心逻辑：处理参考图数据 (DataURL)
         */
        function processReferenceImageData(dataUrl) {
            referenceImage = dataUrl;
            addAiChatMessage('system', '参考图已成功加载。', [{src: referenceImage, label: '参考图'}]);
            updateAgentButtonState();
        }


        // ====================================================================
        // Utility Functions
        // ====================================================================
        const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

        function getTextureKeyForVoxel(blockId, metaData, blockDefs) {
            const blockEntry = blockDefs[blockId.toString()];
            if (!blockEntry) return 'unknown';
            const metaEntry = blockEntry[metaData.toString()];
            if (!metaEntry) return 'unknown';
            if (typeof metaEntry === 'string') return metaEntry.split(':')[0];
            if (typeof metaEntry === 'object' && metaEntry !== null) {
                const key = metaEntry['*'] || metaEntry.top || metaEntry.side || 'unknown';
                return key.split(':')[0];
            }
            return 'unknown';
        }

        function getAllMinecraftMaterials() {
             if (allMaterialsCache) return allMaterialsCache;

            const materials = new Set();
            const uniqueMaterials = [];
            for (const blockIdStr in DEFAULT_BLOCK_ID_LIST) {
                const blockId = parseInt(blockIdStr, 10);
                const blockEntry = DEFAULT_BLOCK_ID_LIST[blockIdStr];
                for (const metaDataStr in blockEntry) {
                    if (isNaN(parseInt(metaDataStr))) continue;
                    const metaData = parseInt(metaDataStr, 10);
                    const metaEntry = blockEntry[metaDataStr];
                    let name = '';
                    let textureKey = '';
                    if (typeof metaEntry === 'string') {
                        textureKey = metaEntry;
                    } else if (typeof metaEntry === 'object' && metaEntry !== null) {
                        textureKey = metaEntry['*'] || metaEntry.top || metaEntry.side || 'unknown';
                    }
                    if (textureKey) {
                        textureKey = textureKey.split(':')[0]; // Remove rotation info
                        name = textureKey.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        if (!materials.has(name)) {
                            materials.add(name);
                            const isAvailable = loadedTextures.has(textureKey);
                            uniqueMaterials.push({ name, id: blockId, meta: metaData, textureKey, isAvailable });
                        }
                    }
                }
            }
            allMaterialsCache = uniqueMaterials;
            return uniqueMaterials;
        }

        // ====================================================================
        // Core 3D and Voxelization Logic
        // ====================================================================

        function init() {
            const mount = document.getElementById('mount');
            if (!mount) return;
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1f2937);
            camera = new THREE.PerspectiveCamera(75, mount.clientWidth / mount.clientHeight, 0.1, 1000);
            camera.position.set(GRID_SIZE * 0.8, GRID_SIZE * 0.8, GRID_SIZE * 0.8);
            renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
            renderer.setSize(mount.clientWidth, mount.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            // --- Enable Shadows ---
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            mount.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.target.set(0, GRID_SIZE / 2, 0);
            controls.update();

            scene.add(new THREE.AmbientLight(0xffffff, 0.8)); // Reduce ambient light
            const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
            directionalLight.position.set(GRID_SIZE, GRID_SIZE * 1.5, GRID_SIZE * 0.5);
            // --- Enable Shadows on Light ---
            directionalLight.castShadow = true;
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
            const d = GRID_SIZE * 1.5;
            directionalLight.shadow.camera.left = -d;
            directionalLight.shadow.camera.right = d;
            directionalLight.shadow.camera.top = d;
            directionalLight.shadow.camera.bottom = -d;
            directionalLight.shadow.camera.far = GRID_SIZE * 5;
            directionalLight.shadow.bias = -0.0001;
            scene.add(directionalLight);

            const gridHelper = new THREE.GridHelper(GRID_SIZE, VOXEL_RESOLUTION, 0x555555, 0x333333);
            scene.add(gridHelper);

            // --- Add Ground Plane to Receive Shadows ---
            const groundPlane = new THREE.Mesh(
                new THREE.PlaneGeometry(GRID_SIZE * 2, GRID_SIZE * 2),
                new THREE.ShadowMaterial({ opacity: 0.3 })
            );
            groundPlane.rotation.x = -Math.PI / 2;
            groundPlane.position.y = -0.01;
            groundPlane.receiveShadow = true;
            scene.add(groundPlane);

            voxelContainerGroup = new THREE.Group();
            scene.add(voxelContainerGroup);

            const highlightGeometry = new THREE.BoxGeometry(VOXEL_SIZE, VOXEL_SIZE, VOXEL_SIZE);
            const highlightMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.4, side: THREE.DoubleSide });
            selectionHighlightMesh = new THREE.InstancedMesh(highlightGeometry, highlightMaterial, VOXEL_RESOLUTION ** 3);
            selectionHighlightMesh.count = 0;
            scene.add(selectionHighlightMesh);
            raycaster = new THREE.Raycaster();
            window.addEventListener('resize', onWindowResize);
            mount.addEventListener('click', onCanvasClick);
            animate();
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }

        function onWindowResize() {
            const mount = document.getElementById('mount');
            if (!mount) return;
            const width = mount.clientWidth;
            const height = mount.clientHeight;
            renderer.setSize(width, height);
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
        }

        function displayVoxels() {
            if (!voxelContainerGroup) return;
            while (voxelContainerGroup.children.length > 0) {
                const child = voxelContainerGroup.children[0];
                voxelContainerGroup.remove(child);
                child.geometry.dispose();
                if (Array.isArray(child.material)) child.material.forEach(m => m.dispose());
                else child.material.dispose();
            }
            const exportBtn = document.getElementById('export-txt-btn');
            const playAnimationBtn = document.getElementById('play-animation-btn');
            if (currentVoxelCoords.size === 0) {
                if(exportBtn) exportBtn.disabled = true;
                if(playAnimationBtn) playAnimationBtn.disabled = true;
                updateSelectionUI();
                return;
            }
            if(exportBtn) exportBtn.disabled = false;
            if(playAnimationBtn) playAnimationBtn.disabled = false;

            const materialToInstancesMap = new Map();
            currentVoxelCoords.forEach(coordString => {
                const voxelProps = voxelProperties.get(coordString) || DEFAULT_VOXEL_PROPERTIES;
                const textureKey = getTextureKeyForVoxel(voxelProps.blockId, voxelProps.metaData, DEFAULT_BLOCK_ID_LIST);
                if (!materialToInstancesMap.has(textureKey)) materialToInstancesMap.set(textureKey, []);
                const [x, y, z] = coordString.split(',').map(Number);
                const halfGrid = GRID_SIZE / 2;
                const posX = -halfGrid + (x + 0.5) * VOXEL_SIZE;
                const posY = (y + 0.5) * VOXEL_SIZE;
                const posZ = -halfGrid + (z + 0.5) * VOXEL_SIZE;
                const matrix = new THREE.Matrix4().setPosition(posX, posY, posZ);
                materialToInstancesMap.get(textureKey).push({ matrix, coord: coordString });
            });
            const baseVoxelGeometry = new THREE.BoxGeometry(VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98);
            materialToInstancesMap.forEach((instances, textureKey) => {
                if (instances.length === 0) return;
                let material;
                const texture = loadedTextures.get(textureKey);
                if (texture) {
                    material = new THREE.MeshStandardMaterial({ map: texture, metalness: 0.1, roughness: 0.8 });
                } else {
                    const color = TEXTURE_KEY_TO_COLOR_MAP[textureKey] || TEXTURE_KEY_TO_COLOR_MAP['unknown'];
                    material = new THREE.MeshLambertMaterial({ color });
                }
                const instancedMesh = new THREE.InstancedMesh(baseVoxelGeometry, material, instances.length);
                instancedMesh.castShadow = true;
                instancedMesh.receiveShadow = true;
                const coordMapForMesh = [];
                instances.forEach((instanceData, i) => {
                    instancedMesh.setMatrixAt(i, instanceData.matrix);
                    coordMapForMesh[i] = instanceData.coord;
                });
                instancedMesh.instanceMatrix.needsUpdate = true;
                instancedMesh.userData = { coordMap: coordMapForMesh };
                voxelContainerGroup.add(instancedMesh);
            });
            const newSelectedCoords = new Set();
            selectedVoxelCoords.forEach(coord => {
                if (currentVoxelCoords.has(coord)) newSelectedCoords.add(coord);
            });
            selectedVoxelCoords = newSelectedCoords;
            if (selectedVoxelCoords.size === 0) selectedPartId = null;
            updateSelectionHighlight();
            updateSelectionUI();
        }

        function voxelizeAndDisplay(model) {
            selectedVoxelCoords.clear();
            selectedPartId = null;
            const newVoxelCoords = new Set();
            const newVoxelProps = new Map();
            const worldToVoxelIndex = (worldPos, outVector) => {
                const halfGrid = GRID_SIZE / 2;
                const idx = Math.floor(((worldPos.x + halfGrid) / GRID_SIZE) * VOXEL_RESOLUTION);
                const idy = Math.floor((worldPos.y / GRID_SIZE) * VOXEL_RESOLUTION);
                const idz = Math.floor(((worldPos.z + halfGrid) / GRID_SIZE) * VOXEL_RESOLUTION);
                return outVector.set(idx, idy, idz);
            };
            const voxelizeTriangle = (vA, vB, vC, partId) => {
                const triBox = new THREE.Box3().setFromPoints([vA, vB, vC]);
                const minVoxelIndex = worldToVoxelIndex(triBox.min, new THREE.Vector3());
                const maxVoxelIndex = worldToVoxelIndex(triBox.max, new THREE.Vector3());
                minVoxelIndex.clampScalar(0, VOXEL_RESOLUTION - 1);
                maxVoxelIndex.clampScalar(0, VOXEL_RESOLUTION - 1);
                for (let x = minVoxelIndex.x; x <= maxVoxelIndex.x; x++) {
                    for (let y = minVoxelIndex.y; y <= maxVoxelIndex.y; y++) {
                        for (let z = minVoxelIndex.z; z <= maxVoxelIndex.z; z++) {
                            const coordString = `${x},${y},${z}`;
                            newVoxelCoords.add(coordString);
                            if (!newVoxelProps.has(coordString)) {
                                newVoxelProps.set(coordString, { ...DEFAULT_VOXEL_PROPERTIES, partId });
                            }
                        }
                    }
                }
            };
            const tempMatrix = new THREE.Matrix4();
            const tempVectorA = new THREE.Vector3();
            const tempVectorB = new THREE.Vector3();
            const tempVectorC = new THREE.Vector3();
            const modelBoundingBox = new THREE.Box3();
            model.updateMatrixWorld(true);
            modelBoundingBox.setFromObject(model, true);
            if (modelBoundingBox.isEmpty()) {
                currentVoxelCoords = newVoxelCoords;
                voxelProperties = newVoxelProps;
                displayVoxels();
                return;
            }
            const modelSize = modelBoundingBox.getSize(new THREE.Vector3());
            const modelCenter = modelBoundingBox.getCenter(new THREE.Vector3());
            const maxDim = Math.max(modelSize.x, modelSize.y, modelSize.z);
            const scaleFactor = maxDim > 0 ? GRID_SIZE / maxDim : 1;
            const translationMatrix = new THREE.Matrix4().makeTranslation(-modelCenter.x, -modelBoundingBox.min.y, -modelCenter.z);
            const scaleMatrix = new THREE.Matrix4().makeScale(scaleFactor, scaleFactor, scaleFactor);
            const finalTransform = new THREE.Matrix4().multiply(scaleMatrix).multiply(translationMatrix);
            model.traverse((child) => {
                if (child instanceof THREE.Mesh && child.visible && child.geometry.isBufferGeometry) {
                    const geometry = child.geometry;
                    const positionAttribute = geometry.attributes.position;
                    const indexAttribute = geometry.index;
                    const partId = child.uuid;
                    tempMatrix.multiplyMatrices(finalTransform, child.matrixWorld);
                    if (positionAttribute) {
                        if (indexAttribute) {
                            for (let i = 0; i < indexAttribute.count; i += 3) {
                                const a = indexAttribute.getX(i);
                                const b = indexAttribute.getX(i + 1);
                                const c = indexAttribute.getX(i + 2);
                                tempVectorA.fromBufferAttribute(positionAttribute, a).applyMatrix4(tempMatrix);
                                tempVectorB.fromBufferAttribute(positionAttribute, b).applyMatrix4(tempMatrix);
                                tempVectorC.fromBufferAttribute(positionAttribute, c).applyMatrix4(tempMatrix);
                                voxelizeTriangle(tempVectorA, tempVectorB, tempVectorC, partId);
                            }
                        } else {
                            for (let i = 0; i < positionAttribute.count; i += 3) {
                                tempVectorA.fromBufferAttribute(positionAttribute, i).applyMatrix4(tempMatrix);
                                tempVectorB.fromBufferAttribute(positionAttribute, i + 1).applyMatrix4(tempMatrix);
                                tempVectorC.fromBufferAttribute(positionAttribute, i + 2).applyMatrix4(tempMatrix);
                                voxelizeTriangle(tempVectorA, tempVectorB, tempVectorC, partId);
                            }
                        }
                    }
                }
            });
            currentVoxelCoords = newVoxelCoords;
            voxelProperties = newVoxelProps;
            saveAppStateToLocalStorage(); // 保存状态

            if (modelParts.length > 0) {
                const partInfo = new Map();
                modelParts.forEach(p => {
                    partInfo.set(p.uuid, { name: p.name, count: 0, isOccluded: true, voxels: [] });
                });

                for (const [coord, props] of voxelProperties.entries()) {
                    if (partInfo.has(props.partId)) {
                        const info = partInfo.get(props.partId);
                        info.count++;
                        info.voxels.push(coord.split(',').map(Number));
                    }
                }

                const isVoxelVisible = (x, y, z) => {
                    return !currentVoxelCoords.has(`${x+1},${y},${z}`) || !currentVoxelCoords.has(`${x-1},${y},${z}`) ||
                           !currentVoxelCoords.has(`${x},${y+1},${z}`) || !currentVoxelCoords.has(`${x},${y-1},${z}`) ||
                           !currentVoxelCoords.has(`${x},${y},${z+1}`) || !currentVoxelCoords.has(`${x},${y},${z-1}`);
                };

                for (const info of partInfo.values()) {
                    let isAnyVoxelVisible = false;
                    for (const [x, y, z] of info.voxels) {
                        if (isVoxelVisible(x, y, z)) {
                            isAnyVoxelVisible = true;
                            break;
                        }
                    }
                    info.isOccluded = !isAnyVoxelVisible;
                }

                modelParts.forEach(p => {
                    const info = partInfo.get(p.uuid);
                    p.voxelCount = info ? info.count : 0;
                    p.isOccluded = info ? info.isOccluded : false;
                });

                modelParts.sort((a, b) => (b.voxelCount || 0) - (a.voxelCount || 0));
            }
            displayVoxels();
        }

        // ====================================================================
        // UI Interaction Handlers
        // ====================================================================

        // 改为调用核心处理函数
        function handleModelLoad(event) {
            const file = event.target.files?.[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                if (e.target?.result) {
                    addAiChatMessage('system', `正在从文件输入加载模型: ${file.name}`);
                    processModelData(e.target.result);
                }
            };
            reader.readAsArrayBuffer(file);
            event.target.value = '';
        }

        // 改为调用核心处理函数
        function handleReferenceImageLoad(event) {
            const file = event.target.files?.[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                if (e.target?.result) {
                    addAiChatMessage('system', `正在从文件输入加载参考图: ${file.name}`);
                    processReferenceImageData(e.target.result);
                }
            };
            reader.readAsDataURL(file);
            event.target.value = '';
        }

        // 改为调用核心处理函数
        async function handleTexturePackLoad(event) {
            const file = event.target.files?.[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = async (e) => {
                if (e.target?.result) {
                    addAiChatMessage('system', `正在从文件输入加载材质包: ${file.name}`);
                    await processTexturePackData(e.target.result);
                }
            };
            reader.readAsArrayBuffer(file);
            event.target.value = '';
        }


        function setCameraView(view) {
            if (!camera || !controls) return;
            const distance = GRID_SIZE * 1.5;
            const center = new THREE.Vector3(0, GRID_SIZE / 2, 0);
            switch (view) {
                case 'front': camera.position.set(0, GRID_SIZE / 2, distance); break;
                case 'back': camera.position.set(0, GRID_SIZE / 2, -distance); break;
                case 'left': camera.position.set(-distance, GRID_SIZE / 2, 0); break;
                case 'right': camera.position.set(distance, GRID_SIZE / 2, 0); break;
                case 'top': camera.position.set(0, distance + GRID_SIZE / 2, 0); break;
                case 'bottom': camera.position.set(0, -distance + GRID_SIZE / 2, 0); break;
            }
            camera.lookAt(center);
            controls.target.copy(center);
            controls.update();
        }

        function handleScreenshot() {
            if (renderer?.domElement) {
                renderer.render(scene, camera);
                const dataURL = renderer.domElement.toDataURL('image/png');
                const link = document.createElement('a');
                link.href = dataURL;
                link.download = 'voxel-view-screenshot.png';
                link.click();
            }
        }

        async function createCollage(viewsToCapture = []) {
            if (!renderer || viewsToCapture.length === 0) return null;

            const originalState = {
                position: camera.position.clone(),
                quaternion: camera.quaternion.clone(),
                target: controls.target.clone()
            };

            const singleViewWidth = renderer.domElement.width;
            const singleViewHeight = renderer.domElement.height;

            const cols = Math.ceil(Math.sqrt(viewsToCapture.length));
            const rows = Math.ceil(viewsToCapture.length / cols);

            const collageCanvas = document.createElement('canvas');
            collageCanvas.width = cols * singleViewWidth;
            collageCanvas.height = rows * singleViewHeight;
            const ctx = collageCanvas.getContext('2d');
            ctx.fillStyle = '#1f2937';
            ctx.fillRect(0, 0, collageCanvas.width, collageCanvas.height);

            ctx.font = '24px sans-serif';
            ctx.fillStyle = 'white';
            ctx.strokeStyle = 'black';
            ctx.lineWidth = 4;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';

            for (let i = 0; i < viewsToCapture.length; i++) {
                const viewName = viewsToCapture[i];

                if (viewName === 'current') {
                    camera.position.copy(originalState.position);
                    camera.quaternion.copy(originalState.quaternion);
                    controls.target.copy(originalState.target);
                    controls.update();
                } else {
                    setCameraView(viewName);
                }

                renderer.render(scene, camera);
                await sleep(10);
                const dataURL = renderer.domElement.toDataURL();

                const img = new Image();
                const promise = new Promise(resolve => img.onload = resolve);
                img.src = dataURL;
                await promise;

                const col = i % cols;
                const row = Math.floor(i / cols);
                const dx = col * singleViewWidth;
                const dy = row * singleViewHeight;

                ctx.drawImage(img, dx, dy);
                const label = viewName.charAt(0).toUpperCase() + viewName.slice(1);
                ctx.strokeText(label, dx + singleViewWidth / 2, dy + 10);
                ctx.fillText(label, dx + singleViewWidth / 2, dy + 10);
            }

            camera.position.copy(originalState.position);
            camera.quaternion.copy(originalState.quaternion);
            controls.target.copy(originalState.target);
            controls.update();

            return collageCanvas.toDataURL('image/jpeg', 0.9);
        }

        async function handleMultiViewScreenshot() {
            const btn = document.getElementById('multi-screenshot-btn');
            btn.disabled = true;
            btn.textContent = '生成中...';

            const collageDataUrl = await createCollage(['front', 'back', 'left', 'right', 'top', 'bottom']);

            if (collageDataUrl) {
                const link = document.createElement('a');
                link.href = collageDataUrl;
                link.download = 'multi-view-collage.jpg';
                link.click();
            }

            btn.disabled = false;
            btn.textContent = '多视角拼贴图';
        }

        function handleExportToTxt() {
            if (voxelProperties.size === 0) {
                alert("没有体素数据可导出。");
                return;
            }

            const outputLines = [];
            outputLines.push("# Voxel Export Data");
            outputLines.push("# Format: x y z blockId metaData");

            voxelProperties.forEach((props, coordString) => {
                const [x, y, z] = coordString.split(',');
                const blockId = props.blockId || 0;
                const metaData = props.metaData || 0;
                outputLines.push(`${x} ${y} ${z} ${blockId} ${metaData}`);
            });

            const textContent = outputLines.join('\\n');
            const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'voxel_output.txt';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }


        function handleDeleteSelection() {
            if (selectedVoxelCoords.size > 0) {
                selectedVoxelCoords.forEach(coord => {
                    currentVoxelCoords.delete(coord);
                    voxelProperties.delete(coord);
                });
                selectedVoxelCoords.clear();
                selectedPartId = null;
                displayVoxels();
                saveAppStateToLocalStorage(); // 保存状态
            }
        }

        function handleApplyMaterialToSelection() {
            if (selectedVoxelCoords.size > 0 && selectedMaterial) {
                selectedVoxelCoords.forEach(coord => {
                    if (currentVoxelCoords.has(coord)) {
                        const currentProps = voxelProperties.get(coord);
                        voxelProperties.set(coord, {
                            ...currentProps,
                            blockId: selectedMaterial.id,
                            metaData: selectedMaterial.meta,
                        });
                    }
                });
                displayVoxels();
                saveAppStateToLocalStorage(); // 保存状态
            }
        }

        function unhideAllParts() {
            if (isolateTimer) {
                clearTimeout(isolateTimer);
                isolateTimer = null;
            }
            if (!loadedModel) return;
            modelParts.forEach(p => {
                const partObject = loadedModel.getObjectByProperty('uuid', p.uuid);
                if (partObject) {
                    partObject.visible = true;
                    p.visible = true;
                }
            });
            voxelizeAndDisplay(loadedModel);
            updateSceneInspector();
        }

        function onCanvasClick(event) {
            if (isAgentRunning) return;
            const mount = document.getElementById('mount');
            if (!mount || !raycaster || !camera || !voxelContainerGroup || currentVoxelCoords.size === 0) return;
            const rect = mount.getBoundingClientRect();
            mouseNdc.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouseNdc.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            raycaster.setFromCamera(mouseNdc, camera);
            const instancedMeshes = voxelContainerGroup.children.filter(child => child instanceof THREE.InstancedMesh);
            if (instancedMeshes.length === 0) {
                selectedVoxelCoords.clear();
                selectedPartId = null;
                updateSelectionUI();
                return;
            }
            const intersects = raycaster.intersectObjects(instancedMeshes, false);
            if (intersects.length > 0 && intersects[0].instanceId !== undefined) {
                const intersection = intersects[0];
                const instancedMesh = intersection.object;
                const instanceId = intersection.instanceId;
                const coordString = instancedMesh.userData.coordMap?.[instanceId];
                if (coordString) {
                    selectedVoxelCoords.clear();
                    selectedVoxelCoords.add(coordString);
                    const voxelProps = voxelProperties.get(coordString);
                    selectedPartId = voxelProps?.partId || null;
                } else {
                    selectedVoxelCoords.clear();
                    selectedPartId = null;
                }
            } else {
                selectedVoxelCoords.clear();
                selectedPartId = null;
            }
            updateSelectionHighlight();
            updateSelectionUI();
        }

        // ====================================================================
        // UI Update Functions
        // ====================================================================
        function updateAgentButtonState() {
            const btn = document.getElementById('ai-agent-btn');
            if (btn) {
                const isReady = loadedModel !== null && loadedTextures.size > 0 && referenceImage !== null;
                btn.disabled = !isReady;
                if (!isReady) {
                    let title = "请按顺序完成：";
                    if (!loadedModel) title += " 1.加载模型";
                    else if (loadedTextures.size === 0) title += " 2.加载材质包";
                    else if (!referenceImage) title += " 3.上传参考图";
                    btn.title = title;
                } else {
                    btn.title = "让 AI 自动为所有部件添加材质";
                }
            }
        }

        function updateSelectionHighlight() {
            if (!selectionHighlightMesh) return;
            const coordsArray = Array.from(selectedVoxelCoords);
            selectionHighlightMesh.count = coordsArray.length;
            if (coordsArray.length > 0) {
                const matrix = new THREE.Matrix4();
                const halfGrid = GRID_SIZE / 2;
                coordsArray.forEach((coord, i) => {
                    const [x, y, z] = coord.split(',').map(Number);
                    matrix.setPosition(-halfGrid + (x + 0.5) * VOXEL_SIZE, (y + 0.5) * VOXEL_SIZE, -halfGrid + (z + 0.5) * VOXEL_SIZE);
                    selectionHighlightMesh.setMatrixAt(i, matrix);
                });
                selectionHighlightMesh.instanceMatrix.needsUpdate = true;
            }
        }

        function updateSelectionUI() {
            const hasSelection = selectedVoxelCoords.size > 0;
            const canApplyMaterial = hasSelection && !!selectedMaterial;
            document.getElementById('delete-selection-btn').disabled = !hasSelection;
            document.getElementById('apply-material-btn').disabled = !canApplyMaterial;
            const partItems = document.querySelectorAll('#model-parts-list li');
            partItems.forEach(item => {
                if (item.dataset.uuid === selectedPartId) {
                    item.classList.add('ring-2', 'ring-yellow-400');
                } else {
                    item.classList.remove('ring-2', 'ring-yellow-400');
                }
            });
        }

        function populateMaterialInventory() {
            const materialGrid = document.getElementById('material-grid');
            const allMaterials = getAllMinecraftMaterials();
            materialGrid.innerHTML = '';
            allMaterials.forEach(material => {
                const button = document.createElement('button');
                button.className = 'p-2 rounded-md text-xs font-medium transition-all bg-gray-700 hover:bg-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500';
                button.textContent = material.name;

                if (!material.isAvailable) {
                    button.classList.add('opacity-40', 'cursor-not-allowed');
                    button.classList.remove('hover:bg-gray-600');
                    button.disabled = true;
                    button.title = '材质包中未找到此贴图';
                }

                button.onclick = () => {
                    if (isAgentRunning) return;
                    selectedMaterial = material;
                    document.querySelectorAll('#material-grid button').forEach(btn => btn.classList.remove('bg-blue-600', 'ring-2', 'ring-blue-300'));
                    button.classList.add('bg-blue-600', 'ring-2', 'ring-blue-300');
                    document.getElementById('material-inventory-btn').textContent = `编辑 (${material.name})`;
                    updateSelectionUI();
                };
                materialGrid.appendChild(button);
            });
        }

        function updateSceneInspector() {
            const listContainer = document.getElementById('model-parts-list');
            listContainer.innerHTML = '';
            if (modelParts.length === 0) {
                listContainer.textContent = '加载模型以查看其部件。';
                return;
            }
            const ul = document.createElement('ul');
            ul.className = 'space-y-1';
            modelParts.forEach(part => {
                const li = document.createElement('li');
                li.dataset.uuid = part.uuid;
                li.className = `w-full text-left flex items-center justify-between p-2 rounded-md text-xs transition-all ${part.visible ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-900 hover:bg-gray-800 text-gray-400'}`;

                const leftSide = document.createElement('div');
                leftSide.className = 'flex-grow flex flex-col items-start truncate';

                const nameSpan = document.createElement('span');
                nameSpan.className = 'truncate cursor-pointer font-semibold text-gray-200';
                nameSpan.textContent = part.name;
                nameSpan.title = `选择 ${part.name} 中的所有体素`;
                nameSpan.onclick = () => {
                    if (isAgentRunning) return;
                    selectPartProgrammatically(part.uuid);
                };

                const tagsContainer = document.createElement('div');
                tagsContainer.className = 'flex items-center space-x-1 mt-1';

                const countTag = document.createElement('span');
                countTag.className = 'text-xs bg-gray-600 text-gray-300 px-1.5 py-0.5 rounded';
                countTag.textContent = `${part.voxelCount || 0} 方块`;
                tagsContainer.appendChild(countTag);

                if (part.isOccluded) {
                    const occludedTag = document.createElement('span');
                    occludedTag.className = 'text-xs bg-red-800 text-red-200 px-1.5 py-0.5 rounded font-semibold';
                    occludedTag.textContent = '不可见';
                    tagsContainer.appendChild(occludedTag);
                }

                leftSide.appendChild(nameSpan);
                leftSide.appendChild(tagsContainer);

                const buttonGroup = document.createElement('div');
                buttonGroup.className = 'flex-shrink-0 flex items-center space-x-2';

                const isolateBtn = document.createElement('button');
                isolateBtn.className = 'bg-transparent border-none p-0 text-gray-400 hover:text-white';
                isolateBtn.title = `仅显示 ${part.name}`;
                isolateBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>`;
                isolateBtn.onclick = () => {
                    if (isAgentRunning) return;
                    if (!loadedModel) return;
                    if (isolateTimer) clearTimeout(isolateTimer);

                    modelParts.forEach(p => {
                        const partObject = loadedModel.getObjectByProperty('uuid', p.uuid);
                        if (partObject) {
                            const shouldBeVisible = p.uuid === part.uuid;
                            partObject.visible = shouldBeVisible;
                            p.visible = shouldBeVisible;
                        }
                    });
                    voxelizeAndDisplay(loadedModel);
                    updateSceneInspector();

                    isolateTimer = setTimeout(unhideAllParts, 5000);
                };

                const visibilityBtn = document.createElement('button');
                visibilityBtn.className = 'bg-transparent border-none p-0 text-gray-400 hover:text-white';
                visibilityBtn.title = `点击以${part.visible ? '隐藏' : '显示'} ${part.name}`;
                visibilityBtn.innerHTML = part.visible ? `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>` : `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7 1.274 4.057 5.064 7 9.542 7 .847 0 1.67.11 2.454.316m5.097 5.097a10.02 10.02 0 01-1.34 2.456M18 12a6 6 0 11-12 0 6 6 0 0112 0z" /><path stroke-linecap="round" stroke-linejoin="round" d="M1 1l22 22" /></svg>`;
                visibilityBtn.onclick = () => {
                    if (isAgentRunning) return;
                    if (!loadedModel) return;
                    if (isolateTimer) {
                        clearTimeout(isolateTimer);
                        isolateTimer = null;
                    }
                    const partObject = loadedModel.getObjectByProperty('uuid', part.uuid);
                    if (partObject) {
                        partObject.visible = !partObject.visible;
                        part.visible = partObject.visible;
                        voxelizeAndDisplay(loadedModel);
                        updateSceneInspector();
                    }
                };

                li.appendChild(leftSide);
                buttonGroup.appendChild(isolateBtn);
                buttonGroup.appendChild(visibilityBtn);
                li.appendChild(buttonGroup);
                ul.appendChild(li);
            });
            listContainer.appendChild(ul);
        }

        // ====================================================================
        // AI Assistant & Agent Functions
        // ====================================================================

        async function handleAiChatSend() {
            const userInput = document.getElementById('ai-user-input');
            const sendBtn = document.getElementById('ai-send-btn');
            const message = userInput.value.trim();

            if (!message || sendBtn.disabled) return;

            addAiChatMessage('user', message);
            userInput.value = '';
            userInput.disabled = true;
            sendBtn.disabled = true;

            const thinkingMsgId = `thinking-${Date.now()}`;
            addAiChatMessage('ai', '思考中...', [], [], thinkingMsgId);

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        apiKey: geminiApiKey,
                        model: currentAiModel
                    })
                });

                const result = await response.json();

                const thinkingBubble = document.getElementById(thinkingMsgId);
                if (thinkingBubble) {
                    thinkingBubble.remove();
                }

                if (!response.ok) {
                    const errorMessage = result.error || `HTTP error! status: ${response.status}`;
                    throw new Error(errorMessage);
                }

                addAiChatMessage('ai', result.reply);

            } catch (error) {
                const thinkingBubble = document.getElementById(thinkingMsgId);
                if (thinkingBubble) {
                    thinkingBubble.remove();
                }
                console.error('AI Chat Error:', error);
                addAiChatMessage('system', `抱歉，与 AI 通信时发生错误: ${error.message}`);
            } finally {
                userInput.disabled = false;
                sendBtn.disabled = false;
                userInput.focus();
            }
        }

        function selectPartProgrammatically(uuid) {
            selectedVoxelCoords.clear();
            voxelProperties.forEach((props, coord) => {
                if (props.partId === uuid) selectedVoxelCoords.add(coord);
            });
            selectedPartId = uuid;
            updateSelectionHighlight();
            updateSelectionUI();
        }

        function addAiChatMessage(sender, text, images = [], actions = [], elementId = null) {
            const chatHistory = document.getElementById('ai-chat-history');
            const msgContainer = document.createElement('div');
            if (elementId) {
                msgContainer.id = elementId;
            }
            const bubbleDiv = document.createElement('div');

            msgContainer.className = `flex flex-col ${sender === 'user' ? 'items-end' : 'items-start'}`;
            bubbleDiv.className = `max-w-[90%] p-2.5 rounded-lg text-sm whitespace-pre-wrap ${
                sender === 'user' ? 'bg-blue-600 text-white' :
                sender === 'ai' ? 'bg-gray-600 text-gray-100' :
                'bg-yellow-600 bg-opacity-50 text-yellow-100 italic'
            }`;

            const validImages = images.filter(Boolean);
            if (validImages.length > 0) {
                const imageContainer = document.createElement('div');
                imageContainer.className = 'mb-2 flex flex-col space-y-1';

                validImages.forEach(imgData => {
                    const img = document.createElement('img');
                    img.src = imgData.src;
                    img.className = "rounded-md w-full h-auto bg-gray-700";

                    const label = document.createElement('span');
                    label.className = "text-xs text-center text-gray-400 font-semibold";
                    label.textContent = imgData.label;

                    const container = document.createElement('div');
                    container.appendChild(img);
                    container.appendChild(label);
                    imageContainer.appendChild(container);
                });
                bubbleDiv.appendChild(imageContainer);
            }

            const textNode = document.createElement('span');
            text = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="font-semibold">$1</strong>');
            text = text.replace(/_reasoning: (.*)_/g, '<br><em class="text-xs text-gray-400 block mt-1">理由: $1</em>');
            textNode.innerHTML = text;
            bubbleDiv.appendChild(textNode);
            msgContainer.appendChild(bubbleDiv);

            if (actions.length > 0) {
                const buttonsContainer = document.createElement('div');
                buttonsContainer.className = 'flex space-x-2 mt-2';
                actions.forEach(action => {
                    const button = document.createElement('button');
                    button.textContent = action.label;
                    button.className = 'bg-blue-600 hover:bg-blue-700 text-white font-medium py-1 px-3 rounded-md text-sm';
                    button.onclick = () => {
                        action.callback();
                        buttonsContainer.remove();
                    };
                    buttonsContainer.appendChild(button);
                });
                msgContainer.appendChild(buttonsContainer);
            }

            chatHistory.appendChild(msgContainer);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }

        function startAiAgent() {
            if (isAgentRunning) return;
            agentCurrentPartIndex = 0;
            agentOverallAnalysis = "";
            isAgentRunning = true;
            isAgentPaused = false;

            document.getElementById('ai-agent-btn').classList.add('hidden');
            document.getElementById('ai-agent-controls').classList.remove('hidden');
            document.getElementById('ai-agent-pause-btn').classList.remove('hidden');
            document.getElementById('ai-agent-continue-btn').classList.add('hidden');
            document.getElementById('ai-send-btn').disabled = true;

            addAiChatMessage('system', `🤖 AI 代理已启动，使用模型 **${currentAiModel}**。`);
            runAiAgentLoop();
        }

        function pauseAiAgent() {
            if (!isAgentRunning || isAgentPaused) return;
            isAgentPaused = true;
            if (agentAbortController) {
                agentAbortController.abort();
            }
            document.getElementById('ai-agent-pause-btn').classList.add('hidden');
            document.getElementById('ai-agent-continue-btn').classList.remove('hidden');
            addAiChatMessage('system', '⏸️ 代理已暂停。点击“继续”以恢复。');
        }

        function continueAiAgent() {
            if (!isAgentRunning || !isAgentPaused) return;
            isAgentPaused = false;
            document.getElementById('ai-agent-pause-btn').classList.remove('hidden');
            document.getElementById('ai-agent-continue-btn').classList.add('hidden');
            addAiChatMessage('system', '▶️ 代理已恢复运行...');
            runAiAgentLoop();
        }

        function stopAiAgent(reason = '用户手动停止') {
            if (!isAgentRunning && !isAgentPaused) return;
             if (agentAbortController) {
                agentAbortController.abort();
            }
            isAgentRunning = false;
            isAgentPaused = false;
            agentCurrentPartIndex = 0;
            agentOverallAnalysis = "";

            document.getElementById('ai-agent-btn').classList.remove('hidden');
            document.getElementById('ai-agent-controls').classList.add('hidden');
            document.getElementById('ai-send-btn').disabled = false;

            addAiChatMessage('system', `⏹️ AI 代理已停止。原因: ${reason}。`);
        }

        async function runAiAgentLoop() {
            try {
                if (agentCurrentPartIndex === 0 && !agentOverallAnalysis) {
                    addAiChatMessage('system', '正在进行初步分析...');
                    const fullModelCollage = await createCollage(['front', 'back', 'left', 'right', 'top', 'bottom']);
                    if (isAgentPaused) return;
                    addAiChatMessage('system', '正在请求 AI 建立总体艺术风格...', [{src: referenceImage, label: "参考图 (艺术风格)"}, {src: fullModelCollage, label: "3D模型 (当前结构)"}]);
                    const analysisPrompt = `您是一位顶级的艺术鉴赏家。请仔细研究“参考图”和“3D模型”。
**您的唯一任务是**: 用一句话捕捉并描述出参考图的**核心感觉**。
这句话应该包含关键的**材质/纹理**和**整体氛围**。
例如：“一个由风化石砖和深色木头构成的古老图书馆，氛围庄严而神秘”，或者“一个由闪亮金属和霓虹灯组成的赛博朋克城市，感觉混乱而充满活力”。
**请只使用以下JSON格式响应**: '{"analysis": "您总结的核心感觉"}'`;
                    const userParts = [ { text: analysisPrompt }, { text: "\\n这是 [参考图 (艺术风格)]:" }, { inlineData: { mimeType: 'image/jpeg', data: referenceImage.split(',')[1] } }, { text: "\\n这是 [3D模型 (当前结构)]:" }, { inlineData: { mimeType: 'image/jpeg', data: fullModelCollage.split(',')[1] } } ];
                    agentAbortController = new AbortController();
                    const analysisResult = await callGeminiAPI(userParts, agentAbortController.signal);
                    agentOverallAnalysis = analysisResult.analysis || "一个标准的 Minecraft 风格建筑";
                    addAiChatMessage('system', `AI 已确立核心感觉: **${agentOverallAnalysis}**`);
                    await sleep(1500);
                    addAiChatMessage('system', '分析完成。现在将根据此方向逐个为部件应用材质...');
                    await sleep(1500);
                }

                const allMaterials = getAllMinecraftMaterials().filter(m => m.isAvailable);
                const materialListString = allMaterials.map(m => `"${m.name}"`).join(', ');
                const visibleParts = modelParts.filter(p => !p.isOccluded && p.voxelCount > 0);
                const materialHistory = [];

                while (agentCurrentPartIndex < visibleParts.length) {
                    if (isAgentPaused) return;
                    const part = visibleParts[agentCurrentPartIndex];
                    addAiChatMessage('system', `处理中 (${agentCurrentPartIndex + 1}/${visibleParts.length}): **${part.name}**`);

                    let isPartCompleted = false;
                    let retryCount = 0;
                    let lastActionResult = null;

                    while (!isPartCompleted && retryCount <= AGENT_MAX_RETRIES_PER_PART) {
                        if (isAgentPaused) return;

                        let actionResult;
                        if (retryCount === 0) {
                            const historyString = materialHistory.length > 0
                                ? `**近期历史**: 您最近的材质选择是：${materialHistory.map(h => `对'${h.partName}'使用了'${h.materialName}'`).join('; ')}。`
                                : ``;

                            const actionPrompt = `您是一位富有灵感的艺术家。
**核心感觉**: "**${agentOverallAnalysis}**"。
**当前焦点**: 名为“**${part.name}**”的部件。
${historyString}
**您的任务**: 基于“核心感觉”和“近期历史”，从“可用材质”列表中选择一个最合适的材质，并解释原因。
**可用材质**: [${materialListString}]
请**只**使用以下JSON格式响应: '{"materialName": "选择的材质名", "reasoning": "您的艺术理由"}'`;

                            const partCollage = await createIsolatedPartCollage(part.uuid);
                            if (isAgentPaused) return;
                            addAiChatMessage('system', `正在为 **${part.name}** 请求材质建议...`, [{src: referenceImage, label: "参考图"}, {src: partCollage, label: `当前部件: ${part.name}`}]);
                            const userParts = [ { text: actionPrompt }, { text: "\\n[参考图]:" }, { inlineData: { mimeType: 'image/jpeg', data: referenceImage.split(',')[1] } }, { text: `\\n[当前部件: ${part.name}]:` }, { inlineData: { mimeType: 'image/jpeg', data: partCollage.split(',')[1] } } ];
                            agentAbortController = new AbortController();
                            actionResult = await callGeminiAPI(userParts, agentAbortController.signal);
                        } else {
                            actionResult = lastActionResult;
                        }

                        const targetMaterial = allMaterials.find(m => m.name.toLowerCase() === actionResult?.materialName?.toLowerCase());
                        if (targetMaterial) {
                            const lastMaterialName = targetMaterial.name;
                            const reasoning = actionResult.reasoning ? `_reasoning: ${actionResult.reasoning}_` : "";
                            addAiChatMessage('ai', `**应用**: 为 **${part.name}** 应用 **${targetMaterial.name}**。${reasoning}`);
                            selectPartProgrammatically(part.uuid);
                            selectedMaterial = targetMaterial;
                            handleApplyMaterialToSelection();
                            await sleep(1500);

                            // 简化审核，信任AI的“感觉”
                            addAiChatMessage('system', `✅ 应用完成`);
                            materialHistory.push({ partName: part.name, materialName: lastMaterialName });
                            if (materialHistory.length > 5) materialHistory.shift();
                            isPartCompleted = true;
                        } else {
                           addAiChatMessage('system', `⚠️ **材质无效**，跳过部件 **${part.name}**...`);
                           isPartCompleted = true;
                        }
                    }
                    if (retryCount > AGENT_MAX_RETRIES_PER_PART) {
                         addAiChatMessage('system', `⚠️ **重试次数过多**，强制继续处理下一个部件...`);
                    }
                    agentCurrentPartIndex++;
                }
                stopAiAgent('任务完成');
            } catch (error) {
                 if (error.name === 'AbortError') {
                     console.log('Agent fetch aborted by user control.');
                 } else {
                     addAiChatMessage('system', `代理在执行过程中遇到错误: ${error.message}`);
                     stopAiAgent('执行出错');
                 }
            }
        }

        async function createIsolatedPartCollage(partUuid) {
            voxelContainerGroup.visible = false;
            selectionHighlightMesh.visible = false;
            const isolatedGroup = new THREE.Group();
            const materialToInstancesMap = new Map();
            voxelProperties.forEach((props, coordString) => {
                if (props.partId === partUuid) {
                    const textureKey = getTextureKeyForVoxel(props.blockId, props.metaData, DEFAULT_BLOCK_ID_LIST);
                    if (!materialToInstancesMap.has(textureKey)) materialToInstancesMap.set(textureKey, []);
                    const [x, y, z] = coordString.split(',').map(Number);
                    const halfGrid = GRID_SIZE / 2;
                    const posX = -halfGrid + (x + 0.5) * VOXEL_SIZE;
                    const posY = (y + 0.5) * VOXEL_SIZE;
                    const posZ = -halfGrid + (z + 0.5) * VOXEL_SIZE;
                    materialToInstancesMap.get(textureKey).push({ matrix: new THREE.Matrix4().setPosition(posX, posY, posZ) });
                }
            });
            const baseVoxelGeometry = new THREE.BoxGeometry(VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98);
            materialToInstancesMap.forEach((instances, textureKey) => {
                const texture = loadedTextures.get(textureKey);
                const material = texture ? new THREE.MeshStandardMaterial({ map: texture }) : new THREE.MeshLambertMaterial({ color: TEXTURE_KEY_TO_COLOR_MAP[textureKey] || 0xff00ff });
                const instancedMesh = new THREE.InstancedMesh(baseVoxelGeometry, material, instances.length);
                instancedMesh.castShadow = true;
                instances.forEach((d, i) => instancedMesh.setMatrixAt(i, d.matrix));
                instancedMesh.instanceMatrix.needsUpdate = true;
                isolatedGroup.add(instancedMesh);
            });
            scene.add(isolatedGroup);
            const partCollage = await createCollage(['front', 'back', 'left', 'right', 'top', 'bottom']);
            scene.remove(isolatedGroup);
            isolatedGroup.children.forEach(c => { c.geometry.dispose(); if(Array.isArray(c.material)) c.material.forEach(m=>m.dispose()); else c.material.dispose(); });
            voxelContainerGroup.visible = true;
            selectionHighlightMesh.visible = true;
            renderer.render(scene, camera);
            return partCollage;
        }

        async function callGeminiAPI(userParts, signal) {
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${currentAiModel}:generateContent?key=${geminiApiKey}`;
            const payload = { contents: [{ role: "user", parts: userParts }], generationConfig: { responseMimeType: "application/json" } };
            const response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: signal });
            if (!response.ok) {
                const errorText = await response.text();
                console.error("API Error Response:", errorText);
                throw new Error(`API 调用失败: ${response.status} ${response.statusText}`);
            }
            const result = await response.json();
            if(!result.candidates || !result.candidates[0].content?.parts?.[0]?.text){
                console.error("Invalid API response structure:", result);
                throw new Error("API返回了无效的数据结构。");
            }
            try {
                 return JSON.parse(result.candidates[0].content.parts[0].text);
            } catch (e) {
                 console.error("Failed to parse JSON from AI response:", result.candidates[0].content.parts[0].text);
                 throw new Error("AI返回了非法的JSON格式。");
            }
        }

        // ====================================================================
        // State Persistence
        // ====================================================================

        function saveAppStateToLocalStorage() {
            if (voxelProperties.size === 0) {
                localStorage.removeItem('appState');
                console.log("No voxel data to save, cleared localStorage.");
                return;
            }

            const appState = {
                voxelProperties: Object.fromEntries(voxelProperties),
                modelParts: modelParts,
                timestamp: new Date().toISOString()
            };

            try {
                localStorage.setItem('appState', JSON.stringify(appState));
                console.log(`App state saved to localStorage at ${appState.timestamp}`);
            } catch (e) {
                console.error("Error saving state to localStorage:", e);
                // 尝试清除旧的存储并重试
                localStorage.removeItem('appState');
                try {
                    localStorage.setItem('appState', JSON.stringify(appState));
                    console.log("Cleared old state and successfully saved app state.");
                } catch (e2) {
                    console.error("Failed to save state even after clearing:", e2);
                }
            }
        }

        function loadAppStateFromLocalStorage() {
            const savedStateJSON = localStorage.getItem('appState');
            if (!savedStateJSON) {
                console.log("No saved state found in localStorage.");
                return false;
            }

            try {
                const savedState = JSON.parse(savedStateJSON);
                console.log(`Found saved state from ${savedState.timestamp}`);

                // 恢复 Voxel 数据
                voxelProperties.clear();
                currentVoxelCoords.clear();

                const savedVoxelProps = savedState.voxelProperties || {};
                for (const coordString in savedVoxelProps) {
                    if (Object.hasOwnProperty.call(savedVoxelProps, coordString)) {
                        currentVoxelCoords.add(coordString);
                        voxelProperties.set(coordString, savedVoxelProps[coordString]);
                    }
                }

                // 恢复模型部件
                modelParts = savedState.modelParts || [];

                if (currentVoxelCoords.size > 0) {
                    // 模拟一个已加载的模型以启用依赖于它的功能
                    if (!loadedModel) {
                        loadedModel = new THREE.Group();
                        loadedModel.name = "Restored from LocalStorage";
                    }
                    displayVoxels();
                    updateSceneInspector();
                    updateAgentButtonState();
                    addAiChatMessage('system', `✅ 成功从浏览器缓存恢复了您上次的编辑。`);
                    return true;
                }
                return false;

            } catch (e) {
                console.error("Error loading state from localStorage:", e);
                localStorage.removeItem('appState'); // 清除损坏的数据
                return false;
            }
        }

        // ====================================================================
        // Initial Setup and Event Binding
        // ====================================================================

        function unlockUI() {
            const mainContainer = document.getElementById('main-container');
            const apiKeyModal = document.getElementById('api-key-modal');

            apiKeyModal.classList.add('hidden');
            mainContainer.classList.remove('opacity-20', 'pointer-events-none');

            document.querySelectorAll('button, input, textarea').forEach(el => {
                el.disabled = false;
            });
            // Re-disable buttons that should be initially disabled
            updateAgentButtonState();
            updateSelectionUI();
        }

        async function initializeApp() {
            console.log("Initializing application...");
            init(); // Init 3D scene & UI bindings

            // --- 智能加载顺序 ---
            // 1. 优先从命令行传入的存档文件加载
            if (window.initialSaveData) {
                console.log("Applying initial save data from command line...");
                await applySaveData(window.initialSaveData);
                 // 加载后，加载任何非模型的辅助文件（如材质包）
                await loadInitialFilesFromServer(true); // skipModel=true
                console.log("Initialization complete (loaded from save file).");
                return;
            }

            // 2. 其次，尝试从浏览器本地存储恢复
            const loadedFromStorage = loadAppStateFromLocalStorage();
            if (loadedFromStorage) {
                // 加载后，加载任何非模型的辅助文件（如材质包）
                await loadInitialFilesFromServer(true); // skipModel=true
                console.log("Initialization complete (restored from localStorage).");
                return;
            }

            // 3. 最后，如果都没有，则从 input 文件夹加载默认模型
            console.log("No save data or local state found, loading default files...");
            await loadInitialFilesFromServer(false); // skipModel=false
            console.log("Application initialization complete (loaded default files).");
        }

        async function handleApiKeyValidation() {
            const modalInput = document.getElementById('modal-api-key-input');
            const errorMsg = document.getElementById('api-key-error-msg');
            const validateBtn = document.getElementById('validate-api-key-btn');
            const btnText = document.getElementById('validate-btn-text');
            const btnSpinner = document.getElementById('validate-btn-spinner');

            const key = modalInput.value;
            if (!key) {
                errorMsg.textContent = 'API 密钥不能为空。';
                return;
            }

            validateBtn.disabled = true;
            btnText.classList.add('hidden');
            btnSpinner.classList.remove('hidden');
            errorMsg.textContent = '';

            try {
                const response = await fetch('/api/validate_key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ apiKey: key })
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    geminiApiKey = key;
                    localStorage.setItem('geminiApiKey', key);
                    document.getElementById('api-key-input').value = key;
                    unlockUI();
                    initializeApp(); // Centralized initialization
                } else {
                    errorMsg.textContent = result.message || '验证失败，请重试。';
                }
            } catch (error) {
                console.error('Validation fetch error:', error);
                errorMsg.textContent = '无法连接到服务器进行验证。';
            } finally {
                validateBtn.disabled = false;
                btnText.classList.remove('hidden');
                btnSpinner.classList.add('hidden');
            }
        }


        document.addEventListener('DOMContentLoaded', () => {
            // 首先检查密钥是否已在服务器端预先验证
            if (window.isKeyPreValidated && window.apiKeyFromFile) {
                console.log("Key was pre-validated on server. Unlocking UI.");
                geminiApiKey = window.apiKeyFromFile;
                localStorage.setItem('geminiApiKey', geminiApiKey); // Store the valid key
                document.getElementById('api-key-input').value = geminiApiKey;
                unlockUI();
                initializeApp(); // Use centralized init
            } else {
                // 如果没有预先验证的密钥，则回退到手动输入流程
                console.log("No pre-validated key. Starting manual validation flow.");
                const validateBtn = document.getElementById('validate-api-key-btn');
                const modalInput = document.getElementById('modal-api-key-input');

                validateBtn.addEventListener('click', handleApiKeyValidation);
                modalInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        handleApiKeyValidation();
                    }
                });

                // 自动验证存储在 localStorage 中的密钥
                const storedKey = localStorage.getItem('geminiApiKey');
                 if (storedKey) {
                    modalInput.value = storedKey;
                    handleApiKeyValidation(); // This will now call initializeApp on success
                } else if (window.initialSaveData) {
                    // This case handles when there's save data but no API key yet.
                    // We can unlock the UI to show the model, but AI features will wait for a key.
                    console.log("Initial save data found, but no API key. Unlocking UI to show model.");
                    unlockUI();
                    init();
                    applySaveData(window.initialSaveData);
                    // AI features will remain locked until a key is entered manually.
                }
            }

            // --- 其他事件监听器 ---
            const modelNameDisplay = document.getElementById('ai-model-name-display');
            modelNameDisplay.textContent = currentAiModel;
            document.getElementById('ai-model-toggle-btn').addEventListener('click', () => {
                if(isAgentRunning || isAgentPaused) return;
                currentAiModel = currentAiModel === FLASH_MODEL_NAME ? PRO_MODEL_NAME : FLASH_MODEL_NAME;
                modelNameDisplay.textContent = currentAiModel;
                addAiChatMessage('system', `AI 模型已切换为 **${currentAiModel}**。`);
            });

            const toggleInspectorBtn = document.getElementById('toggle-inspector-btn');
            const modelPartsList = document.getElementById('model-parts-list');
            const chevronUp = document.getElementById('inspector-chevron-up');
            const chevronDown = document.getElementById('inspector-chevron-down');
            toggleInspectorBtn.addEventListener('click', () => {
                modelPartsList.classList.toggle('hidden');
                chevronUp.classList.toggle('hidden');
                chevronDown.classList.toggle('hidden');
            });
            document.getElementById('modelInput').addEventListener('change', handleModelLoad);
            document.getElementById('texturePackInput').addEventListener('change', handleTexturePackLoad);
            document.getElementById('reference-image-input').addEventListener('change', handleReferenceImageLoad);
            document.getElementById('view-front').addEventListener('click', () => setCameraView('front'));
            document.getElementById('view-back').addEventListener('click', () => setCameraView('back'));
            document.getElementById('view-left').addEventListener('click', () => setCameraView('left'));
            document.getElementById('view-right').addEventListener('click', () => setCameraView('right'));
            document.getElementById('view-top').addEventListener('click', () => setCameraView('top'));
            document.getElementById('view-bottom').addEventListener('click', () => setCameraView('bottom'));
            document.getElementById('screenshot-btn').addEventListener('click', handleScreenshot);
            document.getElementById('multi-screenshot-btn').addEventListener('click', handleMultiViewScreenshot);
            document.getElementById('export-txt-btn').addEventListener('click', handleExportToTxt);
            document.getElementById('delete-selection-btn').addEventListener('click', handleDeleteSelection);
            document.getElementById('apply-material-btn').addEventListener('click', handleApplyMaterialToSelection);
            const materialPanel = document.getElementById('material-inventory-panel');
            document.getElementById('material-inventory-btn').addEventListener('click', () => materialPanel.classList.remove('hidden'));
            document.getElementById('close-material-panel-btn').addEventListener('click', () => materialPanel.classList.add('hidden'));
            materialPanel.addEventListener('click', (e) => { if (e.target === materialPanel) materialPanel.classList.add('hidden'); });
            const aiPanel = document.getElementById('ai-assistant-panel');
            document.getElementById('ai-assistant-btn').addEventListener('click', () => aiPanel.classList.toggle('hidden'));
            document.getElementById('ai-panel-close-btn').addEventListener('click', () => aiPanel.classList.add('hidden'));
            document.getElementById('ai-clear-chat-btn').addEventListener('click', () => {
                document.getElementById('ai-chat-history').innerHTML = '';
                 addAiChatMessage('system', '欢迎！请按左上角的步骤加载模型、材质和参考图以开始。');
            });
            document.getElementById('ai-send-btn').addEventListener('click', handleAiChatSend);
            document.getElementById('ai-user-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleAiChatSend();
                }
            });
            document.getElementById('ai-agent-btn').addEventListener('click', startAiAgent);
            document.getElementById('ai-agent-pause-btn').addEventListener('click', pauseAiAgent);
            document.getElementById('ai-agent-continue-btn').addEventListener('click', continueAiAgent);
            document.getElementById('ai-agent-stop-btn').addEventListener('click', () => stopAiAgent('用户手动停止'));
            const apiKeyPopup = document.getElementById('api-key-popup');
            document.getElementById('api-key-manager-btn').addEventListener('click', () => apiKeyPopup.classList.toggle('hidden'));
            document.getElementById('api-key-save').addEventListener('click', () => {
                geminiApiKey = document.getElementById('api-key-input').value;
                localStorage.setItem('geminiApiKey', geminiApiKey);
                apiKeyPopup.classList.add('hidden');
                addAiChatMessage('system', 'API 密钥已保存。');
            });
            document.getElementById('api-key-cancel').addEventListener('click', () => apiKeyPopup.classList.add('hidden'));
            
            // --- 存档功能事件监听器 ---
            document.getElementById('export-save-btn').addEventListener('click', handleExportSave);
            document.getElementById('import-save-btn').addEventListener('click', () => {
                document.getElementById('import-save-input').click();
            });
            document.getElementById('import-save-input').addEventListener('change', handleImportSave);
            document.getElementById('import-url-btn').addEventListener('click', handleImportFromUrl);
            document.getElementById('play-animation-btn').addEventListener('click', playFallingAnimation);
        });

        // --- 存档功能函数 ---
        
        function getCurrentVoxelData() {
            const voxelData = {};
            voxelProperties.forEach((props, coordString) => {
                voxelData[coordString] = props;
            });
            return voxelData;
        }

        function getCurrentChatHistory() {
            const chatMessages = [];
            const chatHistory = document.getElementById('ai-chat-history');
            if (chatHistory) {
                const messages = chatHistory.querySelectorAll('div[class*="flex"]');
                messages.forEach(msg => {
                    const text = msg.textContent || '';
                    if (text.trim()) {
                        chatMessages.push({
                            content: text.trim(),
                            timestamp: new Date().toISOString()
                        });
                    }
                });
            }
            return chatMessages;
        }

        function getCurrentAgentState() {
            return {
                is_running: isAgentRunning,
                is_paused: isAgentPaused,
                current_part_index: agentCurrentPartIndex,
                overall_analysis: agentOverallAnalysis,
                model_name: currentAiModel
            };
        }

        async function handleExportSave() {
            try {
                const voxelData = getCurrentVoxelData();
                const chatHistory = getCurrentChatHistory();
                const agentState = getCurrentAgentState();

                const response = await fetch('/api/save/export', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        voxelData: voxelData,
                        chatHistory: chatHistory,
                        agentState: agentState
                    })
                });

                if (response.ok) {
                    // 触发文件下载
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = response.headers.get('Content-Disposition')?.split('filename=')[1] || 'mine_builder_save.zip';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                    addAiChatMessage('system', '✅ 存档导出成功！');
                } else {
                    const result = await response.json();
                    throw new Error(result.message || '导出失败');
                }
            } catch (error) {
                console.error('Export save error:', error);
                addAiChatMessage('system', `❌ 导出存档失败: ${error.message}`);
            }
        }

        async function handleImportSave(event) {
            const file = event.target.files?.[0];
            if (!file) return;

            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/save/import', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    await applySaveData(result.data);
                    addAiChatMessage('system', '✅ 存档导入成功！');
                } else {
                    throw new Error(result.message || '导入失败');
                }
            } catch (error) {
                console.error('Import save error:', error);
                addAiChatMessage('system', `❌ 导入存档失败: ${error.message}`);
            }

            // 清空文件输入
            event.target.value = '';
        }

        async function handleImportFromUrl() {
            const urlInput = document.getElementById('save-url-input');
            const url = urlInput.value.trim();
            
            if (!url) {
                addAiChatMessage('system', '请输入存档URL');
                return;
            }

            try {
                const response = await fetch('/api/save/import', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    await applySaveData(result.data);
                    addAiChatMessage('system', '✅ 从URL导入存档成功！');
                    urlInput.value = '';
                } else {
                    throw new Error(result.message || '导入失败');
                }
            } catch (error) {
                console.error('Import from URL error:', error);
                addAiChatMessage('system', `❌ 从URL导入存档失败: ${error.message}`);
            }
        }

        async function playFallingAnimation() {
            if (currentVoxelCoords.size === 0) return;

            const playBtn = document.getElementById('play-animation-btn');
            playBtn.disabled = true;
            playBtn.textContent = '播放中...';

            // Hide the main voxel group
            voxelContainerGroup.visible = false;

            const voxels = Array.from(currentVoxelCoords).map(coordString => {
                const [x, y, z] = coordString.split(',').map(Number);
                const props = voxelProperties.get(coordString) || DEFAULT_VOXEL_PROPERTIES;
                return { x, y, z, props };
            });

            // Sort voxels from bottom to top, then by x, then by z
            voxels.sort((a, b) => a.y - b.y || a.x - b.x || a.z - b.z);

            const animationGroup = new THREE.Group();
            scene.add(animationGroup);

            const baseVoxelGeometry = new THREE.BoxGeometry(VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98, VOXEL_SIZE * 0.98);

            const speedSlider = document.getElementById('animation-speed-slider');
            const maxDelay = 200; // Corresponds to speed 1
            const minDelay = 5;   // Corresponds to speed 100
            const speedValue = parseInt(speedSlider.value, 10);
            // Inverse mapping: lower slider value means higher delay
            const delayBetweenVoxels = maxDelay - ((speedValue - 1) / 99) * (maxDelay - minDelay);


            for (let i = 0; i < voxels.length; i++) {
                const voxel = voxels[i];
                const halfGrid = GRID_SIZE / 2;
                const targetX = -halfGrid + (voxel.x + 0.5) * VOXEL_SIZE;
                const targetY = (voxel.y + 0.5) * VOXEL_SIZE;
                const targetZ = -halfGrid + (voxel.z + 0.5) * VOXEL_SIZE;
                const startY = GRID_SIZE * 1.5;

                const textureKey = getTextureKeyForVoxel(voxel.props.blockId, voxel.props.metaData, DEFAULT_BLOCK_ID_LIST);
                const texture = loadedTextures.get(textureKey);
                const material = texture ?
                    new THREE.MeshStandardMaterial({ map: texture, metalness: 0.1, roughness: 0.8 }) :
                    new THREE.MeshLambertMaterial({ color: TEXTURE_KEY_TO_COLOR_MAP[textureKey] || 0xff00ff });

                const mesh = new THREE.Mesh(baseVoxelGeometry, material);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                mesh.position.set(targetX, startY, targetZ);
                animationGroup.add(mesh);

                // Animate the fall
                setTimeout(() => {
                    const fallDuration = 500 + Math.random() * 300; // Duration of fall in ms
                    const startTime = Date.now();

                    function animateFall() {
                        const elapsedTime = Date.now() - startTime;
                        let t = elapsedTime / fallDuration;
                        t = t < 1 ? t : 1; // Clamp t to 1

                        // Ease-out cubic interpolation
                        const easedT = 1 - Math.pow(1 - t, 3);

                        mesh.position.y = startY * (1 - easedT) + targetY * easedT;

                        if (t < 1) {
                            requestAnimationFrame(animateFall);
                        } else {
                            mesh.position.y = targetY; // Ensure it lands exactly
                        }
                    }
                    animateFall();
                }, i * delayBetweenVoxels);
            }

            // Cleanup after animation completes
            setTimeout(() => {
                scene.remove(animationGroup);
                animationGroup.children.forEach(child => {
                    child.geometry.dispose();
                    if (Array.isArray(child.material)) {
                        child.material.forEach(m => m.dispose());
                    } else {
                        child.material.dispose();
                    }
                });
                voxelContainerGroup.visible = true;
                playBtn.disabled = false;
                playBtn.textContent = '播放动画';
            }, voxels.length * delayBetweenVoxels + 1000); // Wait for all animations to finish + buffer
        }

        async function applySaveData(saveData) {
            try {
                // 恢复体素数据
                if (saveData.voxel_data && Object.keys(saveData.voxel_data).length > 0) {
                    currentVoxelCoords.clear();
                    voxelProperties.clear();
                    
                    Object.entries(saveData.voxel_data).forEach(([coordString, props]) => {
                        currentVoxelCoords.add(coordString);
                        voxelProperties.set(coordString, props);
                    });

                    // 关键修复：当从存档加载时，我们没有真实的GLTF模型。
                    // 我们需要模拟一个已加载的模型，以解锁依赖于它的UI功能（例如AI代理）。
                    if (!loadedModel) {
                        loadedModel = new THREE.Group(); // 使用一个空的Group作为占位符
                        loadedModel.name = "Loaded from Save";
                         addAiChatMessage('system', `从存档恢复了体素模型。AI功能已解锁。`);
                    }
                    
                    displayVoxels();
                    updateAgentButtonState(); // 确保在模型“加载”后更新按钮状态
                }

                // 恢复AI聊天记录
                if (saveData.chat_history && Array.isArray(saveData.chat_history)) {
                    const chatHistory = document.getElementById('ai-chat-history');
                    if (chatHistory) {
                        chatHistory.innerHTML = '';
                        saveData.chat_history.forEach(msg => {
                            if (msg.content) {
                                addAiChatMessage('system', `[已恢复] ${msg.content}`);
                            }
                        });
                    }
                }

                // 恢复AI代理状态
                if (saveData.agent_state) {
                    isAgentRunning = saveData.agent_state.is_running || false;
                    isAgentPaused = saveData.agent_state.is_paused || false;
                    agentCurrentPartIndex = saveData.agent_state.current_part_index || 0;
                    agentOverallAnalysis = saveData.agent_state.overall_analysis || '';
                    currentAiModel = saveData.agent_state.model_name || FLASH_MODEL_NAME;
                    
                    // 更新UI状态
                    document.getElementById('ai-model-name-display').textContent = currentAiModel;
                    
                    if (isAgentRunning || isAgentPaused) {
                        document.getElementById('ai-agent-btn').classList.add('hidden');
                        document.getElementById('ai-agent-controls').classList.remove('hidden');
                        
                        if (isAgentPaused) {
                            document.getElementById('ai-agent-pause-btn').classList.add('hidden');
                            document.getElementById('ai-agent-continue-btn').classList.remove('hidden');
                        } else {
                            document.getElementById('ai-agent-pause-btn').classList.remove('hidden');
                            document.getElementById('ai-agent-continue-btn').classList.add('hidden');
                        }
                    }
                }

                addAiChatMessage('system', `📁 存档数据已成功恢复 (版本: ${saveData.version || '未知'})`);
                saveAppStateToLocalStorage(); // 保存状态
            } catch (error) {
                console.error('Apply save data error:', error);
                addAiChatMessage('system', `❌ 应用存档数据时出错: ${error.message}`);
            }
        }

    </script>
</body>
</html>
"""

# --- Flask 路由 ---
@app.route('/')
def index():
    """提供主HTML页面内容。"""
    # 将服务器端验证的密钥和状态传递给前端模板
    return render_template_string(
        HTML_CONTENT,
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
