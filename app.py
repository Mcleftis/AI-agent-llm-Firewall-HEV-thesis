import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import sys

#dhmiourgia tou site


sys.path.append(os.path.dirname(os.path.abspath(__file__)))#exoume to path tou arxeiou, ginetai apolyto, me to dirname pairnoume ton fakelo pou to periexei, prosthetei afton ton fakelo ekei pou h python psaxnei modules
from full_system import get_driver_intent

#set-up selidas
st.set_page_config(page_title="Hybrid AI System Control", page_icon="🧠", layout="wide")#rythmizei thn emfanizh ths selidas, me layout=wide aplwnetai se olo to platos ths selidas

#data loading
@st.cache_data#krataei to apotelesma ths mnhmhs sth cache, gia na mhn allazei kathe fora pou kanoume allagh
def get_dataset():
    base_dir = os.path.dirname(os.path.abspath(__file__))#pou vrisketai to trexon arxeio
    possible_paths = [#to psaxnei se 2 merh
        os.path.join(base_dir, "data", "my_working_dataset.csv"),
        os.path.join(base_dir, "my_working_dataset.csv"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = [c.strip() for c in df.columns]#kovei ta kena apo deksia kai apo aristera
            cols_to_fix = ["Engine Power (kW)", "Regenerative Braking Power (kW)"]
            for col in cols_to_fix:
                if col in df.columns: df[col] = df[col].fillna(0)#gemizei me mhdenika ta kena
            return df, "✅ System Ready"
            
    # Mock Data Fallback
    dummy_df = pd.DataFrame({
        "Speed (km/h)": np.random.uniform(0, 120, 100),#100 tyxaioi arithmoi apo 0 ews 120
        "Engine Power (kW)": np.random.uniform(0, 50, 100),
        "Regenerative Braking Power (kW)": np.random.uniform(0, 20, 100),
    })
    return dummy_df, "⚠️ Demo Data Mode"

df, status_msg = get_dataset()#afta ta dyo kanei return h get_dataset

#UI Header
st.title("🧠 True Semantic AI Control")
st.markdown("### Powered by OpenAI Logic & Llama 3")#sxolio apo katw
if "Demo" in status_msg: st.warning(status_msg)#an yparxei to demo sto status_msg, exoume kitrino warning box sto streamlit UI
else: st.success(status_msg)#alliws ola fortwsan kanonika

#Sidebar/AI-input
st.sidebar.header("🗣️ Talk to the Car")#ti leei plagia h epikefalida
user_input = st.sidebar.text_input("Command:", placeholder="e.g. 'Οδήγα σαν τον παππού μου' or 'McRae style'")#koutaki pou dexetai ti tha grapsoume, kai mesa exei me thola afto to mhnyma

#AI proccessing logic
if 'mode' not in st.session_state:#to programma kathe fora pou allazei o xrhsths kati, trexxei ksana, px ana allaksei slider, an allaksei input, monimh mnhmh mexri o xrhsths na allaksei th synedria
    st.session_state['mode'] = "WAITING..."
    st.session_state['aggr'] = 0.5#afta ta dyo einai ta αrxika state an o xrhsths den exei dwsei kati

if st.sidebar.button("🧠 Analyze Intent"):#an o xrhsths pathsei to analyze_intent
    with st.spinner("AI is thinking (Llama 3)..."):#molis to pathsoume
        #kaloume ton egkefalo(oxi fake logic)
        try:
            result = get_driver_intent(forced_prompt=user_input)#pairnei to prompt tou odhgou
            st.session_state['mode'] = result['mode']
            st.session_state['aggr'] = result['aggressiveness']#efoson exoun stalei sto montelo, to montelo vgazei 2 apanthseis,ola afta ta kanei save alliws tha xathoun
        except Exception as e:
            st.error(f"AI Error: {e}")

# Display Results
mode = st.session_state['mode']
aggressiveness = st.session_state['aggr']

#Dahboard KPIs
k1, k2, k3 = st.columns(3)#treis ises sthles gia na valeis ta KPIs didpla dipla
k1.metric("AI Detected Mode", mode)#omorfo kouti typou kpi
k2.metric("Aggressiveness", f"{aggressiveness*100:.0f}%")#xwris dekadika
k3.metric("System Status", "ONLINE")

#Animation
st.divider()#orizontia grammh sto UI, spaei th selida
st.subheader("📡 Live Telemetry")
col1, col2 = st.columns(2)#xwrizei to section se 2 sthles
chart_speed = col1.empty()#dhmiourgei xwro gia na valoume otidhpote
chart_power = col2.empty()

start_simulation = st.sidebar.button("🚀 Start Simulation")#otan o xrhsths pathsei to koumpi h metavlhth ginetai true

if start_simulation:#molis paththei to koumpi trexei h if
    steps = min(len(df), 200)#mexri 200 vhmata
    progress_bar = st.progress(0)#exeis kai ena progress bar
    
    for i in range(1, steps):
        current_data = df.iloc[:i]#pairneis afta ta rows kai afto dhmiourgiei ena animation
        
        chart_speed.line_chart(current_data.get("Speed (km/h)", current_data.iloc[:, 0]), height=300)#an yparxei sthlh th xrhsimopoiei, alliws kane fallback xrhsimopoiwntas th prwth sthlh
        
        pwr_cols = ["Engine Power (kW)", "Regenerative Braking Power (kW)"]
        valid_cols = [c for c in pwr_cols if c in df.columns]#elegxei poies sthles einai power-related
        if valid_cols:
            chart_power.area_chart(current_data[valid_cols], height=300, color=["#ff4b4b", "#00ff00"])#kanei chart me afta ta dyo
            
        progress_bar.progress(i/steps)#anevazei to bar progress stadiaka
        time.sleep(0.05)
        
    st.success("Ride Complete ✅")
else:#otan den patietai to start simulation
    chart_speed.line_chart(df.get("Speed (km/h)", df.iloc[:, 0]), height=300)
    pwr_cols = ["Engine Power (kW)", "Regenerative Braking Power (kW)"]
    valid_cols = [c for c in pwr_cols if c in df.columns]
    if valid_cols:
        chart_power.area_chart(df[valid_cols], height=300, color=["#ff4b4b", "#00ff00"])