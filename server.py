from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)
CORS(app)

# --- Load Config and Secrets ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
UBER_KEY = os.getenv('UBER_API_KEY')
SHEETS_CREDENTIALS_FILE = os.getenv('SHEETS_CREDENTIALS', 'your-credentials.json')

# --- Load Goddess Codes from JSON file ---
try:
    with open('goddess_truecodes.json', 'r', encoding='utf-8') as f:
        goddess_data = json.load(f)['goddesses']
    goddess_codes = {g['truecode']: g['g_id'] for g in goddess_data}
    print("✅ Goddess codes loaded successfully.")
except FileNotFoundError:
    print("⚠️ 'goddess_truecodes.json' not found. Login functionality will be limited.")
    goddess_codes = {}
except Exception as e:
    print(f"🔥 Error loading goddess codes: {e}")
    goddess_codes = {}


# --- Google Sheets Integration ---
try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(SHEETS_CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open("工資結算表").sheet1
    print("✅ Google Sheets integration successful.")
except FileNotFoundError:
    sheet = None
    print(f"⚠️ Google Sheets credentials not found at '{SHEETS_CREDENTIALS_FILE}'. Sheet functionality disabled.")
except Exception as e:
    sheet = None
    print(f"🔥 Error connecting to Google Sheets: {e}")


# --- API Endpoints ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data or 'truecode' not in data:
        return jsonify({"message": "Missing username, password, or truecode"}), 400

    # In a real app, you'd check username/password against a database
    if data['username'] == 'admin' and data['password'] == 'gpt4' and data['truecode'] in goddess_codes:
        return jsonify({"message": "登入成功 (Grok 4 自動驗證)"})

    return jsonify({"message": "錯誤"}), 401

@app.route('/driver/<driver_id>', methods=['POST'])
def receive_task(driver_id):
    task = request.json
    if not task or 'secure_token' not in task:
        return jsonify({"status": "rejected", "reason": "Missing secure_token"}), 400

    if task['secure_token'] not in goddess_codes:
        return jsonify({"status": "rejected", "reason": "Invalid secure_token"}), 403

    print(f"自動派單給 {driver_id}:", task)

    # 自動工資記錄
    if sheet:
        try:
            sheet.append_row([driver_id, task.get('reward', ''), task.get('deadline', ''), '已派單 (自動)'])
        except Exception as e:
            print(f"🔥 Error writing to Google Sheet: {e}")

    # 自動 LINE/Uber 通知 (Dummy functions)
    notifyLine(driver_id, task)
    integrateUberAuto(task)

    return jsonify({"status": "received", "driver": driver_id})

def notifyLine(driver_id, task):
    """Dummy function for LINE notification."""
    print(f"自動 LINE 通知 {driver_id}: {task.get('type', 'N/A')}")

def integrateUberAuto(task):
    """Dummy function for Uber integration."""
    print(f"自動 Uber 整合: {task.get('location', 'N/A')}")


if __name__ == '__main__':
    # Use environment variables for host and port for flexibility
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host=host, port=port, debug=True)
