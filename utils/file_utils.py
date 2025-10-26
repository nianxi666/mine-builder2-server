"""
文件工具模块 - 文件查找和读取功能
"""
import os
import base64
import logging


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
