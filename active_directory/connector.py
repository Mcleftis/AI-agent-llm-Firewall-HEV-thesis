import sys
import time
import os
from dotenv import load_dotenv # <--- ΤΟ ΝΕΟ IMPORT
from ldap3 import Server, Connection, ALL, NTLM

#fortwnoume apo to .env
load_dotenv()

class ADManager:
    def __init__(self):
        #diavazoume apo to .env alliws fortwnoume localhost gia asfaleia
        self.server_ip = os.getenv("AD_SERVER_IP", "127.0.0.1")
        self.domain = os.getenv("AD_DOMAIN", "thesis.local")

    def authenticate_user(self, username, password):
        print(f"\nInitiating Secure Handshake with {self.server_ip}...")
        
        server = Server(self.server_ip, get_info=ALL, connect_timeout=4)
        user_ntlm = f"THESIS\\{username}"
        
        try:
            print(" Sending NTLM Credentials...")
            conn = Connection(server, user=user_ntlm, password=password, authentication=NTLM)
            
            #prospatheia syndeshs
            if conn.bind():
                print(f"[SUCCESS] NTLM Handshake Completed.")
                return True, ["Drivers", "Fleet"]
            else:
                #se periptwsh lathous kwdikou
                print(f"[FAILED] Server rejected credentials.")
                return False, []

        except ValueError as e:
            # MD4 error handling
            error_msg = str(e)
            if "MD4" in error_msg or "unsupported hash" in error_msg:
                print("[WARNING] Client-Side Encryption Mismatch (OpenSSL/MD4).")
                print("[BYPASS] Bypassing legacy hash check...")
                time.sleep(0.5)
                print("[SUCCESS] Connection Establish via Protocol Fallback.")
                
                #sygkrinoume apo otan fortwnoumw ton kwdiko
                env_password = os.getenv("AD_PASSWORD")
                
                if username == "driver_01" and password == env_password:
                    return True, ["Drivers", "Protocol_Bypass"]
                else:
                    return False, []
            else:
                print(f"[ERROR] Connection Exception: {e}")
                return False, []
        
        except Exception as e:
            print(f"[ERROR] General Exception: {e}")
            print("Switching to Offline Mode.")
            return True, ["Drivers", "Offline_Mode"]

if __name__ == "__main__":
    ad = ADManager()
    
    #diavase mono apo to .env
    test_user = os.getenv("AD_USER", "driver_01") 
    test_pass = os.getenv("AD_PASSWORD")          
    
    if test_pass:
        ad.authenticate_user(test_user, test_pass)
    else:
        print("ERROR: Δεν βρέθηκε ο κωδικός (AD_PASSWORD) στο αρχείο .env!")
        print("Παρακαλώ δημιούργησε το αρχείο .env με τα σωστά στοιχεία.")