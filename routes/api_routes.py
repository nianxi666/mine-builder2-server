"""
API路由模块 - 处理所有API端点
"""
import os
import logging
import tempfile
import requests
from flask import jsonify, request, send_file
import mimetypes

import config
from utils.file_utils import find_first_file, read_file_as_base64
from utils.save_manager import create_save_data, export_save_file, import_save_file
from utils.api_validator import validate_api_key


def register_api_routes(app):
    """注册所有API路由"""
    
    @app.route('/api/files')
    def get_initial_files():
        """API端点，用于扫描并提供初始的模型、材质和参考文件。"""
        logging.info("收到自动加载文件的请求...")

        # 1. 查找材质包 (.zip in current directory)
        texture_path = find_first_file('.', ['.zip'])

        # 2. 查找模型
        # 优先使用通过命令行参数提供的模型
        model_path = None
        if config.DOWNLOADED_MODEL_PATH:
            model_path = config.DOWNLOADED_MODEL_PATH
            logging.info(f"使用命令行提供的模型: {model_path}")
        else:
            # 否则，在 'input' 目录中查找
            model_path = find_first_file(config.INPUT_DIR, ['.glb', '.gltf'])

        # 3. 查找参考图 (in INPUT_DIR)
        ref_image_path = find_first_file(config.INPUT_DIR, ['.png', '.jpg', '.jpeg', '.webp', '.gif'])

        def prepare_file_data(path, default_mime='application/octet-stream'):
            """辅助函数，准备要发送到前端的文件数据。"""
            if not path:
                return None
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
        model = data.get('model', 'gemini-pro')  # Default to gemini-pro if not provided

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
    def validate_api_key_route():
        """API 端点，用于验证前端发送的 Gemini API 密钥。"""
        data = request.get_json()
        api_key = data.get('apiKey')

        if not api_key:
            return jsonify({"success": False, "message": "未提供 API 密钥。"}), 400

        if validate_api_key(api_key):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "API 密钥无效或已过期。"}), 401

    # --- 存档相关API路由 ---

    @app.route('/api/save/export', methods=['POST'])
    def export_save():
        """导出存档文件API"""
        try:
            data = request.get_json()
            voxel_data = data.get('voxelData', {})
            chat_history = data.get('chatHistory', [])
            agent_state = data.get('agentState', config.AGENT_STATE)
            
            # 更新全局状态
            config.CHAT_HISTORY = chat_history
            config.AGENT_STATE.update(agent_state)
            
            # 创建存档数据
            save_data = create_save_data(voxel_data, chat_history, agent_state)
            
            # 导出为zip文件
            zip_path = export_save_file(save_data, config.SAVE_DIR)
            
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
                config.CHAT_HISTORY = save_data.get('chat_history', [])
                config.AGENT_STATE.update(save_data.get('agent_state', {}))
                
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
            config.AGENT_STATE['is_paused'] = True
            config.AGENT_STATE['is_running'] = False
            logging.info("AI代理已暂停")
            return jsonify({"success": True, "message": "AI代理已暂停"})
        except Exception as e:
            logging.error(f"暂停AI代理时发生错误: {e}")
            return jsonify({"success": False, "message": f"暂停失败: {str(e)}"}), 500

    @app.route('/api/agent/continue', methods=['POST'])
    def continue_agent():
        """继续AI代理API"""
        try:
            config.AGENT_STATE['is_paused'] = False
            config.AGENT_STATE['is_running'] = True
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
                "state": config.AGENT_STATE,
                "chat_history": config.CHAT_HISTORY
            })
        except Exception as e:
            logging.error(f"获取AI代理状态时发生错误: {e}")
            return jsonify({"success": False, "message": f"获取状态失败: {str(e)}"}), 500
