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
from flask import Flask, jsonify, Response, request, render_template, send_from_directory, send_file

# --- Configurations ---
PORT = 5000
INPUT_DIR = "input"
CACHE_DIR = "cache"
SAVE_DIR = "saves"  # Directory for saves
API_KEY_FROM_FILE = None # To store the key read from key.txt
API_KEY_VALIDATED = False # To mark if the key from the file has been successfully validated
DOWNLOADED_MODEL_PATH = None # To store the path of the model downloaded from a URL

# Global variables to save AI chat history and state
CHAT_HISTORY = []
AGENT_STATE = {
    "is_running": False,
    "is_paused": False,
    "current_part_index": 0,
    "overall_analysis": "",
    "model_name": "gemini-1.5-flash"
}
INITIAL_SAVE_DATA = None # To store the save loaded from --input_data


# --- Logging Setup ---
# Configure logging, all logs will be output to the terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SERVER] - %(levelname)s - %(message)s')

# --- Flask App Initialization ---
app = Flask(__name__, template_folder='templates', static_folder='static')
# Disable Flask's default startup message to keep the terminal output clean
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# --- Backend Core Functions ---

def find_first_file(directory, extensions):
    """Find the first file in the specified directory with the given extensions."""
    if not os.path.isdir(directory):
        logging.warning(f"Directory '{directory}' does not exist.")
        return None
    logging.info(f"Scanning directory '{directory}' for file types: {extensions}")
    # Sort files to ensure consistent results on each run
    for filename in sorted(os.listdir(directory)):
        if any(filename.lower().endswith(ext) for ext in extensions):
            path = os.path.join(directory, filename)
            logging.info(f"Found file: {path}")
            return path
    logging.warning(f"No file of type {extensions} found in '{directory}'.")
    return None

def read_file_as_base64(filepath):
    """Read a file and return its content as a Base64 encoded string."""
    if not filepath or not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Could not read file {filepath}: {e}")
        return None

# --- Save/Load Functions ---

def create_save_data(voxel_data=None, chat_history=None, agent_state=None):
    """Create the save data structure"""
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
            "model_name": "gemini-1.5-flash"
        }
    }
    return save_data

def export_save_file(save_data):
    """Export the save file in zip format"""
    temp_dir = tempfile.mkdtemp()
    try:
        # Create the save data JSON file
        save_json_path = os.path.join(temp_dir, "save_data.json")
        with open(save_json_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        # Create the zip file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"mine_builder_save_{timestamp}.zip"
        zip_path = os.path.join(SAVE_DIR, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(save_json_path, "save_data.json")

        return zip_path
    finally:
        # Clean up the temporary directory
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

def import_save_file(zip_path_or_url):
    """Import the save file"""
    try:
        # If it's a URL, download it first
        if zip_path_or_url.startswith(('http://', 'https://')):
            import requests
            response = requests.get(zip_path_or_url)
            response.raise_for_status()

            # Save to a temporary file
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_zip.write(response.content)
            temp_zip.close()
            zip_path = temp_zip.name
        else:
            zip_path = zip_path_or_url

        # Unzip and read the save data
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            with zipf.open('save_data.json') as f:
                save_data = json.load(f)

        # If it's a temporary file, clean up
        if zip_path_or_url.startswith(('http://', 'https://')):
            os.unlink(zip_path)

        return save_data
    except Exception as e:
        logging.error(f"Failed to import save: {e}")
        return None

# --- Flask Routes ---
@app.route('/')
def index():
    """Serve the main HTML page."""
    # Pass server-side validated key and state to the frontend template
    return render_template(
        'index.html',
        api_key_from_file=API_KEY_FROM_FILE if API_KEY_VALIDATED else '',
        is_key_pre_validated=API_KEY_VALIDATED,
        initial_save_data=INITIAL_SAVE_DATA
    )

@app.route('/api/files')
def get_initial_files():
    """API endpoint to scan and provide initial model, texture, and reference files."""
    logging.info("Request received to auto-load files...")

    # 1. Find texture pack (.zip in current directory)
    texture_path = find_first_file('.', ['.zip'])

    # 2. Find model
    # Prioritize the model provided via command-line argument
    model_path = None
    if DOWNLOADED_MODEL_PATH:
        model_path = DOWNLOADED_MODEL_PATH
        logging.info(f"Using model provided via command line: {model_path}")
    else:
        # Otherwise, look in the 'input' directory
        model_path = find_first_file(INPUT_DIR, ['.glb', '.gltf'])

    # 3. Find reference image (in INPUT_DIR)
    ref_image_path = find_first_file(INPUT_DIR, ['.png', '.jpg', '.jpeg', '.webp', '.gif'])

    def prepare_file_data(path, default_mime='application/octet-stream'):
        """Helper function to prepare file data to be sent to the frontend."""
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

    # Filter out files that were not found before sending
    final_response = {k: v for k, v in response_data.items() if v and v.get('data')}

    logging.info(f"File scan complete. Results: Model={'Found' if 'model' in final_response else 'Not found'}, "
                 f"Texture Pack={'Found' if 'texture' in final_response else 'Not found'}, "
                 f"Reference Image={'Found' if 'reference' in final_response else 'Not found'}.")

    return jsonify(final_response)

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """API endpoint to handle chat messages from the frontend."""
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
    """API endpoint to validate the Gemini API key sent from the frontend."""
    data = request.get_json()
    api_key = data.get('apiKey')

    if not api_key:
        return jsonify({"success": False, "message": "API key not provided."}), 400

    # Use a lightweight API call to validate the key, e.g., list models
    validation_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

    try:
        response = requests.get(validation_url)
        if response.status_code == 200:
            # Even an empty list of models indicates a valid key
            logging.info("API key validation successful.")
            return jsonify({"success": True})
        else:
            # The API returned an error, indicating an invalid key or other issue
            logging.warning(f"API key validation failed. Status code: {response.status_code}, Response: {response.text}")
            return jsonify({"success": False, "message": "API key is invalid or has expired."}), 401
    except requests.exceptions.RequestException as e:
        # Network issues or other request errors
        logging.error(f"Network error while validating API key: {e}")
        return jsonify({"success": False, "message": f"Could not connect to validation service: {e}"}), 500


def _validate_key_on_server(api_key):
    """Validate the API key internally on the server."""
    if not api_key:
        return False

    validation_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(validation_url, timeout=5) # 5-second timeout
        if response.status_code == 200:
            logging.info("Server-side API key auto-validation successful.")
            return True
        else:
            logging.warning(f"Server-side API key auto-validation failed. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during server-side API key validation: {e}")
        return False

# --- Save/Load related API routes ---

@app.route('/api/save/export', methods=['POST'])
def export_save():
    """Export save file API"""
    try:
        # Update global state
        global CHAT_HISTORY, AGENT_STATE

        data = request.get_json()
        voxel_data = data.get('voxelData', {})
        chat_history = data.get('chatHistory', [])
        agent_state = data.get('agentState', AGENT_STATE)

        CHAT_HISTORY = chat_history
        AGENT_STATE.update(agent_state)

        # Create save data
        save_data = create_save_data(voxel_data, chat_history, agent_state)

        # Export to zip file
        zip_path = export_save_file(save_data)

        if zip_path and os.path.exists(zip_path):
            logging.info(f"Save exported successfully: {zip_path}")
            return send_file(zip_path, as_attachment=True, download_name=os.path.basename(zip_path))
        else:
            return jsonify({"success": False, "message": "Failed to export save"}), 500

    except Exception as e:
        logging.error(f"An error occurred while exporting save: {e}")
        return jsonify({"success": False, "message": f"Export failed: {str(e)}"}), 500

@app.route('/api/save/import', methods=['POST'])
def import_save():
    """Import save file API"""
    try:
        # Check for file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"success": False, "message": "No file selected"}), 400

            # Save to temporary file
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            file.save(temp_path.name)
            zip_path = temp_path.name
        else:
            # Check for URL
            data = request.get_json()
            url = data.get('url') if data else None
            if not url:
                return jsonify({"success": False, "message": "No file or URL provided"}), 400
            zip_path = url

        # Import save data
        save_data = import_save_file(zip_path)

        if save_data:
            # Update global state
            global CHAT_HISTORY, AGENT_STATE
            CHAT_HISTORY = save_data.get('chat_history', [])
            AGENT_STATE.update(save_data.get('agent_state', {}))

            logging.info("Save imported successfully")
            return jsonify({
                "success": True,
                "data": save_data
            })
        else:
            return jsonify({"success": False, "message": "Failed to import save"}), 500

    except Exception as e:
        logging.error(f"An error occurred while importing save: {e}")
        return jsonify({"success": False, "message": f"Import failed: {str(e)}"}), 500

@app.route('/api/agent/pause', methods=['POST'])
def pause_agent():
    """Pause AI agent API"""
    try:
        global AGENT_STATE
        AGENT_STATE['is_paused'] = True
        AGENT_STATE['is_running'] = False
        logging.info("AI agent paused")
        return jsonify({"success": True, "message": "AI agent paused"})
    except Exception as e:
        logging.error(f"An error occurred while pausing AI agent: {e}")
        return jsonify({"success": False, "message": f"Pause failed: {str(e)}"}), 500

@app.route('/api/agent/continue', methods=['POST'])
def continue_agent():
    """Continue AI agent API"""
    try:
        global AGENT_STATE
        AGENT_STATE['is_paused'] = False
        AGENT_STATE['is_running'] = True
        logging.info("AI agent continued")
        return jsonify({"success": True, "message": "AI agent continued"})
    except Exception as e:
        logging.error(f"An error occurred while continuing AI agent: {e}")
        return jsonify({"success": False, "message": f"Continue failed: {str(e)}"}), 500

@app.route('/api/agent/state', methods=['GET'])
def get_agent_state():
    """Get AI agent state API"""
    try:
        return jsonify({
            "success": True,
            "state": AGENT_STATE,
            "chat_history": CHAT_HISTORY
        })
    except Exception as e:
        logging.error(f"An error occurred while getting AI agent state: {e}")
        return jsonify({"success": False, "message": f"Failed to get state: {str(e)}"}), 500

# --- Main Program Entry ---
def main():
    """Main function to set up and run the web server."""
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="3D Voxel Viewer with AI Assistant")
    parser.add_argument('--input_model', type=str, help='URL or local path of the 3D model to load.')
    parser.add_argument('--input_data', type=str, help='URL or local path of the save file to import.')
    args = parser.parse_args()

    # --- Save Import Logic ---
    global CHAT_HISTORY, AGENT_STATE, INITIAL_SAVE_DATA
    if args.input_data:
        logging.info(f"Save data parameter detected: {args.input_data}")
        save_data = import_save_file(args.input_data)
        if save_data:
            # Only store the data in the initial variable, let the frontend handle it
            INITIAL_SAVE_DATA = save_data
            logging.info("Successfully loaded save data at startup, will be passed to the frontend.")
        else:
            logging.warning("Failed to import save data at startup")

    # --- Model Loading Logic ---
    global DOWNLOADED_MODEL_PATH
    if args.input_model:
        if args.input_model.startswith(('http://', 'https://')):
            # --- Handle URL ---
            url = args.input_model
            logging.info(f"Model URL detected: {url}")
            if not os.path.exists(CACHE_DIR):
                os.makedirs(CACHE_DIR)
                logging.info(f"Created cache directory: '{CACHE_DIR}'")

            try:
                # Extract filename from URL to use as cache filename
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename: # If the path is empty, use a default name
                    filename = "cached_model.glb"

                cached_path = os.path.join(CACHE_DIR, filename)

                logging.info(f"Downloading model from URL to '{cached_path}'...")
                response = requests.get(url, stream=True)
                response.raise_for_status() # Raise HTTPError if the request fails

                with open(cached_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                DOWNLOADED_MODEL_PATH = cached_path
                logging.info(f"Model successfully downloaded and cached.")

            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to download model from URL: {e}")
        else:
            # --- Handle local file path ---
            if os.path.exists(args.input_model):
                DOWNLOADED_MODEL_PATH = args.input_model
                logging.info(f"Loading model from local path: '{DOWNLOADED_MODEL_PATH}'")
            else:
                logging.warning(f"The provided local model path does not exist: '{args.input_model}'")


    # Check and load API key from key.txt file
    global API_KEY_FROM_FILE, API_KEY_VALIDATED
    if os.path.exists('key.txt'):
        with open('key.txt', 'r') as f:
            API_KEY_FROM_FILE = f.read().strip()
        if API_KEY_FROM_FILE:
            logging.info("Successfully loaded API key from key.txt file, now validating...")
            API_KEY_VALIDATED = _validate_key_on_server(API_KEY_FROM_FILE)
            if not API_KEY_VALIDATED:
                 logging.warning("The key loaded from key.txt failed validation. The application will require manual entry in the web page.")
        else:
            logging.warning("The key.txt file exists but is empty.")
    else:
        logging.info("The key.txt file was not found. The application will require manual key entry in the web page.")

    # Ensure the input directory exists
    if not os.path.exists(INPUT_DIR):
        logging.info(f"Creating '{INPUT_DIR}' directory, please place your models and reference images inside.")
        os.makedirs(INPUT_DIR)

    # Print usage instructions in the terminal
    print("\n" + "="*70)
    print("🚀 3D AI Assistant Viewer has started")
    print(f"Server is running on http://127.0.0.1:{PORT}")
    print("\n" + "-"*70)
    print("Instructions:")
    print(f"1. Model Loading: Place your .glb/.gltf model files in the '{INPUT_DIR}/' folder,")
    print(f"   or use the `--input_model <URL or path>` command-line argument to load directly.")
    print(f"2. Place your .png/.jpg reference images in the '{INPUT_DIR}/' folder.")
    print(f"3. Place your .zip texture packs in the same folder as this script.")
    print("4. The page has been automatically opened in your browser.")
    print("5. All file scanning and server logs will be displayed in this terminal window.")
    print("="*70 + "\n")

    # Open the browser with a delay in a new thread to ensure the server has time to start
    url = f"http://127.0.0.1:{PORT}"
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()

    # Start the Flask server
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == '__main__':
    main()
