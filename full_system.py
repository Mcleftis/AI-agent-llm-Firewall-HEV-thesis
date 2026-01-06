import pandas as pd
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO
import ollama
import json
import time
import re
import os

DATA_FILENAME = "data/my_working_dataset.csv"

#LLM Engine, Semantics se agglika
def get_driver_intent(forced_prompt=None):
    print("\n" + "="*50)
    print("HYBRID AI SYSTEM: SEMANTIC ENGINE ONLINE")
    print("="*50)
    
    if forced_prompt:
        user_command = forced_prompt
    else:
        user_command = input("Driver Command (Say anything): ")
    
    print("AI analyses semantic meaning...")
    
    system_prompt = """
    You are the AI Control Unit of a generic autonomous vehicle.
    Your task is to analyze the DRIVER'S INTENT based on their input (Greek or English).
    
    Steps to follow:
    1. Detect language (Greek/English).
    2. Identify sentiment (Urgency, Relaxation, Anger, Panic, Metaphors).
    3. Determine the 'Urgency Score' on a scale of 0 to 10.

    ### SCORING RULES ###
    - SCORE 8-10 (SPORT/RACE): Mentions of racing drivers (Hamilton, Rossi, McRae, Senna), fast cars (Ferrari, Porsche), metaphors (Rocket, Fire, Sfentona, Missile), or panic/emergency.
    - SCORE 0-2 (ECO/SLEEP): Mentions of slow animals (Turtle, Snail), family members (Grandma), relaxation (Sleep, Chill, Volta, Laraxa), or safety/economy.
    - SCORE 4-6 (NORMAL): Standard instructions, balanced driving.

    ### OUTPUT FORMAT ###
    You must return ONLY a JSON object:
    {"urgency_score": <int 0-10>, "reasoning": "<short explanation>"}
    """
    
    # Default Params (Fallback)
    params = {"mode": "NORMAL", "aggressiveness": 0.5}

    try:
        client = ollama.Client(host='http://127.0.0.1:11434')
        response = client.chat(model='llama3', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_command},
        ])
        
        content = response['message']['content']
        print(f"AI Internal Thought: {content}") 

        #eksagwgh tou json
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            score = result.get("urgency_score", 5)
            reason = result.get("reasoning", "No reason provided")
            
            #Den menoume pote sto normal an to score einai akraio
            if score >= 7:
                mode = "SPORT"
                aggressiveness = 1.0 # Τέρμα γκάζι
            elif score <= 3:
                mode = "ECO"
                aggressiveness = 0.1 # Πολύ χαλαρά
            else:
                mode = "NORMAL"
                aggressiveness = float(score) / 10.0 # Δυναμική προσαρμογή
                
            print(f"Analysis: {reason}")
            print(f"Result: Score {score}/10 -> Mode: {mode}")
            
            params = {"mode": mode, "aggressiveness": aggressiveness}
        else:
            print("JSON Parsing failed. Using Heuristics.")
            # Fallback σε απλή λογική αν αποτύχει το JSON
            cmd = user_command.lower()
            if any(x in cmd for x in ['fast', 'trexa', 'viazomai', 'hamilton', 'rossi']):
                params = {"mode": "SPORT", "aggressiveness": 1.0}
            elif any(x in cmd for x in ['slow', 'siga', 'laraxa', 'eco']):
                params = {"mode": "ECO", "aggressiveness": 0.2}

    except Exception as e:
        print(f"LLM Error: {e}")
        
    return params

#Environment
class ProfessionalHybridEnv(gym.Env):
    def __init__(self, df):
        super(ProfessionalHybridEnv, self).__init__()
        self.df = df
        self.current_step = 0
        self.soc = 60.0 
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32)
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.soc = 60.0 
        return self._get_obs(), {}

    def _get_obs(self):
        row = self.df.iloc[self.current_step]
        eng_pwr = row.get('Engine Power (kW)', 0)
        reg_pwr = row.get('Regenerative Braking Power (kW)', 0)
        pwr = eng_pwr - reg_pwr
        return np.array([row.get('Speed (km/h)', 0), row.get('Acceleration (m/s²)', 0), pwr, self.soc], dtype=np.float32)

    def step(self, action):
        u_engine = float(action[0])
        row = self.df.iloc[self.current_step]
        eng_pwr = row.get('Engine Power (kW)', 0)
        reg_pwr = row.get('Regenerative Braking Power (kW)', 0)
        pwr = eng_pwr - reg_pwr
        
        fuel = 0.0
        if pwr <= 0:
            self.soc -= (pwr * 0.7) / 100 
        else:
            if (pwr * u_engine) > 0: fuel = (pwr * u_engine * 0.00025) 
            self.soc -= (pwr * (1.0 - u_engine) * 0.05) 
            
        self.soc = np.clip(self.soc, 0, 100)
        self.current_step += 1
        
        info = {"fuel": fuel, "soc": self.soc}
        terminated = self.current_step >= len(self.df) - 1
        return self._get_obs(), 0, terminated, False, info

#Main Run function
def run_live_system(prompt="neutral", model_path="models/ppo_hev"):
    if not os.path.exists(DATA_FILENAME):
        if os.path.exists("my_working_dataset.csv"):
            csv_path = "my_working_dataset.csv"
        else:
            print(f"Error: Dataset not found.")
            return
    else:
        csv_path = DATA_FILENAME

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    env = ProfessionalHybridEnv(df)
    
    print(f"Loading PPO Agent from: {model_path}...")
    try:
        model = PPO.load(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    #Lhpsh entolhs mesw LLM
    llm_params = get_driver_intent(forced_prompt=prompt)
    
    mode = llm_params.get('mode', 'NORMAL')
    aggressiveness = float(llm_params.get('aggressiveness', 0.0))
    
    print(f"\nStarting Drive Mode: [{mode}]")
    time.sleep(1)
    
    obs, _ = env.reset()
    total_fuel = 0
    
    steps_to_run = min(1000, len(df)-1)
    for i in range(steps_to_run):
        action, _ = model.predict(obs)
        
        # LLM Injection Logic
        if aggressiveness > 0.6:
            action[0] = max(action[0], aggressiveness * 0.9)
        elif aggressiveness < 0.3:
             action[0] = min(action[0], 0.5) 
            
        obs, _, done, _, info = env.step(action)
        total_fuel += info['fuel']
        
        if i % 200 == 0:
            print(f"Step {i}: SOC={info['soc']:.1f}%, Fuel Used={total_fuel:.2f}L")
            
        if done: break

    print("\n" + "="*40)
    print(f"End of Ride Summary ({mode})")
    print(f"Final Consumption: {total_fuel:.2f} Liters")
    print(f"Final Battery: {info['soc']:.1f}%")
    print("="*40)

if __name__ == "__main__":
    run_live_system()