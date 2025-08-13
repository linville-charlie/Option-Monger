#!/usr/bin/env python3
"""
Debug script to troubleshoot stock price fetching
"""
import time
import logging
from datetime import datetime
from core.ibkr_connection import IBKRConnection
from core.options_data import OptionsDataFetcher

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("="*60)
print("STOCK PRICE DEBUG TEST")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# Test connection
print("\n1. Testing connection...")
conn = IBKRConnection()
if not conn.connect():
    print("❌ Failed to connect to IB Gateway")
    exit(1)
print("✅ Connected to IB Gateway")

try:
    # Get the app directly to check market data
    app = conn.get_app()
    print(f"\n2. App connected: {app.connected}")
    print(f"   Next order ID: {app.nextOrderId}")
    
    # Create fetcher
    fetcher = OptionsDataFetcher(conn)
    
    # Test stock data fetching with debug output
    print("\n3. Fetching AAPL stock data...")
    stock_data = fetcher.get_stock_data("AAPL")
    
    if stock_data:
        print("\n✅ Stock data received:")
        for key, value in stock_data.items():
            if value is not None and key != 'timestamp':
                print(f"   {key}: {value}")
    else:
        print("❌ No stock data received")
        
    # Test underlying price
    print("\n4. Testing get_underlying_price...")
    price = fetcher.get_underlying_price("AAPL")
    if price:
        print(f"✅ Underlying price: ${price:.2f}")
    else:
        print("❌ Could not get underlying price")
        
    # Check what's in market_data directly
    print("\n5. Checking app.market_data directly...")
    if hasattr(app, 'market_data'):
        print(f"   Market data keys: {list(app.market_data.keys())}")
        for req_id, data in app.market_data.items():
            print(f"   Request {req_id}: {data}")
    else:
        print("   No market_data attribute")
        
finally:
    conn.disconnect()
    print("\n✅ Disconnected from IB Gateway")

print("\n" + "="*60)
print("DEBUG COMPLETE")
print("="*60)