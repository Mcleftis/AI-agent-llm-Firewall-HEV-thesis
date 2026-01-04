import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("------------First Visualization Check------------")


df = pd.read_csv(r"C:\Users\mclef\Desktop\project_ai\nev_energy_management_dataset.csv")

df.replace(["N/A", "-", "unknown"], float("nan"), inplace=True)
df.dropna(inplace=True)

#Basic Columns into Numeric
target = "Fuel Consumption (L/100km)"
speed = "Speed (km/h)"
engine_power = "Engine Power (kW)"  


for col in [target, speed, engine_power]:
    #Finding the real name of the column in the csv
    actual_name = [c for c in df.columns if col.split('(')[0] in c][0]
    df[actual_name] = pd.to_numeric(df[actual_name], errors='coerce')
    #Updating the name of the variables
    if col == target: target = actual_name
    if col == speed: speed = actual_name
    if col == engine_power: engine_power = actual_name

#Plotting

plt.figure(figsize=(15, 6))

# Plot 1: Speed vs Fuel Consumption

plt.subplot(1, 2, 1)
sns.scatterplot(x=df[speed], y=df[target], alpha=0.3)
plt.title(f'{speed} vs {target}')
plt.grid(True)

# Plot 2: Engine Power vs Fuel Consumption

plt.subplot(1, 2, 2)
sns.scatterplot(x=df[engine_power], y=df[target], alpha=0.3, color='orange')
plt.title(f'{engine_power} vs {target}')
plt.grid(True)

plt.tight_layout()
plt.show()

print("-----------------------------------Last Check-----------------------------------------")

import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv(r"C:\Users\mclef\Desktop\project_ai\nev_energy_management_dataset.csv")

#First 100 seconds
subset = df.iloc[:100]

# Scaling
power_norm = subset['Engine Power (kW)'] / subset['Engine Power (kW)'].max()
fuel_norm = subset['Fuel Consumption (L/100km)'] / subset['Fuel Consumption (L/100km)'].max()

plt.figure(figsize=(12, 6))
plt.plot(power_norm, label='Engine Power (Normalized)', color='orange')
plt.plot(fuel_norm, label='Fuel Consumption (Normalized)', color='black', linestyle='--')
plt.title('Power and Consumption Synchronization: (Check for Lag)')
plt.legend()
plt.show()