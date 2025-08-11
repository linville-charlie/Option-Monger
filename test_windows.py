#!/usr/bin/env python3
"""
Test script for Windows local development
Run this on your Windows machine to test the connection
"""
import sys
import time
from core.ibkr_connection import IBKRConnection
from core.config import Config

print("="*60)
print("IBKR Connection Test for Windows")
print("="*60)

# Show current configuration
print(f"Host: {Config.TWS_HOST}")
print(f"Port: {Config.get_port()}")
print(f"Client ID: {Config.TWS_CLIENT_ID}")
print(f"Paper Trading: {Config.USE_PAPER_TRADING}")
print("="*60)

# Test connection
conn = IBKRConnection()
print("Attempting to connect...")

if conn.connect():
    print("✅ CONNECTION SUCCESSFUL!")
    
    app = conn.get_app()
    if app:
        print(f"Next Order ID: {app.nextOrderId}")
        print(f"Accounts: {app.accounts}")
        
        # Request current time as a test
        print("\nRequesting server time...")
        app.reqCurrentTime()
        time.sleep(1)
        
    print("\nConnection test completed successfully!")
    conn.disconnect()
else:
    print("❌ CONNECTION FAILED")
    print("\nPlease check:")
    print("1. IB Gateway is running on port 8000")
    print("2. 'Enable ActiveX and Socket Clients' is checked")
    print("3. Your client machine IP is in the trusted IPs list")
    
    app = conn.app
    if app and app._errors:
        print("\nErrors received:")
        for code, msg in app._errors:
            print(f"  - Error {code}: {msg}")