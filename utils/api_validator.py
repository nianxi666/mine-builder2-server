"""
API密钥验证模块
"""
import logging
import requests


def validate_api_key(api_key):
    """验证 Gemini API 密钥是否有效"""
    if not api_key:
        return False
    
    validation_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(validation_url, timeout=5)
        if response.status_code == 200:
            logging.info("API 密钥验证成功。")
            return True
        else:
            logging.warning(f"API 密钥验证失败。状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"验证 API 密钥时发生网络错误: {e}")
        return False
