import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

from data_processor import get_data_ready, create_sequences


FILE_PATH = r"C:\Users\mclef\Desktop\thesis\my_working_dataset.csv"
TIME_STEPS = 60

X_scaled, y_scaled, scaler_y=get_data_ready(FILE_PATH)

#sequence creation
X_seq, y_seq=create_sequences(X_scaled, y_scaled, TIME_STEPS)
print(f"Σχήμα Δεδομένων(Data Shape): {X_seq.shape}")

#training
X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.2, shuffle=True, random_state=42)

#lstm
model = Sequential([
    LSTM(32, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=False),
    Dropout(0.2), 
    Dense(32, activation='relu'),
    Dense(1)
])

optimizer = Adam(learning_rate=0.0001)

model.compile(optimizer=optimizer, loss='mse')


history = model.fit(
    X_train, y_train, 
    epochs=100,           
    batch_size=16,        
    validation_split=0.2, 
    verbose=1
)

y_pred_scaled=model.predict(X_test)

y_pred_real=scaler_y.inverse_transform(y_pred_scaled)
y_test_real=scaler_y.inverse_transform(y_test)

print("r2:", r2_score(y_test_real,y_pred_real))
print("mae:", mean_absolute_error(y_test_real,y_pred_real))

plt.figure(figsize=(12, 6))
plt.plot(y_test_real[:100], label='Real Consumption', color='black')
plt.plot(y_pred_real[:100], label='Predict LSTM', color='purple', linestyle='--')
plt.title(f'LSTM Prediction (R2: {r2_score(y_test_real,y_pred_real):.3f})')
plt.ylabel('Liters / 100km')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()