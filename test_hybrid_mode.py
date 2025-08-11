#!/usr/bin/env python3
"""
Test with hybrid mode - real strikes/price, simulated bids/deltas
This works even when full market data connection has issues
"""
from YOUR_MAIN_INTERFACE import find_best_options
from datetime import datetime

print("HYBRID MODE TEST - COVERED CALLS")
print("="*70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
print("Using: Real strikes from IBKR + Simulated bids/deltas")
print("="*70)

# Test parameters
ticker = 'AAPL'
expiration = '20250919'  # September monthly
capital = 100000

print(f"\nStrategy Parameters:")
print(f"  Ticker: {ticker}")
print(f"  Expiration: {expiration}")
print(f"  Capital: ${capital:,}")
print("-"*70)

print("\nOptimizing covered call positions...")

try:
    # This will try to connect to get real strikes, 
    # but use simulated bids/deltas for speed
    results = find_best_options(
        ticker=ticker,
        expiration=expiration,
        capital=capital,
        use_live_data=True,  # Try to get real strikes
        n_simulations=500,
        optimization_method='thorough'
    )
    
    print("\n" + "="*70)
    print("OPTIMIZATION RESULTS")
    print("="*70)
    
    print(results['recommendation'])
    
    print("\n" + "-"*70)
    print("KEY METRICS:")
    print("-"*70)
    
    print(f"Current Stock Price: ${results['current_stock_price']:.2f}")
    print(f"Shares Needed: {results['shares_needed']:,}")
    print(f"Contracts to Sell: {results['contracts_sold']}")
    print(f"Premium to Collect: ${results['premium_collected']:,.2f}")
    print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
    print(f"Return on Capital: {results['return_on_capital']:.2f}%")
    print(f"Win Rate: {results['win_rate']:.1f}%")
    
    # Check if we got multiple strikes
    n_strikes = len(results['optimal_positions'])
    if n_strikes > 1:
        print(f"\n✅ Strategy uses {n_strikes} different strikes:")
    else:
        print(f"\n✓ Strategy uses single strike (optimal for this scenario):")
    
    for strike, qty in sorted(results['optimal_positions'].items()):
        print(f"  Sell {qty} calls at ${strike:.2f}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFalling back to pure demo mode...")
    
    # Try with pure demo mode
    try:
        results = find_best_options(
            ticker=ticker,
            expiration=expiration,
            capital=capital,
            use_live_data=False,  # Pure demo
            n_simulations=200
        )
        
        print("\nDEMO MODE RESULTS:")
        print("-"*50)
        print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
        print(f"Positions: {results['optimal_positions']}")
        
    except Exception as e2:
        print(f"Demo also failed: {e2}")

print("\n" + "="*70)
print("NOTES:")
print("="*70)
print("""
To get FULL real market data:
1. Ensure IB Gateway is freshly restarted
2. Check API settings (port 4002, trusted IPs)
3. Edit core/simple_real_strikes.py line 112
4. Change fetch_real_data = True

Current configuration:
- Host: 172.21.112.1 (Windows from WSL)
- Port: 4002 (IB Gateway)
- Market data subscription: Active
""")