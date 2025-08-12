#!/usr/bin/env python3
"""
Check what IB Gateway sessions are active
"""
import socket
import time

def check_port(host, port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

print("Checking IB Gateway/TWS ports...")
print("="*50)

# Common IB ports
ports = {
    7496: "TWS Live Trading",
    7497: "TWS Paper Trading", 
    4001: "IB Gateway Live Trading",
    4002: "IB Gateway Paper Trading",
    8000: "Custom Port (your setup)",
}

for port, description in ports.items():
    if check_port("127.0.0.1", port):
        print(f"✅ Port {port} is OPEN - {description}")
    else:
        print(f"❌ Port {port} is CLOSED - {description}")

print("\n" + "="*50)
print("RECOMMENDATION:")
print("="*50)

if check_port("127.0.0.1", 8000):
    print("Port 8000 is open (your IB Gateway)")
    print("\nThe 'competing live session' error means:")
    print("1. You may have another script/app using client ID 0")
    print("2. Or TWS is also running")
    print("\nSolutions:")
    print("- Close any Python scripts using IB API")
    print("- Use a different client ID (1, 2, or 3)")
    print("- Or close and restart IB Gateway")
else:
    print("Port 8000 is not open!")
    print("Please start IB Gateway first.")