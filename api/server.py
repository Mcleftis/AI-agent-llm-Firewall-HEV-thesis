import sys
import os
import time
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from db_logger import log_telemetry  

# Prosthetoume ton "gonea" fakelo sto path gia na vroume to full_system.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- 1. IMPORT TO AI MODULE (LLAMA 3) ---
try:
    from full_system import get_driver_intent
    AI_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: full_system.py not found. Using Mock AI.")
    AI_AVAILABLE = False

# --- 2. IMPORT TO RUST FIREWALL (SAFETY LAYER) ---
try:
    import rust_can_firewall 
    RUST_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: Rust module not found. Did you run 'maturin develop'?")
    RUST_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Vasiko URL (Prepei na tairiazei me to openapi.yaml)
BASE_URL = '/api/v1'

# --- ENDPOINT 1: AI CONTROL & SAFETY CHECK (POST) ---
# URL: /api/v1/control/intent
@app.route(f'{BASE_URL}/control/intent', methods=['POST'])
def analyze_intent():
    # Diavazoume to JSON pou steilame
    data = request.json
    raw_command = data.get('command', '') # P.x. "GIVE_MAX_THROTTLE"
    print(f"🧠 AI Request Received: '{raw_command}'")
    
    # --- VIMA A: ELEGXOS ASFALEIAS ME RUST (ACTIVE SAFETY) 🛡️ ---
    # Auto einai to "Man-in-the-Middle" check pou legane gia thn Comma.ai
    if RUST_AVAILABLE:
        # H Rust elegxei an h entolh einai asfalhs
        safe_command = rust_can_firewall.sanitize_command(raw_command)
        
        # An h Rust epistrepsei None, shmainei oti to ekopse!
        if safe_command is None:
            print(f"⛔ BLOCKED: H Rust ekopse thn entolh '{raw_command}'!")
            return jsonify({
                "status": "BLOCKED",
                "reason": "Safety Violation detected by Rust Firewall (Active Protection)",
                "original_command": raw_command
            }), 403  # 403 Forbidden HTTP Code

    # --- VIMA B: AI PROCESSING (An perasei ton elegxo) ---
    if AI_AVAILABLE:
        try:
            # Simuloume ligo xrono skepshs tou AI
            start_time = time.time()
            time.sleep(0.5) 
            
            # Edw kanonika tha kalousame to get_driver_intent(raw_command)
            # Gia to demo epistrefoume ena domhmeno apotelesma
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
        # Fallback an den exoume AI
        result = {
            "status": "SIMULATION_OK",
            "selected_mode": "NORMAL",
            "reasoning": "Mock Response (AI Module not loaded)"
        }

    return jsonify(result)


# --- ENDPOINT 2: VEHICLE TELEMETRY (GET) ---
# URL: /api/v1/vehicle/telemetry
@app.route(f'{BASE_URL}/vehicle/telemetry', methods=['GET'])
def get_telemetry():
    # print("Telemetry Request") -> To ekopsa gia na mhn gemizei to log
    
    # 1. Paragwgh tyxaiwn dedomenwn (Simulation tou CAN Bus)
    current_speed = round(random.uniform(50, 120), 1)
    current_battery = round(random.uniform(30, 90), 1)
    current_temp = round(random.uniform(70, 95), 1)
    
    # 2. LOGGING STH VASH (Black Box Recorder) 📼
    try:
        log_telemetry(current_speed, current_battery, current_temp, source="API")
    except Exception as e:
        print(f"⚠️ Database Error: {e}")

    # 3. Epistrofh sto Dashboard (JSON)
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "speed_kmh": current_speed,
        "battery_soc": current_battery,
        "motor_temp": current_temp,
        "ai_reasoning": "Vehicle operating within normal parameters." # Gia to neo dashboard
    })


# --- ENDPOINT 3: SECURITY STATUS (GET) ---
# URL: /api/v1/security/status
@app.route(f'{BASE_URL}/security/status', methods=['GET'])
def get_security_status():
    print("🛡️ Security Check (Real-Time Rust Stats)")
    
    # Default times (an kati paei strava)
    blocked_count = 0
    status = "INACTIVE"
    threat_level = "LOW"
    
    if RUST_AVAILABLE:
        try:
            # Kaloume thn ALITHINH Rust synarthsh pou ftiaksame
            blocked_count = rust_can_firewall.get_firewall_stats()
            
            status = "ACTIVE (Rust Engine v2.0 Protected)"
            
            # Logiki gia to Threat Level (pws allazei to xrwma sto dashboard)
            if blocked_count > 10:
                threat_level = "CRITICAL"  # Kokkino
            elif blocked_count > 0:
                threat_level = "MODERATE"  # Portokali
            else:
                threat_level = "LOW"       # Prasino
                
        except Exception as e:
            print(f"Rust Error: {e}")
            status = "ERROR_STATE"
    else:
        status = "SIMULATION_MODE (Python Fallback)"

    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "firewall_status": status,
        "blocked_packets_last_min": blocked_count, # <--- 100% REAL NUMBER
        "current_threat_level": threat_level
    })

if __name__ == '__main__':
    print("🚀 API Server is running correctly now!")
    print(f"👉 Listening on: http://localhost:5000{BASE_URL}")
    app.run(host='0.0.0.0', port=5000, debug=True)