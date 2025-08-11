#!/usr/bin/env python3
"""
Test covered call strategy with REAL market data
"""
from YOUR_MAIN_INTERFACE import find_best_options
from datetime import datetime
import time

print("LIVE MARKET DATA TEST - COVERED CALLS")
print("="*70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Market should be open (9:30 AM - 4:00 PM ET)")
print("="*70)

# Use a weekly expiration for fewer strikes (faster)
ticker = 'AAPL'
expiration = '20250822'  # August 22, 2025 (weekly)
capital = 100000

print(f"\nStrategy Parameters:")
print(f"  Ticker: {ticker}")
print(f"  Expiration: {expiration}")
print(f"  Capital: ${capital:,}")
print("-"*70)

print("\n⏳ Connecting to IB Gateway (port 4002)...")
print("⏳ This will fetch REAL bid prices and deltas...")
print("⏳ Please wait 1-2 minutes for all strikes...\n")

start_time = time.time()

try:
    results = find_best_options(
        ticker=ticker,
        expiration=expiration,
        capital=capital,
        use_live_data=True,  # ← REAL DATA
        n_simulations=500,
        optimization_method='thorough'
    )
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*70)
    print("✅ SUCCESS - REAL MARKET DATA RESULTS")
    print("="*70)
    print(f"Data fetch time: {elapsed:.1f} seconds")
    
    # Show the full recommendation
    print("\n" + results['recommendation'])
    
    # Additional details
    print("\n" + "-"*70)
    print("REAL MARKET DATA DETAILS:")
    print("-"*70)
    
    print(f"\nStock Price (LIVE): ${results['current_stock_price']:.2f}")
    print(f"Shares to Buy: {results['shares_needed']:,}")
    print(f"Cost for Shares: ${results['capital_for_shares']:,.2f}")
    
    print(f"\nPremium from Selling Calls (REAL): ${results['premium_collected']:,.2f}")
    print(f"Net Capital After Premium: ${results['net_capital_after_premium']:,.2f}")
    
    print(f"\nExpected P&L: ${results['expected_pnl']:,.2f}")
    print(f"Return on Capital: {results['return_on_capital']:.2f}%")
    print(f"Win Rate: {results['win_rate']:.1f}%")
    
    if results.get('var_95'):
        print(f"95% VaR: ${results['var_95']:,.2f}")
    
    # Show each position with real Greeks
    print("\n" + "-"*70)
    print("POSITION DETAILS WITH REAL GREEKS:")
    print("-"*70)
    
    for detail in results['position_details']:
        print(f"\nStrike ${detail['strike']:.2f}:")
        print(f"  Contracts to Sell: {detail['quantity']}")
        print(f"  Real Bid Price: ${detail['bid']:.2f}")
        print(f"  Real Delta: {detail['delta']:.3f}")
        print(f"  ITM Probability: {detail['itm_probability']:.1f}%")
        print(f"  Premium per Contract: ${detail['premium_per_contract']:.2f}")
        print(f"  Total Premium: ${detail['premium_per_contract'] * detail['quantity']:.2f}")
    
    print("\n" + "="*70)
    print("EXECUTION READY")
    print("="*70)
    print(f"""
To execute this covered call strategy:

1. BUY {results['shares_needed']:,} shares of {ticker} at ~${results['current_stock_price']:.2f}
2. SELL the following calls (expiring {expiration}):""")
    
    for strike, qty in sorted(results['optimal_positions'].items()):
        print(f"   - {qty} contracts at ${strike:.2f} strike")
    
    print(f"""
3. COLLECT ${results['premium_collected']:,.2f} in premium immediately
4. HOLD until expiration
5. Expected profit: ${results['expected_pnl']:,.2f}
""")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n❌ Error after {elapsed:.1f} seconds: {e}")
    print("\nPossible issues:")
    print("1. Market might be closed (need regular trading hours)")
    print("2. IB Gateway connection issue")
    print("3. Market data subscription not active")
    print("4. Expiration date not available")
    
    # Show more error details
    import traceback
    print("\nDetailed error:")
    traceback.print_exc()

print("="*70)
print("END OF TEST")
print("="*70)