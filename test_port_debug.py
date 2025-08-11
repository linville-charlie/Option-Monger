#!/usr/bin/env python3
"""
Debug port and connection settings
"""
from core.config import Config

print("CURRENT CONFIGURATION:")
print("="*50)
print(f"Host: {Config.TWS_HOST}")
print(f"Port: {Config.TWS_PORT}")
print(f"Paper Port: {Config.TWS_PAPER_PORT}")
print(f"Live Port: {Config.TWS_LIVE_PORT}")
print(f"Client ID: {Config.TWS_CLIENT_ID}")
print(f"Use Paper Trading: {Config.USE_PAPER_TRADING}")
print(f"Actual Port Used: {Config.get_port()}")
print("="*50)

import socket
print(f"\nTesting connection to {Config.TWS_HOST}:{Config.get_port()}...")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex((Config.TWS_HOST, Config.get_port()))
    sock.close()
    
    if result == 0:
        print(f"✅ Port {Config.get_port()} is OPEN - IB Gateway is reachable")
    else:
        print(f"❌ Cannot connect to port {Config.get_port()}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nIf connection failed, please verify:")
print(f"1. IB Gateway is configured to use port {Config.get_port()}")
print("2. Your WSL IP is in the trusted IPs list")
print("3. 'Enable ActiveX and Socket Clients' is checked in API settings")