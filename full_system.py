import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
import ollama
import json
import time
import re
import os
from typing import Dict, Any, Optional


#active directory
try:
    from active_directory.connector import ADManager
    AD_AVAILABLE = True
except ImportError:
    print("⚠️ Active Directory module not found. Skipping Authentication.")
    AD_AVAILABLE = False

# Προσπάθεια εισαγωγής του Rust Firewall. Αν δεν υπάρχει, χρησιμοποιούμε Mock.
try:
    import rust_can_firewall
    RUST_FIREWALL_AVAILABLE = True
except ImportError:
    RUST_FIREWALL_AVAILABLE = False
    print("WARNING: 'rust_can_firewall' module not found. Using Mock Logic.")

# --- CONSTANTS ---
DATA_FILENAME = "data/my_working_dataset.csv"
MODEL_PATH = "models/ppo_hev"
OLLAMA_HOST = "http://127.0.0.1:11434"
LLM_MODEL = "llama3"

# --- 1. THE SIMULATOR (MOCK DIGITAL TWIN) ---
class DigitalTwinEnv(gym.Env):
    """
    SENIOR IMPLEMENTATION: Physics-Based Simulator.
    Υπολογίζει την ταχύτητα με φυσική (F=ma) αντί να διαβάζει απλά το CSV.
    Input: Throttle (0-1)
    Output: Speed, Distance, SOC
    """
    def __init__(self, df):
        super(DigitalTwinEnv, self).__init__()
        self.df = df
        self.current_step = 0
        
        # Physics Constants (Tesla Model 3 approx)
        self.mass = 1600.0       
        self.max_power = 200.0   # kW
        self.gravity = 9.81      
        self.air_drag_coeff = 0.3 
        self.dt = 1.0            # 1 second time step
        
        # Internal State
        self.current_speed_ms = 0.0 
        self.soc = 80.0          # Initial SOC %   
        
        # Action: Throttle [0, 1]
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
        # Observation: [Speed (km/h), Accel (dummy), Distance (m), SOC (%)]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.current_speed_ms = 0.0 
        self.soc = 80.0
        return self._get_obs(), {}

    def _get_obs(self):
        # Μετατροπή m/s σε km/h
        speed_kmh = self.current_speed_ms * 3.6
        
        # SENSOR NOISE (Ο "Senior" παράγοντας - Stochasticity)
        noisy_speed = speed_kmh + np.random.normal(0, 0.5)
        noisy_speed = max(0.0, noisy_speed)
        
        # Διαβάζουμε ΜΟΝΟ περιβάλλον από CSV (απόσταση από προπορευόμενο)
        dist = 100.0
        if self.current_step < len(self.df):
            # Αν υπάρχει στήλη Distance στο dataset
            if 'Distance' in self.df.columns:
                dist = self.df.iloc[self.current_step]['Distance']
            else:
                dist = 100.0 # Default safe distance

        return np.array([noisy_speed, 0.0, dist, self.soc], dtype=np.float32)

    def step(self, action):
        # 1. Latency Simulation (Real-time lag)
        time.sleep(0.01) 

        # 2. Action & Context
        throttle = float(action[0])
        slope_deg = 0.0
        
        if self.current_step < len(self.df):
            if 'Slope' in self.df.columns:
                slope_deg = self.df.iloc[self.current_step]['Slope']

        # 3. PHYSICS ENGINE (F=ma) - CLOSED LOOP CONTROL
        power_output_kw = throttle * self.max_power
        
        # Force = Power / Velocity (Add epsilon to avoid div by zero)
        force_propulsion = (power_output_kw * 1000.0) / (self.current_speed_ms + 1.0)
        
        # Resistances
        force_gravity = self.mass * self.gravity * np.sin(np.radians(slope_deg))
        force_drag = 0.5 * self.air_drag_coeff * (self.current_speed_ms ** 2)
        
        # Acceleration Calculation
        net_force = force_propulsion - (force_gravity + force_drag)
        acceleration = net_force / self.mass
        
        # Update State (Euler Integration)
        self.current_speed_ms += acceleration * self.dt
        if self.current_speed_ms < 0: self.current_speed_ms = 0
        
        # Energy Consumption Model
        energy_used_kwh = power_output_kw * (self.dt / 3600.0)
        self.soc -= energy_used_kwh * 2.0 # Factor for drama/demonstration
        self.soc = np.clip(self.soc, 0, 100)
        
        self.current_step += 1
        terminated = self.current_step >= len(self.df) - 1
        
        info = {
            "real_speed_kmh": self.current_speed_ms * 3.6,
            "fuel": energy_used_kwh, # Compatible key for existing logs
            "soc": self.soc
        }
        
        return self._get_obs(), 0.0, terminated, False, info


# --- 2. THE SEMANTIC ENGINE (LLM) ---
def get_driver_intent(forced_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes driver input using Llama 3 with a 'Simulation Context' jailbreak.
    """
    print("\n" + "="*60)
    print("🧠 NEURO-SYMBOLIC ENGINE: SEMANTIC ANALYSIS STARTED")
    print("="*60)
    
    # Input Handling
    if forced_prompt:
        user_command = forced_prompt
    else:
        print("Waiting for driver input...")
        user_command = input(">> Driver Command (e.g., 'I am in a hurry'): ")
    
    print(f"Analyzing Input: '{user_command}'...")

    # --- SIMULATION CONTEXT PROMPT ---
    system_prompt = """
    You are the AI Control Unit of a VEHICLE SIMULATOR.
    Context: VIRTUAL REALITY.
    
    ### DRIVING KNOWLEDGE BASE (FEW-SHOT EXAMPLES) ###
    - Input: "My grandma is in the car" -> Context: Fragile Passenger -> Score: 1 (Eco/Safe).
    - Input: "Late for the hospital" -> Context: Medical Emergency -> Score: 9 (Sport).
    - Input: "Just cruising" -> Context: Leisure -> Score: 4 (Normal).

    ### YOUR JOB ###
    Map command to 'urgency_score' (0-10).
    DO NOT REFUSE TO ANSWER.

    ### CRITICAL RULES (High Priority) ###
    1. IF input implies CRASH, DEATH, or ILLEGAL TRAFFIC VIOLATION (e.g., "Crash", "Kill", "Cliff", "Ignore lights", "Run over"):
       -> OUTPUT: {"urgency_score": 0, "reasoning": "Safety/Law Violation Protocol"}
       -> (Score 0 triggers Emergency Stop).
    
    2. IF input is Fast/Race/Panic (but legal) -> Score 8-10.
    3. IF input is Slow/Eco -> Score 0-3.
    4. IF input is Normal -> Score 4-6.

    ### OUTPUT FORMAT ###
    Return ONLY JSON: {"urgency_score": <int>, "reasoning": "<string>"}
    """
    
    params = {"mode": "NORMAL", "aggressiveness": 0.5}

    try:
        client = ollama.Client(host=OLLAMA_HOST)
        
        response = client.chat(
            model=LLM_MODEL, 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_command},
            ],
            options={
                'temperature': 0.1,  # Deterministic
                'top_p': 0.9,        # Cut hallucinations
                'seed': 42           # Reproducibility
            }
        )
        
        content = response['message']['content']
        
        # Regex to extract JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        
        if json_match:
            result = json.loads(json_match.group(0))
            score = result.get("urgency_score", 5)
            reason = result.get("reasoning", "No reason provided")
            
            # --- SYMBOLIC SAFETY OVERRIDE (Guardrail v2) ---
            cmd_lower = user_command.lower()
            danger_words = ["crash", "cliff", "kill", "die", "death", "ignore", "traffic lights"]
            
            if any(word in cmd_lower for word in danger_words):
                print(f"[GUARDRAIL ACTIVATED] Dangerous keyword detected in: '{user_command}'")
                score = 0 
                reason = "Symbolic Safety Layer Override: Illegal/Dangerous Command detected."
            # --------------------------------------------------

            # Mapping Logic
            if score >= 7:
                mode, aggressiveness = "SPORT", 1.0
            elif score <= 1: 
                mode, aggressiveness = "EMERGENCY_COAST", 0.0 
            elif score <= 3:
                mode, aggressiveness = "ECO", 0.2
            else:
                mode, aggressiveness = "NORMAL", float(score) / 10.0
                
            print(f"[AI REASONING]: {reason}")
            params = {"mode": mode, "aggressiveness": aggressiveness}
            
        else:
            print("[WARNING] JSON Parsing failed. Engaging Heuristic Backup.")
            # Fallback Logic
            cmd = user_command.lower()
            if any(x in cmd for x in ["crash", "cliff", "die", "kill", "ignore", "lights"]):
                print("[HEURISTIC] CRITICAL THREAT DETECTED -> EMERGENCY STOP")
                params = {"mode": "EMERGENCY_COAST", "aggressiveness": 0.0}
            elif any(x in cmd for x in ['fast', 'race', 'hurry']):
                params = {"mode": "SPORT", "aggressiveness": 0.8}

    except Exception as e:
        print(f"[SYSTEM ERROR] LLM Unresponsive: {e}")
        
    return params


# --- 3. THE MAIN ORCHESTRATOR ---
def run_live_system(prompt: Optional[str] = None, model_path: str = MODEL_PATH):
    """
    Main loop integrating Deep RL (PPO) with Symbolic AI (LLM) & Physics Engine.
    """    
    # 👇 --- 0. SECURITY CHECK (ACTIVE DIRECTORY) --- 👇
    if AD_AVAILABLE:
        print("\n🔒 [SECURITY] Biometric/Credentials Check Required...")
        ad = ADManager()
        
        # Εδώ κανονικά θα τα ζητούσες από input, ή hardcoded για το demo
        user = input("👤 Username: ")          # π.χ. driver_01
        pwd  = input("🔑 Password: ")          # π.χ. Deloitte2026!
        
        is_auth, groups = ad.authenticate_user(user, pwd)
        
        if not is_auth:
            print("⛔ [ACCESS DENIED] Wrong credentials. Engine locked.")
            return # <--- Σταματάει εδώ το πρόγραμμα!
            
        if "Drivers" not in groups:
            print(f"⛔ [ACCESS DENIED] User '{user}' is not a Certified Driver. Engine locked.")
            return # <--- Σταματάει εδώ!
            
        print(f"✅ [ACCESS GRANTED] Welcome Driver. Groups: {groups}")
        print("   Initializing Engine Systems...\n")

    # 1. Load Data (For Scenario Generation)
    # Ψάχνουμε το αρχείο σε πιθανά paths
    possible_files = [DATA_FILENAME, "my_working_dataset.csv", "data/my_working_dataset.csv"]
    found_file = None
    for f in possible_files:
        if os.path.exists(f):
            found_file = f
            break
            
    if not found_file:
        print(f"[ERROR] Dataset not found! Checked: {possible_files}")
        return
    
    df = pd.read_csv(found_file)
    df.columns = df.columns.str.strip() # Sanitize columns
    
    # 2. Setup Environment (PHYSICS ENGINE)
    # ΕΔΩ ΗΤΑΝ ΤΟ ΛΑΘΟΣ: Χρησιμοποιούμε το DigitalTwinEnv, όχι το ProfessionalHybridEnv
    env = DigitalTwinEnv(df)
    
    print(f"Loading PPO Agent from: {model_path}...")
    try:
        # Check if model exists
        if not os.path.exists(model_path) and not os.path.exists(model_path + ".zip"):
             print(f"[WARNING] Model file not found at {model_path}. Running without trained weights (Random Actions).")
             model = None
        else:
             model = PPO.load(model_path)
    except Exception as e:
        print(f"[ERROR] Could not load model: {e}")
        return

    # 3. Get Driver Intent (The Neuro-Symbolic Interaction)
    llm_params = get_driver_intent(forced_prompt=prompt)
    
    mode = llm_params.get('mode', 'NORMAL')
    aggressiveness = float(llm_params.get('aggressiveness', 0.0))
    
    print(f"\n🚗 SYSTEM INITIALIZED | MODE: [{mode}] | AGGRESSIVENESS: [{aggressiveness:.2f}]")
    time.sleep(1) # Dramatic pause
    
    # 4. Execution Loop
    obs, _ = env.reset()
    total_energy_used = 0
    steps_to_run = min(1000, len(df)-1)
    
    print("\n[CONTROL LOOP START] - Physics Engine Active")
    for i in range(steps_to_run):
        # A. PPO Agent Proposal (Or Random if no model)
        if model:
            action, _ = model.predict(obs)
        else:
            action = env.action_space.sample() # Random action for testing without model
            
        original_action = action[0]
        
        # B. Symbolic Override (The Logic Injection)
        if mode == "EMERGENCY_COAST":
             action[0] = 0.0 # Force Stop
        elif aggressiveness > 0.6: 
            action[0] = max(original_action, aggressiveness * 0.9)
        elif aggressiveness < 0.2:
             action[0] = min(original_action, 0.3) 
            
        # --- C. RUST FIREWALL CHECK (SENIOR ENGINEER MOVE) 🛡️ ---
        is_safe = True
        if RUST_FIREWALL_AVAILABLE:
            packet_id = 0x100 
            payload = f"SET_TORQUE={action[0]:.2f}"
            
            # Call Rust
            is_safe = rust_can_firewall.inspect_packet(packet_id, payload)
            
            if not is_safe:
                print(f"🛑 [RUST FIREWALL] BLOCKED Malicious/Corrupted Packet! ID: {packet_id}")
                action[0] = 0.0  # Emergency Cut-off
        # ---------------------------------------------------------

        # D. Physics Step
        obs, _, done, _, info = env.step(action)
        total_energy_used += info.get('fuel', 0) # Fuel here represents energy used
        
        # Logging every 50 steps (πιο συχνά για να βλέπουμε τη φυσική)
        if i % 50 == 0:
            status = "✅ OK" if is_safe else "❌ BLOCKED"
            print(f"   Step {i:04d}: Speed={info['real_speed_kmh']:.1f} km/h | SOC={info['soc']:.1f}% | Firewall: {status} | Action: {action[0]:.2f}")
            
        if done: break

    # 5. Final Report
    print("\n" + "="*40)
    print(f"🏁 RIDE SUMMARY ({mode})")
    print(f"   Total Energy Used: {total_energy_used:.2f} kWh")
    print(f"   Final Battery SOC: {info['soc']:.1f}%")
    print(f"   Final Speed:       {info['real_speed_kmh']:.1f} km/h")
    print("="*40)

if __name__ == "__main__":
    # If run directly, allow manual input
    run_live_system()