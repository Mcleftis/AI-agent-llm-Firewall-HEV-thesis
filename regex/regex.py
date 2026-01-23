import re  # <--- Να το Regex που ηθελες!

# Εστω οτι αυτο ειναι ενα κομματι απο το log file σου
dummy_logs = """
[2023-10-25 10:00:01] INFO: System Start
[2023-10-25 10:00:05] WARNING: CPU Temp High (85C)
[2023-10-25 10:00:10] ERROR: Connection Refused from IP 192.168.1.50
[2023-10-25 10:00:12] INFO: Throttle at 50%
[2023-10-25 10:00:15] CRITICAL: Rust Firewall BLOCKED command 'DROP_TABLE'
"""

def parse_logs():
    # 1. Φτιαχνουμε ενα Regex pattern
    # Ψαχνουμε γραμμες που λενε ERROR ή CRITICAL και μετα εχουν μηνυμα
    # (Μην αγχωνεσαι με τα συμβολα, απλα πες οτι ψαχνει patterns)
    pattern = r"(ERROR|CRITICAL):\s*(.*)"

    print("🔍 Scanning logs for threats...")
    
    # Διαβαζουμε τα logs γραμμη-γραμμη
    for line in dummy_logs.split('\n'):
        # 2. Εφαρμοζουμε το Regex
        match = re.search(pattern, line)
        
        if match:
            severity = match.group(1) # Π.χ. CRITICAL
            message = match.group(2)  # Π.χ. Rust Firewall BLOCKED...
            print(f"🚨 ALERT FOUND! Level: {severity} | Msg: {message}")

if __name__ == "__main__":
    parse_logs()