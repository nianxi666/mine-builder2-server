"""
存档管理模块 - 处理游戏存档的导出和导入
"""
import os
import json
import datetime
import tempfile
import zipfile
import logging
import requests
import shutil


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


def export_save_file(save_data, save_dir="saves"):
    """导出存档文件为zip格式"""
    # 确保存档目录存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    temp_dir = tempfile.mkdtemp()
    try:
        # 创建存档数据JSON文件
        save_json_path = os.path.join(temp_dir, "save_data.json")
        with open(save_json_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # 创建zip文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"mine_builder_save_{timestamp}.zip"
        zip_path = os.path.join(save_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(save_json_path, "save_data.json")
        
        return zip_path
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def import_save_file(zip_path_or_url):
    """导入存档文件"""
    try:
        # 如果是URL，先下载
        if zip_path_or_url.startswith(('http://', 'https://')):
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
