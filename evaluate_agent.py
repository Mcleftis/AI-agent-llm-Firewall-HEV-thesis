import pandas as pd
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO
import os
import time

#einai gia to evaluate mode sto main.py, metraei thn apodosh tou AI xwris vohtheia, xwris LLM

DATA_FILENAME = "data/my_working_dataset.csv"


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
        terminated = self.current_step >= len(self.df) - 1
        
        return self._get_obs(), 0, terminated, False, {"fuel": fuel, "soc": self.soc}

#function calling main
def run_evaluation(model_path="models/ppo_hev", traffic="normal"):
    print(f"\nSTARTING EVALUATION (Traffic: {traffic})")
    print(f"Loading Model: {model_path}...")

    #Load Data
    if not os.path.exists(DATA_FILENAME):
        csv_path = "my_working_dataset.csv"
    else:
        csv_path = DATA_FILENAME
        
    try:
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Create Env
    env = ProfessionalHybridEnv(df)
    
    # Load Model
    try:
        model = PPO.load(model_path)
    except:
        print(f"Could not load model from {model_path}")
        return

    # Run Simulation
    obs, _ = env.reset()#neo perivallon
    total_fuel = 0
    steps = 0
    
    start_time = time.time()
    
    while True:
        action, _ = model.predict(obs)#pairnei th parathrhsh kai dra
        obs, _, done, _, info = env.step(action)#ti epistrefei to env.action
        total_fuel += info['fuel']#poso fuel katanalwthike se afto to vhma, prostithetai sto synoliko
        steps += 1
        if done: break#an teleiwse to episodeio, vges
    
    end_time = time.time()
    
    # Report
    print("-" * 30)
    print("EVALUATION COMPLETE")
    print("-" * 30)
    print(f"Duration: {end_time - start_time:.2f} sec")
    print(f"Total Fuel Consumed: {total_fuel:.4f} Liters")
    print(f"Final Battery SOC: {info['soc']:.2f}%")
    print("-" * 30)
    
    return {"fuel": total_fuel, "soc": info['soc']}

if __name__ == "__main__":
    run_evaluation()