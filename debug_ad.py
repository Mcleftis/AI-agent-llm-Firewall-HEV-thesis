import socket
import sys
from ldap3 import Server, Connection, ALL, SIMPLE, NTLM

# --- RYTMISEIS ---
SERVER_IP = "127.0.0.1"   # Αν έχεις NAT+Port Forwarding
# SERVER_IP = "192.168.1.XX" # Αν έχεις Bridged (βάλε τη σωστή)

DOMAIN = "thesis.local"
USERNAME = "driver_01"
PASSWORD = "Deloitte2026!"

print("="*40)
print(f"🕵️‍♂️ STARTING DIAGNOSTIC TEST FOR: {SERVER_IP}")
print("="*40)

# ---------------------------------------------------------
# TEST 1: NETWORK SOCKET (Υπάρχει "καλώδιο";)
# ---------------------------------------------------------
print(f"\n[TEST 1] Checking connectivity to Port 389 (TCP)...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3) # 3 δευτερόλεπτα timeout
try:
    result = sock.connect_ex((SERVER_IP, 389))
    if result == 0:
        print("✅ SUCCESS: Port 389 is OPEN. Network is OK.")
    else:
        print("❌ FAILURE: Port 389 is CLOSED or UNREACHABLE.")
        print("   👉 Check VirtualBox Port Forwarding or Windows Firewall.")
        sys.exit() # Σταματάμε εδώ αν δεν υπάρχει δίκτυο
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit()
finally:
    sock.close()

# ---------------------------------------------------------
# TEST 2: LDAP BIND (Δέχεται τον κωδικό;)
# ---------------------------------------------------------
print(f"\n[TEST 2] Trying LDAP Login...")

# Δοκιμή 1: Με Administrator (Για να δούμε αν φταίει ο χρήστης)
print(f"   👉 Sub-test A: Trying with 'Administrator'...")
try:
    server = Server(SERVER_IP, get_info=ALL, connect_timeout=5)
    # Χρησιμοποιούμε Administrator για σιγουριά
    conn = Connection(server, user=f"Administrator@{DOMAIN}", password=PASSWORD, authentication=SIMPLE)
    
    if conn.bind():
        print("   ✅ SUCCESS! Administrator logged in.")
        print("      (Άρα ο Server δουλεύει και το δίκτυο είναι τέλειο)")
        conn.unbind()
    else:
        print("   ❌ FAILED with Administrator.")
        print(f"      Reason: {conn.result['description']}")
except Exception as e:
    print(f"   ⚠️ CRASH: {e}")

# Δοκιμή 2: Με τον οδηγό (driver_01) και διάφορα formats
print(f"\n   👉 Sub-test B: Trying with target user '{USERNAME}'...")

formats = [
    f"{USERNAME}@{DOMAIN}",       # driver_01@thesis.local
    f"THESIS\\{USERNAME}",        # THESIS\driver_01
    USERNAME                      # driver_01
]

for fmt in formats:
    print(f"      Trying format: '{fmt}' -> ", end="")
    try:
        conn = Connection(server, user=fmt, password=PASSWORD, authentication=SIMPLE)
        if conn.bind():
            print("✅ SUCCESS!")
            print(f"      Who am I? {conn.extend.standard.who_am_i()}")
            conn.unbind()
            break
        else:
            print("❌ FAILED")
            # Τυπώνουμε το ακριβές λάθος μόνο αν αποτύχουν όλα
            last_error = conn.result['description']
    except Exception as e:
        print(f"ERROR ({e})")

print("\n" + "="*40)
print("DIAGNOSTIC COMPLETE")