#!/usr/bin/env python3
"""
Quick connection test after IB Gateway restart
"""
from core.ibkr_connection import IBKRConnection
from core.options_data import OptionsDataFetcher
from core.config import Config
import time
import socket

print("IB GATEWAY CONNECTION TEST")
print("="*70)
print(f"Configuration:")
print(f"  Host: {Config.TWS_HOST}")
print(f"  Port: {Config.get_port()}")
print(f"  Client ID: {Config.TWS_CLIENT_ID}")
print("="*70)

# First test raw socket connection
print("\n1. Testing socket connection...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex((Config.TWS_HOST, Config.get_port()))
    sock.close()
    
    if result == 0:
        print(f"✅ Port {Config.get_port()} is OPEN")
    else:
        print(f"❌ Cannot connect to port {Config.get_port()}")
        exit(1)
except Exception as e:
    print(f"❌ Socket error: {e}")
    exit(1)

# Now test API connection
print("\n2. Testing API connection...")
conn = IBKRConnection()

try:
    if conn.connect():
        print("✅ Connected to IB Gateway API!")
        
        # Wait a moment for connection to stabilize
        time.sleep(2)
        
        # Test getting stock price
        print("\n3. Testing market data...")
        fetcher = OptionsDataFetcher(conn)
        
        price = fetcher.get_underlying_price('AAPL')
        if price:
            print(f"✅ AAPL stock price: ${price:.2f}")
        else:
            print("⚠️ Could not get stock price (market may be closed)")
        
        # Get option strikes
        print("\n4. Getting option strikes...")
        strikes = fetcher.get_option_strikes('AAPL', '20250919')
        if strikes:
            print(f"✅ Found {len(strikes)} strikes")
            print(f"   Range: ${min(strikes):.2f} to ${max(strikes):.2f}")
        else:
            print("⚠️ No strikes found")
        
        conn.disconnect()
        print("\n✅ Connection test SUCCESSFUL!")
        print("="*70)
        print("IB Gateway is working correctly!")
        
    else:
        print("❌ Failed to connect to IB Gateway API")
        print("\nPlease check:")
        print("1. IB Gateway is logged in")
        print("2. Paper trading is selected")
        print("3. API settings are correct")
        
except Exception as e:
    print(f"❌ Error during connection: {e}")
    if conn:
        conn.disconnect()

print("\n" + "="*70)