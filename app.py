import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import sys

#dhmiourgia tou site


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from full_system import get_driver_intent

#set-up selidas
st.set_page_config(page_title="Hybrid AI System Control", page_icon="🧠", layout="wide")

#data loading
@st.cache_data
def get_dataset():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, "data", "my_working_dataset.csv"),
        os.path.join(base_dir, "my_working_dataset.csv"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = [c.strip() for c in df.columns]
            cols_to_fix = ["Engine Power (kW)", "Regenerative Braking Power (kW)"]
            for col in cols_to_fix:
                if col in df.columns: df[col] = df[col].fillna(0)
            return df, "✅ System Ready"
            
    # Mock Data Fallback
    dummy_df = pd.DataFrame({
        "Speed (km/h)": np.random.uniform(0, 120, 100),
        "Engine Power (kW)": np.random.uniform(0, 50, 100),
        "Regenerative Braking Power (kW)": np.random.uniform(0, 20, 100),
    })
    return dummy_df, "⚠️ Demo Data Mode"

df, status_msg = get_dataset()

#UI Header
st.title("🧠 True Semantic AI Control")
st.markdown("### Powered by OpenAI Logic & Llama 3")
if "Demo" in status_msg: st.warning(status_msg)
else: st.success(status_msg)

#Sidebar/AI-input
st.sidebar.header("🗣️ Talk to the Car")
user_input = st.sidebar.text_input("Command:", placeholder="e.g. 'Οδήγα σαν τον παππού μου' or 'McRae style'")

#AI proccessing logic
if 'mode' not in st.session_state:
    st.session_state['mode'] = "WAITING..."
    st.session_state['aggr'] = 0.5

if st.sidebar.button("🧠 Analyze Intent"):
    with st.spinner("AI is thinking (Llama 3)..."):
        #kaloume ton egkefalo(oxi fake logic)
        try:
            result = get_driver_intent(forced_prompt=user_input)
            st.session_state['mode'] = result['mode']
            st.session_state['aggr'] = result['aggressiveness']
        except Exception as e:
            st.error(f"AI Error: {e}")

# Display Results
mode = st.session_state['mode']
aggressiveness = st.session_state['aggr']

#Dahboard KPIs
k1, k2, k3 = st.columns(3)
k1.metric("AI Detected Mode", mode)
k2.metric("Aggressiveness", f"{aggressiveness*100:.0f}%")
k3.metric("System Status", "ONLINE")

#Animation
st.divider()
st.subheader("📡 Live Telemetry")
col1, col2 = st.columns(2)
chart_speed = col1.empty()
chart_power = col2.empty()

start_simulation = st.sidebar.button("🚀 Start Simulation")

if start_simulation:
    steps = min(len(df), 200)
    progress_bar = st.progress(0)
    
    for i in range(1, steps):
        current_data = df.iloc[:i]
        
        chart_speed.line_chart(current_data.get("Speed (km/h)", current_data.iloc[:, 0]), height=300)
        
        pwr_cols = ["Engine Power (kW)", "Regenerative Braking Power (kW)"]
        valid_cols = [c for c in pwr_cols if c in df.columns]
        if valid_cols:
            chart_power.area_chart(current_data[valid_cols], height=300, color=["#ff4b4b", "#00ff00"])
            
        progress_bar.progress(i/steps)
        time.sleep(0.05)
        
    st.success("Ride Complete ✅")
else:
    chart_speed.line_chart(df.get("Speed (km/h)", df.iloc[:, 0]), height=300)
    pwr_cols = ["Engine Power (kW)", "Regenerative Braking Power (kW)"]
    valid_cols = [c for c in pwr_cols if c in df.columns]
    if valid_cols:
        chart_power.area_chart(df[valid_cols], height=300, color=["#ff4b4b", "#00ff00"])