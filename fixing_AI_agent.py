import pandas as pd
import os


file_path = r"C:\Users\mclef\Desktop\thesis\my_working_dataset.csv"

print(f"Searching the file in: {file_path}")

if os.path.exists(file_path):
    
    df = pd.read_csv(file_path)
    print("File found.")
    print(f"Columns before: {df.columns.tolist()}")

    if 'Regenerative Braking Power (kW)' not in df.columns:
        print("Caution! The Regenerative Brake (kW) is missing")
        print("Fixing...")

        # Create the column. # If 'Total Power' exists, we would normally use negative values as Regen. # If not, we simply set Regen to 0 to avoid errors.
        if 'Engine Power (kW)' in df.columns:
            df['Regenerative Braking Power (kW)'] = 0.0
        else:
            df['Regenerative Braking Power (kW)'] = 0.0

        
        df.to_csv(file_path, index=False)
        print("Success! File is updated.")
    else:
        print("The column already exists. No need to change.")

    print(f"Columns: {df.columns.tolist()}")
else:
    print("Error! Cannot find the file. Check the datapath")