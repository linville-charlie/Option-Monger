#!/usr/bin/env python3
"""
Test with REAL market data subscriptions
"""
from YOUR_MAIN_INTERFACE import find_best_options
from datetime import datetime
import time

print("TESTING WITH REAL MARKET DATA")
print("="*70)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# Test with a shorter expiration for faster fetching
ticker = 'AAPL'
expiration = '20250815'  # August 15, 2025 (weekly, fewer strikes)
capital = 100000

print(f"\nParameters:")
print(f"  Ticker: {ticker}")
print(f"  Expiration: {expiration} (weekly - fewer strikes)")
print(f"  Capital: ${capital:,}")
print("-"*70)

start_time = time.time()

try:
    print("\nConnecting to IB Gateway...")
    print("Fetching REAL bid prices and deltas...")
    print("(This will take 1-2 minutes for all strikes)")
    
    results = find_best_options(
        ticker=ticker,
        expiration=expiration,
        capital=capital,
        use_live_data=True,  # Real data
        n_simulations=200,
        optimization_method='fast'  # Fast for testing
    )
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*70)
    print("RESULTS WITH REAL MARKET DATA")
    print("="*70)
    
    print(f"\nTime taken: {elapsed:.1f} seconds")
    
    print(f"\n1. STOCK PRICE (REAL):")
    print(f"   Current Price: ${results['current_stock_price']:.2f}")
    
    print(f"\n2. POSITION DETAILS (REAL BIDS & DELTAS):")
    for detail in results['position_details']:
        print(f"   Strike ${detail['strike']:.2f}:")
        print(f"     Quantity: {detail['quantity']} contracts")
        print(f"     Real Delta: {detail['delta']:.3f}")
        print(f"     Real Bid: ${detail['bid']:.2f}")
        print(f"     Premium per contract: ${detail['premium_per_contract']:.2f}")
    
    print(f"\n3. FINANCIAL SUMMARY:")
    print(f"   Shares to buy: {results['shares_needed']}")
    print(f"   Capital for shares: ${results['capital_for_shares']:,.2f}")
    print(f"   Premium collected (REAL): ${results['premium_collected']:,.2f}")
    print(f"   Expected P&L: ${results['expected_pnl']:,.2f}")
    print(f"   Win Rate: {results['win_rate']:.1f}%")
    
    print(f"\n4. OPTIMAL POSITIONS:")
    for strike, qty in sorted(results['optimal_positions'].items()):
        print(f"   Sell {qty} calls at ${strike:.2f}")
    
    print("\n" + "="*70)
    print("✅ SUCCESS - REAL MARKET DATA FETCHED")
    print("="*70)
    print("""
You now have:
- Real stock price from IBKR
- Real bid prices for each strike
- Real delta values from IBKR
- Optimization based on actual market conditions
""")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check market data subscriptions are active")
    print("2. Ensure market is open (9:30 AM - 4:00 PM ET)")
    print("3. Verify IB Gateway is running")
    print("4. Check account has permissions")
    
    import traceback
    print("\nFull error:")
    traceback.print_exc()

print("\n" + "="*70)
print("END OF TEST")
print("="*70)