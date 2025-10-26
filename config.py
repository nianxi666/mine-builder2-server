"""
配置文件 - 存储应用程序常量和全局状态
"""

# --- 配置常量 ---
PORT = 5000
INPUT_DIR = "input"
CACHE_DIR = "cache"
SAVE_DIR = "saves"  # 存档目录

# --- 全局状态变量 ---
API_KEY_FROM_FILE = None  # 用于存储从 key.txt 读取的密钥
API_KEY_VALIDATED = False  # 标记来自文件的密钥是否已验证成功
DOWNLOADED_MODEL_PATH = None  # 用于存储从URL下载的模型路径

# 全局变量保存AI聊天记录和状态
CHAT_HISTORY = []
AGENT_STATE = {
    "is_running": False,
    "is_paused": False,
    "current_part_index": 0,
    "overall_analysis": "",
    "model_name": "gemini-2.5-flash"
}
INITIAL_SAVE_DATA = None  # 用于存储从 --input_data 加载的存档
