import pandas as pd
import matplotlib.pyplot as plt

# Φόρτωση
df = pd.read_csv(r"C:\Users\mclef\Desktop\project_ai\nev_energy_management_dataset.csv")

# Πάρε μόνο τα πρώτα 100 δευτερόλεπτα (για να φαίνεται καθαρά)
subset = df.iloc[:100]

# Κανονικοποίηση (Scaling) πρόχειρα για να μπουν στο ίδιο γράφημα
# Διαιρούμε με το μέγιστο για να πάνε όλα στο 0-1
power_norm = subset['Engine Power(kW)'] / subset['Engine Power(kW)'].max()
fuel_norm = subset['Fuel Consumption (L/100km)'] / subset['Fuel Consumption (L/100km)'].max()

plt.figure(figsize=(12, 6))
plt.plot(power_norm, label='Engine Power (Normalized)', color='orange')
plt.plot(fuel_norm, label='Fuel Consumption (Normalized)', color='black', linestyle='--')
plt.title('Συγχρονισμός Ισχύος & Κατανάλωσης (Check for Lag)')
plt.legend()
plt.show()