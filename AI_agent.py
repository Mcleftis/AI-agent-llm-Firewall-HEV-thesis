import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
import os
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize


DATA_FILENAME = "data/my_working_dataset.csv"


class ProfessionalHybridEnv(gym.Env):
    def __init__(self, df, temperature=25):
        super(ProfessionalHybridEnv, self).__init__() #constructor
        self.df = df #apothikevei to dataset pou tou dwsame
        self.temperature = temperature #Ton xeimwna talaipwreitai parapanw ena HEV(prostethike meta)
        self.current_step = 0 #prwto row tou dataset
        self.soc = 60.0 #arxikh mpataria

        # Observation Space ti vlepei to AI
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32 #den exoun oria oi times, pannta tha mou dineis 4 times, to gym prepei na kserei ton typo twn parathrhsewn
        )

        # Action Space (Continuous: 0.0 to 1.0)
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)# to AI apofasizei poso hlektriko kai poso mhxanikoinhto 

    def reset(self, seed=None, options=None):#ksekina neo episodio
        super().reset(seed=seed) 
        self.current_step = 0
        self.soc = 60.0 
        return self._get_obs(), {}#to AI pairnei th prwth parathrhsh

    def _get_obs(self):#pairnei ton pinaka me tous 4 arithmous kai to dinei sto AI ws parathrhsh
        row = self.df.iloc[self.current_step]#fere mou th grammh pou antistoixei sto tade vhma
        
        # SAFE READ
        eng_pwr = row.get('Engine Power (kW)', 0)
        reg_pwr = row.get('Regenerative Braking Power (kW)', 0)
        power_demand = eng_pwr - reg_pwr

        obs = np.array([
            row.get('Speed (km/h)', 0),
            row.get('Acceleration (m/s²)', 0),
            power_demand,
            self.soc
        ], dtype=np.float32)# kane ena pinaka me 4 arithmous
        return obs#afta eiani ta dedomena sou

    def step(self, action):
        
        u_engine = float(action[0])#poso mhxanh thelw na xrhsimopoihsw
        row = self.df.iloc[self.current_step]#dedomena ths trexousas stigmhs
        
        #synthikes gia mpataria(prostethike meta)
        if self.temperature < 10:
            temp_factor = 1.2  #Kryo:H mpataria zorizetai
        elif self.temperature > 30:
            temp_factor = 1.1  #Zesth:Ara theloume air condition
        else:
            temp_factor = 1.0  #Idanika

        eng_pwr = row.get('Engine Power (kW)', 0)#an den to vrei, mhdenizetai
        reg_pwr = row.get('Regenerative Braking Power (kW)', 0)
        power_demand = eng_pwr - reg_pwr
        
        engine_power = 0.0
        battery_power = 0.0
        fuel_consumption = 0.0
        
        #periptwseis
        if power_demand <= 0:
            battery_power = power_demand
            self.soc -= (battery_power * 0.001 * (1.0 / temp_factor))
        else:
            engine_power = power_demand * u_engine
            battery_power = power_demand * (1.0 - u_engine)
            
            if engine_power > 0:
                fuel_consumption = (engine_power * 0.00025) 
            
            self.soc -= (battery_power * 0.001 * temp_factor)
            
        self.soc = np.clip(self.soc, 0, 100)# voitha sto na meinei h mpataria se evros 0-100, vazeis to self mprosta giati thes na to xrhsimopoihseis se olo to programma, allows apla thn orizeis xwris to self
        
        reward = 0
        reward -= fuel_consumption * 10
      
        if self.soc < 30: reward -= 1.0 * (30 - self.soc)
        elif self.soc > 90: reward -= 1.0 * (self.soc - 90)
            
        self.current_step += 1
        terminated = self.current_step >= len(self.df) - 1#an ftasei sto telos tou csv to epeisodio teleiwnei
        truncated = False #den stamatame to epeisodio gia kanenan allo logo
        
        info = {"fuel": fuel_consumption, "soc": self.soc}#extra plhrofories gia debugging
        
        return self._get_obs(), reward, terminated, truncated, info



def train_ppo(steps=200000, lr=0.0003, save_path="models/ppo_hev", traffic='normal'):
    print(f"\nStarting Training Session:")
    print(f"Configuration -> Steps: {steps}, LR: {lr}")
    
    #Loading data
    if not os.path.exists(DATA_FILENAME):
        print(f"Error: Cannot find file {DATA_FILENAME}")
        return

    print("Loading dataset...")
    df = pd.read_csv(DATA_FILENAME)
    df.columns = df.columns.str.strip() 

    if 'Regenerative Braking Power (kW)' not in df.columns:
         df['Regenerative Braking Power (kW)'] = 0.0

    #Creating environment wrapped in DummyVecEnv (gia Normalization)
    env = DummyVecEnv([lambda: ProfessionalHybridEnv(df)])
    
    #NORMALIZATION
    #ekshsorrophsh noumerwn gia na mathainei to AI pio grhgora
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.)

    #save path
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

    #Training
    print("Initializing PPO Agent with Normalization...")
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=lr)
    
    print("Training started...")
    model.learn(total_timesteps=steps)
    
    #Save Model AND Normalization Stats
    #aparaithto to save gia na ta kseroume meta 
    model.save(save_path)
    env.save(f"{save_path}_vecnormalize.pkl")
    
    print(f"Training Completed! Model saved at: {save_path}")


# Running on its own
if __name__ == "__main__":
    #Run with default settings if it is runned directly
    train_ppo()