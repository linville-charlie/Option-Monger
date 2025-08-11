#!/usr/bin/env python3
"""
Simple test of IB Gateway connection and market data
"""
from core.ibkr_connection import IBKRConnection
from core.options_data import OptionsDataFetcher
import time

print("SIMPLE IB GATEWAY CONNECTION TEST")
print("="*70)

# Test 1: Basic connection
print("\n1. Testing basic connection...")
conn = IBKRConnection()
if conn.connect():
    print("✅ Connected to IB Gateway successfully!")
    
    # Test 2: Get account info
    print("\n2. Getting account info...")
    time.sleep(2)  # Give it time to receive data
    
    # Test 3: Get stock price
    print("\n3. Fetching AAPL stock price...")
    fetcher = OptionsDataFetcher(conn)
    price = fetcher.get_underlying_price('AAPL')
    
    if price:
        print(f"✅ AAPL current price: ${price:.2f}")
    else:
        print("❌ Could not fetch stock price")
        print("   (May need market data subscription)")
    
    # Test 4: Get option strikes
    print("\n4. Getting available option strikes...")
    strikes = fetcher.get_option_strikes('AAPL', '20250815')
    
    if strikes:
        print(f"✅ Found {len(strikes)} strikes")
        print(f"   Range: ${min(strikes):.2f} to ${max(strikes):.2f}")
        
        # Test 5: Get one option's data (if we have subscription)
        if len(strikes) > 20:
            test_strike = strikes[20]  # Pick one in the middle
            print(f"\n5. Testing market data for ${test_strike:.2f} strike...")
            
            option_data = fetcher.get_option_data(
                symbol='AAPL',
                expiry='20250815',
                strike=test_strike,
                right='C'
            )
            
            if option_data and option_data.quote:
                print(f"✅ Got real market data!")
                print(f"   Bid: ${option_data.quote.bid:.2f}")
                print(f"   Ask: ${option_data.quote.ask:.2f}")
                if option_data.greeks:
                    print(f"   Delta: {option_data.greeks.delta:.3f}")
                    print(f"   Gamma: {option_data.greeks.gamma:.4f}")
                    print(f"   Theta: {option_data.greeks.theta:.3f}")
                    print(f"   Vega: {option_data.greeks.vega:.3f}")
            else:
                print("❌ No market data received")
                print("   Check market data subscriptions")
    else:
        print("❌ Could not fetch strikes")
    
    # Disconnect
    conn.disconnect()
    print("\n✅ Disconnected successfully")
    
else:
    print("❌ Failed to connect to IB Gateway")
    print("\nTroubleshooting:")
    print("1. Restart IB Gateway on Windows")
    print("2. Check API settings (Enable ActiveX and Socket Clients)")
    print("3. Port should be 4002")
    print("4. Add WSL IP to Trusted IPs")
    print("5. Check 'Read-Only API' is unchecked if you want to trade")

print("\n" + "="*70)
print("END OF TEST")
print("="*70)