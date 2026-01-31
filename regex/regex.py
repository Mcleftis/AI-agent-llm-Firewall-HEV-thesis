import re  # <--- Να το Regex που ηθελες!


dummy_logs = """
[2023-10-25 10:00:01] INFO: System Start
[2023-10-25 10:00:05] WARNING: CPU Temp High (85C)
[2023-10-25 10:00:10] ERROR: Connection Refused from IP 192.168.1.50
[2023-10-25 10:00:12] INFO: Throttle at 50%
[2023-10-25 10:00:15] CRITICAL: Rust Firewall BLOCKED command 'DROP_TABLE'
"""

def parse_logs():



    pattern = r"(ERROR|CRITICAL):\s*(.*)"

    print("🔍 Scanning logs for threats...")
    

    for line in dummy_logs.split('\n'):

        match = re.search(pattern, line)
        
        if match:
            severity = match.group(1) # Π.χ. CRITICAL
            message = match.group(2)  # Π.χ. Rust Firewall BLOCKED...
            print(f"🚨 ALERT FOUND! Level: {severity} | Msg: {message}")

if __name__ == "__main__":
    parse_logs()