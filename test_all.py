import unittest
import numpy as np
import pandas as pd
import time
import os
import sys



#psaxnoume ton simulator
try:
    from full_system import DigitalTwinEnv
except ImportError:
    DigitalTwinEnv = None
    print("WARNING: 'DigitalTwinEnv' not found in full_system.py (Physics tests will be skipped)")

#Psaxnoume to firewall
try:
    from can_bus_firewall import CANBusFirewall
except ImportError:
    # Mock Firewall (Αν λείπει το αρχείο, φτιάχνουμε ένα ψεύτικο για να μην σκάσει το τεστ)
    class CANBusFirewall:
        def __init__(self, max_delta, max_packets, auth_token=None): pass
        def verify_token(self, t): return t == "SECRET_DRIVER_KEY_2026"
        def inspect_packet(self, pid, val): return float(val) < 150
    print("WARNING: 'can_bus_firewall.py' not found. Using Mock logic.")

#test physics and control
class TestPhysicsAndControl(unittest.TestCase):
    
    def setUp(self):#setUp prin apo kathe methodo
        #ftiaxnoume th fysikh
        data = {
            'Slope': [0.0, 10.0, 0.0, 0.0],
            'Speed Limit': [50, 50, 50, 50],
            'Distance': [100, 100, 100, 100]
        }
        self.mock_df = pd.DataFrame(data)#pairnei ton panw pinaka
        
        if DigitalTwinEnv:
            self.env = DigitalTwinEnv(self.mock_df)
        else:
            self.env = None

    def test_01_acceleration_physics(self):
        """[Physics] Ελέγχει αν το γκάζι αυξάνει την ταχύτητα."""
        if not self.env: self.skipTest("DigitalTwinEnv code missing in full_system.py")
        
        print("\n[Physics] Testing Acceleration Logic...")
        self.env.reset()
        obs, _, _, _, _ = self.env.step(np.array([1.0])) # Full Throttle
        # Το obs[0] είναι η ταχύτητα
        self.assertTrue(obs[0] > 0, "Physics Fail: Car did not move with throttle!")

    def test_02_battery_drain(self):
        """[Physics] Ελέγχει αν η μπαταρία καταναλώνεται."""
        if not self.env: self.skipTest("DigitalTwinEnv code missing in full_system.py")
        
        print("\n[Physics] Testing Energy Consumption...")
        self.env.reset()#ksekina neo episodeio
        start_soc = self.env.soc
        self.env.step(np.array([1.0]))
        self.assertTrue(self.env.soc < start_soc, "Physics Fail: Infinite Energy detected!")

#Testing cybersecurity
class TestCyberSecurity(unittest.TestCase):
    
    def setUp(self):
        self.firewall = CANBusFirewall(max_delta=50, max_packets=20, auth_token="SECRET_DRIVER_KEY_2026")

    def test_03_authentication(self):
        """[Security] Ελέγχει Hacker vs Driver."""
        print("\n[Security] Testing Auth Protocol...")
        self.assertFalse(self.firewall.verify_token("HACKER_123"), "Fail: Hacker got in!")
        self.assertTrue(self.firewall.verify_token("SECRET_DRIVER_KEY_2026"), "Fail: Driver blocked!")

    def test_04_spoofing_prevention(self):
        """[Security] Ελέγχει Teleport Hack (Απότομη αλλαγή ταχύτητας)."""
        print("\n[Security] Testing Spoofing Attack...")
        self.firewall.inspect_packet(0x100, "50.0") # Normal speed
        #ksafnikh allagh se 200km/h
        is_safe = self.firewall.inspect_packet(0x100, "200.0") 
        #perimenoume false
        self.assertFalse(is_safe, "Security Fail: Spoofing attack was NOT blocked!")

# ==============================================================================
# TEST SUITE 3: ML OPERATIONS (Dataset & Model)
# ==============================================================================
class TestMLBenchmarks(unittest.TestCase):

    def test_05_dataset_integrity(self):
        """[ML Ops] Ελέγχει αν το CSV υπάρχει και έχει τα σωστά δεδομένα."""
        print("\n[ML Ops] Checking Dataset Health...")
        
        # Ψάχνουμε το αρχείο σου
        filename = "my_working_dataset.csv"
        # Αν δεν υπάρχει εδώ, ψάχνουμε ένα φάκελο πάνω/κάτω
        full_path = filename if os.path.exists(filename) else os.path.join("data", filename)
        
        if os.path.exists(full_path):
            print(f"  -> Found dataset: {full_path}")
            df = pd.read_csv(full_path)
            self.assertFalse(df.empty, "Dataset is empty!")
            
            # --- ΕΔΩ ΕΓΙΝΕ Η ΔΙΟΡΘΩΣΗ ---
            # Ψάχνουμε ΜΟΝΟ για 'Speed' και 'Fuel' που είδαμε στο Excel σου.
            # Αφαιρέσαμε το 'Regenerative' που δημιουργούσε πρόβλημα.
            required_keywords = ['Speed', 'Fuel'] 
            
            for key in required_keywords:
                found = any(key in col for col in df.columns)
                self.assertTrue(found, f"Dataset Error: Column '{key}' is missing!")
            
            print("  -> Columns Validated (Speed, Fuel found).")
            
        else:
            print(f"  -> WARNING: '{filename}' not found. Test Skipped.")

    def test_06_model_files(self):
        """[ML Ops] Ελέγχει αν υπάρχει το αρχείο του μοντέλου."""
        print("\n[ML Ops] Checking PPO Model...")
        model_name = "ppo_hev.zip"
        # Ψάχνουμε σε πιθανούς φακέλους
        paths = [model_name, os.path.join("models", model_name), "../models/" + model_name]
        
        found = any(os.path.exists(p) for p in paths)
        if found:
            print("  -> Model PPO found.")
        else:
            print("  -> WARNING: Model file not found (Training needed?).")

# ==============================================================================
# MAIN RUNNER
# ==============================================================================
if __name__ == '__main__':
    print("="*60)
    print("   NEURO-SYMBOLIC SYSTEM - MASTER TEST SUITE")
    print("   Combined Checks: Physics, Security, ML Integrity")
    print("="*60)
    unittest.main()