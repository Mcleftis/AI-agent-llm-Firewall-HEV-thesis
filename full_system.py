import pandas as pd
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO
import ollama
import json
import time
import re

#Settings
DATA_FILENAME = r"C:\Users\mclef\Desktop\thesis\my_working_dataset.csv"
MODEL_PATH = "final_hybrid_agent_model"

#LLM
def get_driver_intent():
    print("\n" + "="*50)
    print("HYBRID AI SYSTEM: ONLINE")
    print("="*50)
    user_command = input("Tell the car how to drive(Greek, English): (π.χ. 'Βιάζομαι', 'Χαλαρά'): ")
    
    print("AI analyses...")
    
    #Improved Prompt in order to understand Greek
    system_prompt = """
    You are the ECU of a Hybrid Car. Translate the driver's command (which might be in Greek or English) to JSON.
    
    Rules:
    - If driver says "hurry", "fast", "βιάζομαι", "τρέξε" -> aggressiveness: 1.0, mode: "SPORT"
    - If driver says "relax", "eco", "χαλαρά", "οικονομικά" -> aggressiveness: 0.0, mode: "ECO"
    
    Output keys: 
    - 'aggressiveness' (0.0 to 1.0)
    - 'soc_target' (0-100)
    - 'mode' (string)
    
    Example output: {"aggressiveness": 0.8, "soc_target": 50, "mode": "SPORT"}
    Output ONLY JSON.
    """
    
    params = {"aggressiveness": 0.0, "soc_target": 60, "mode": "NORMAL"} # Default

    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_command},
        ])
        content = response['message']['content']
        
        # Smarter find JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            params = json.loads(json_str)
            print(f"Command Received: {params.get('mode', 'UNKNOWN')} (Aggr: {params.get('aggressiveness', 0)})")
        else:
            print("LLM responded with text instead of a JSON file. Setting Default.")
            
    except Exception as e:
        print(f"LLM Error {e}. Default.")
    
    return params


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
        pwr = row.get('Engine Power (kW)', 0) - row.get('Regenerative Braking Power (kW)', 0)
        return np.array([row.get('Speed (km/h)', 0), row.get('Acceleration (m/s²)', 0), pwr, self.soc], dtype=np.float32)

    def step(self, action):
        u_engine = float(action[0])
        row = self.df.iloc[self.current_step]
        pwr = row.get('Engine Power (kW)', 0) - row.get('Regenerative Braking Power (kW)', 0)
        
        fuel = 0.0
        if pwr <= 0:
            self.soc -= (pwr * 0.7) / 100 
        else:
            if (pwr * u_engine) > 0: fuel = (pwr * u_engine * 0.00025) 
            self.soc -= (pwr * (1.0 - u_engine) * 0.05) 
            
        self.soc = np.clip(self.soc, 0, 100)
        self.current_step += 1
        
        
        # Adding soc in dictionary
        info = {"fuel": fuel, "soc": self.soc}
        
        return self._get_obs(), 0, self.current_step >= len(self.df)-1, False, info

# Main programme
if __name__ == "__main__":
   
    df = pd.read_csv(DATA_FILENAME); df.columns = df.columns.str.strip()
    env = ProfessionalHybridEnv(df)
    
    print("Loading PPO...")
    try:
        model = PPO.load(MODEL_PATH)
    except:
        print("Run firstly AI_agent.py!"); exit()

    #Get a command from LLM
    llm_params = get_driver_intent()
    
    #Drive by having LLM as a guideline
    mode = llm_params.get('mode', 'NORMAL')
    print(f"\n🏎️  Ξεκινάει η οδήγηση σε mode: {mode}...")
    time.sleep(1)
    
    obs, _ = env.reset()
    total_fuel = 0
    aggressiveness = float(llm_params.get('aggressiveness', 0.0))
    
    #1000 steps
    for i in range(1000):
        action, _ = model.predict(obs)
        
        # Modifier: If sport, press throttle.
        if aggressiveness > 0.5:
            action[0] = max(action[0], aggressiveness * 0.9) # Boost
            
        obs, _, done, _, info = env.step(action)
        total_fuel += info['fuel']
        
        if i % 200 == 0:
            
            print(f"   Step {i}: SOC={info['soc']:.1f}%, Fuel so far={total_fuel:.2f}L")
            
        if done: break

    print("\n" + "="*40)
    print(f"End of ride ({mode})")
    print(f"Final consumption: {total_fuel:.2f} Liters")
    print("="*40)