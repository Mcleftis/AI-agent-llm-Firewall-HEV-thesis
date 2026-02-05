import sys
import os
from dotenv import load_dotenv
load_dotenv()
import time
import random
import hashlib  # Security: Hashing
import logging  # IDS Logging
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from datetime import datetime

# --- AZURE CLOUD LIBRARY ---
from azure.storage.blob import BlobServiceClient

# --- LOCAL IMPORTS ---
# Προσθήκη του φακέλου thesis στο path για να βρει τα modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_logger import log_telemetry

# --- LOGGING SETUP (Local IDS) ---
logging.basicConfig(filename='intrusion_attempts.log', level=logging.WARNING, 
                    format='%(asctime)s - %(message)s')

# --- IMPORTS ΜΕ ΑΣΦΑΛΕΙΑ (Fallback αν λείπουν) ---
try:
    from full_system import get_driver_intent
    AI_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: full_system.py not found. Using Mock AI.")
    AI_AVAILABLE = False

try:
    import rust_can_firewall 
    RUST_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: Rust module not found. Running in Python Simulation Mode.")
    RUST_AVAILABLE = False

app = Flask(__name__)
CORS(app)

BASE_URL = '/api/v1'

# ==============================================================================
# 🔐 SECURITY CONFIGURATION
# ==============================================================================

# 1. TOKEN HASHING (SHA-256 για το "super-secret-key-2025")
STORED_TOKEN_HASH = os.getenv("TOKEN_HASH")

# 2. AZURE CLOUD CONFIG (GERMANY WEST CENTRAL)
AZURE_CONN_STRING = os.getenv("AZURE_STORAGE_KEY")
CONTAINER_NAME = "thesis-logs"

# ==============================================================================
# ☁️ CLOUD UPLOAD FUNCTION
# ==============================================================================
def upload_to_cloud(file_name):
    """
    REAL MODE: Στέλνει το log file στο Azure Storage για Forensic ανάλυση.
    """
    print(f"\n[CLOUD] ☁️ Initiating Upload to Azure Blob Storage...")
    
    try:
        # 1. Σύνδεση με το Cloud
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONN_STRING)
        
        # 2. Επιλογή του Κουβά (Container)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # 3. Διάβασμα και Ανέβασμα του αρχείου
        with open(file_name, "rb") as data:
            # Το overwrite=True αντικαθιστά το παλιό αρχείο
            container_client.upload_blob(name=file_name, data=data, overwrite=True)
            
        print(f"[CLOUD] ✅ SUCCESS: File '{file_name}' secure in Azure Cloud (Germany)!")
        
    except Exception as e:
        print(f"[CLOUD] ❌ ERROR: Upload failed. Reason: {e}")


# ==============================================================================
# 🧠 MAIN CONTROL ENDPOINT
# ==============================================================================
@app.route(f'{BASE_URL}/control/intent', methods=['POST'])
def analyze_intent():
    # --- A. SECURE TOKEN VERIFICATION ---
    user_token = request.headers.get("X-Auth-Token")
    
    if not user_token:
        abort(401)

    # Υπολογισμός Hash του κλειδιού που λάβαμε
    input_hash = hashlib.sha256(user_token.encode()).hexdigest()
    
    # Σύγκριση με το σωστό Hash
    if input_hash != STORED_TOKEN_HASH:
        logging.warning(f"IDS ALERT: Invalid Token Attempt from {request.remote_addr}")
        abort(401) # Λάθος κωδικός

    # --- B. PARSE DATA ---
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        command = data.get("command", "")
    except Exception as e:
        return jsonify({"error": "Bad Request"}), 400

    # --- C. IDS/IPS (SQL INJECTION CHECK) ---
    BAD_KEYWORDS = ["DROP", "DELETE", "SELECT", "INSERT", "--", "SCRIPT", "UNION"]
    
    if any(bad_word in command.upper() for bad_word in BAD_KEYWORDS):
        # 1. Καταγραφή στο τοπικό αρχείο
        alert_msg = f"🛑 CRITICAL IDS ALERT: SQL Injection Detected! Command: '{command}' IP: {request.remote_addr}"
        print(alert_msg)
        logging.critical(alert_msg)
        
        # 2. Αποστολή στο AZURE CLOUD (Off-site Backup)
        upload_to_cloud('intrusion_attempts.log')
        
        return jsonify({
            "status": "BLOCKED", 
            "reason": "Malicious SQL/Script Injection pattern detected by IDS. Incident reported to Cloud."
        }), 403

    # --- D. RUST FIREWALL CHECK ---
    is_safe = True
    if RUST_AVAILABLE:
        try:
            is_safe = rust_can_firewall.validate_command(command)
        except Exception as e:
            print(f"⚠️ Rust Error: {e}")

    if not is_safe:
         logging.warning(f"RUST FIREWALL ALERT: Blocked command '{command}'")
         return jsonify({"status": "BLOCKED", "reason": "Rust Firewall rejected the command."}), 403

    # --- E. AI LOGIC & OVERRIDE ---
    ai_mode = "NORMAL_MODE"
    try:
        if AI_AVAILABLE:
            ai_mode = get_driver_intent(command)
            print(f"🤖 AI Raw Answer: {ai_mode}")
        
        # Override Logic (Το "Hack" για να πιάνει πάντα το Sport Mode)
        if "fast" in command.lower() or "speed" in command.lower() or "sport" in command.lower():
             if "SPORT" not in str(ai_mode).upper():
                 print("⚡ FORCE OVERRIDE: Keyword detected -> Switching to SPORT")
                 ai_mode = "SPORT_MODE"

    except Exception as e:
        print(f"⚠️ AI Module Error: {e}")
        if "fast" in command.lower(): ai_mode = "SPORT_MODE"

    # --- F. FINAL RESPONSE ---
    mode_result = "NORMAL"
    if "SPORT" in str(ai_mode).upper(): 
        mode_result = "SPORT"
        
    return jsonify({
        "status": "APPROVED",
        "selected_mode": mode_result,
        "reasoning": f"AI output: {ai_mode}",
        "execution_time": 0.5,
        "throttle_sensitivity": 0.9 if mode_result == "SPORT" else 0.5
    })


# ==============================================================================
# 📡 TELEMETRY ENDPOINT
# ==============================================================================
@app.route(f'{BASE_URL}/vehicle/telemetry', methods=['GET'])
def get_telemetry():
    current_speed = round(random.uniform(50, 120), 1) # nosec
    current_battery = round(random.uniform(30, 90), 1) # nosec
    current_temp = round(random.uniform(70, 95), 1) # nosec
    
    try:
        log_telemetry(current_speed, current_battery, current_temp, source="API")
    except Exception as e:
        print(f"⚠️ Database Error: {e}")

    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "speed_kmh": current_speed,
        "battery_soc": current_battery,
        "motor_temp": current_temp,
        "ai_reasoning": "Vehicle operating within normal parameters." 
    })

@app.route(f'{BASE_URL}/security/status', methods=['GET'])
def get_security_status():
    status = "ACTIVE (Rust Engine v2.0 Protected)" if RUST_AVAILABLE else "SIMULATION_MODE (Python Fallback)"
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "firewall_status": status,
        "ids_status": "LOGGING ENABLED",
        "cloud_sync": "AZURE BLOB STORAGE (GERMANY)"
    })

# ==============================================================================
# 🚀 SERVER START
# ==============================================================================
if __name__ == '__main__':
    # SSL Setup
    cert_file = os.path.join('certs', 'cert.pem')
    key_file = os.path.join('certs', 'key.pem')
    
    print("\n" + "="*50)
    print("🚦 HYBRID AI VEHICLE CONTROL SYSTEM v2.0")
    print("🔒 SECURITY: Hashing, IDS & Azure Cloud Logging Active")
    print("🌍 CLOUD REGION: Germany West Central")
    print("="*50 + "\n")
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_context = (cert_file, key_file)
        app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=ssl_context)
    else:
        print("⚠️ SSL Certs not found. Running in HTTP mode (Not secure).")
        app.run(host='0.0.0.0', port=5000, debug=False)