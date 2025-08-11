#!/usr/bin/env python3
"""
Test the simplified connection
"""
from core.ibkr_connection_simple import SimpleIBKRConnection

print("Testing Simplified Connection")
print("="*60)

conn = SimpleIBKRConnection()
if conn.connect():
    print("✅ Connection successful!")
    
    # Test getting some data
    app = conn.get_app()
    if app:
        print(f"Next order ID: {app.nextOrderId}")
        print(f"Accounts: {app.accounts}")
    
    conn.disconnect()
else:
    print("❌ Connection failed")
    print("Make sure IB Gateway is running on port 8000")