import time
import random
from can_bus_firewall import CANBusFirewall

def start_hacking_simulation():
    print("ACTIVATING FIREWALL TEST...\n")
    
    #ftiaxnoume ton fhlaks me delta=50 kai gia DoS na dexetai max 20
    firewall = CANBusFirewall(max_packets_per_sec=20, max_delta=50)

    #Normal odhghsh
    print("Phase 1: Normal Driving:")
    current_speed = 50.0
    packet_id = 0x123 #id ths taxythtas
    
    for i in range(5):
       
        current_speed += random.uniform(-2, 2)#prosthtetw ena mikro noumero apo -2 ews 2
        payload = str(current_speed)
        
        is_safe = firewall.inspect_packet(packet_id, payload)#kalei to firewall na kanei elegxo
        
        if is_safe:
            print(f"Packet Accepted: Speed {current_speed:.2f} km/h")
        else:
            print(f"BLOCKED: Speed {current_speed:.2f} km/h")
        
        time.sleep(0.1) # Κανονικός ρυθμός

    #Epithesh spoofing
    print("\nPhase 2: Spoofing Attack (The Teleport)")

    fake_speed = 200.0
    payload = str(fake_speed)
    
    print(f"HACKER: Sending fake speed {fake_speed} km/h...")
    is_safe = firewall.inspect_packet(packet_id, payload)#thymhsou h inspect packet to kanei flaot to payload    
    if is_safe:
        print("FAILURE: The attack passed!")
    else:
        print(f"SUCCESS: Attack Blocked! (Delta Check triggered)")

    #DoS (SPAMMING)
    print("\nPhase 3: DoS Attack (Flooding)")
    print("HACKER: Flooding the bus with 100 messages...")
    
    blocked_count = 0
    for i in range(50):
        #spammaroume astrapiaia paketa
        is_safe = firewall.inspect_packet(0x999, "spam") 
        if not is_safe:
            blocked_count += 1
            
    print(f"DoS Report: Sent 50 packets rapidly.")
    print(f"Firewall Blocked: {blocked_count} packets.")
    if blocked_count > 0:
        print("SUCCESS: DoS Attack Detected & Mitigated.")
    else:
        print("FAILURE: Firewall didn't catch the flood.")

if __name__ == "__main__":
    start_hacking_simulation()