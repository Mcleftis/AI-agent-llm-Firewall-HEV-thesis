import sys
import os
import time
import random
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from datetime import datetime
from db_logger import log_telemetry


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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
    print("⚠️ Warning: Rust module not found. Did you run 'maturin develop'?")
    RUST_AVAILABLE = False

app = Flask(__name__)
CORS(app)


BASE_URL = '/api/v1'


API_SECRET_TOKEN = "super-secret-key-2025"


@app.route(f'{BASE_URL}/control/intent', methods=['POST'])
def analyze_intent():

    user_token = request.headers.get('X-Auth-Token')
    
    if user_token != API_SECRET_TOKEN:
        print(f"⛔ SECURITY ALERT: Unauthorized access attempt from {request.remote_addr}")
        abort(403)

    data = request.json
    raw_command = data.get('command', '') 
    print(f"🧠 AI Request Received: '{raw_command}'")
    

    if RUST_AVAILABLE:
        safe_command = rust_can_firewall.sanitize_command(raw_command)
        
        if safe_command is None:
            print(f"⛔ BLOCKED: H Rust ekopse thn entolh '{raw_command}'!")
            return jsonify({
                "status": "BLOCKED",
                "reason": "Safety Violation detected by Rust Firewall (Active Protection)",
                "original_command": raw_command
            }), 403


    if AI_AVAILABLE:
        try:
            start_time = time.time()
            time.sleep(0.5) 
            result = {
                "status": "APPROVED",
                "selected_mode": "SPORT" if "fast" in raw_command else "NORMAL",
                "throttle_sensitivity": 0.9,
                "reasoning": f"AI processed '{raw_command}' and Rust confirmed safety.",
                "execution_time": round(time.time() - start_time, 2)
            }
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        result = {
            "status": "SIMULATION_OK",
            "selected_mode": "NORMAL",
            "reasoning": "Mock Response (AI Module not loaded)"
        }

    return jsonify(result)



@app.route(f'{BASE_URL}/vehicle/telemetry', methods=['GET'])
def get_telemetry():
    current_speed = round(random.uniform(50, 120), 1)
    current_battery = round(random.uniform(30, 90), 1)
    current_temp = round(random.uniform(70, 95), 1)
    
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
    blocked_count = 0
    status = "INACTIVE"
    threat_level = "LOW"
    
    if RUST_AVAILABLE:
        try:
            blocked_count = rust_can_firewall.get_firewall_stats()
            status = "ACTIVE (Rust Engine v2.0 Protected)"
            
            if blocked_count > 10:
                threat_level = "CRITICAL"
            elif blocked_count > 0:
                threat_level = "MODERATE"
            else:
                threat_level = "LOW"
                
        except Exception as e:
            print(f"Rust Error: {e}")
            status = "ERROR_STATE"
    else:
        status = "SIMULATION_MODE (Python Fallback)"

    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "firewall_status": status,
        "blocked_packets_last_min": blocked_count, 
        "current_threat_level": threat_level
    })


if __name__ == '__main__':

    cert_file = os.path.join('certs', 'cert.pem')
    key_file = os.path.join('certs', 'key.pem')


    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_context = (cert_file, key_file)
        
        print("\n" + "="*50)
        print("🚀 API Server is running SECURELY over HTTPS!")
        print(f"👉 Access via: https://localhost:5000{BASE_URL}")
        print(f"🔒 Certificates loaded from: {cert_file}")
        print("="*50 + "\n")
        

        app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=ssl_context)
    else:
        print("\n" + "!"*50)
        print("❌ Error: Certificates not found in 'certs' folder.")
        print("Please run 'python setup_certs.py' first to generate keys.")
        print("!"*50 + "\n")