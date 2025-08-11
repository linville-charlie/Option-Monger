#!/usr/bin/env python3
"""
Test covered call strategy with LIVE market data
"""
from YOUR_MAIN_INTERFACE import find_best_options
from datetime import datetime

print("LIVE MARKET TEST - COVERED CALL STRATEGY")
print("="*70)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# Test parameters - Updated for August 2025
ticker = 'AAPL'
expiration = '20250919'  # September 19, 2025 (monthly expiration)
capital = 100000  # $100,000 to invest

print(f"\nTesting covered calls for:")
print(f"  Ticker: {ticker}")
print(f"  Expiration: {expiration} (September monthly)")
print(f"  Capital: ${capital:,}")
print("-"*70)

try:
    # Run with LIVE data
    print("\nConnecting to IB Gateway for live data...")
    results = find_best_options(
        ticker=ticker,
        expiration=expiration,
        capital=capital,
        use_live_data=True,  # ← LIVE DATA
        n_simulations=500,    # More simulations for accuracy
        optimization_method='thorough'  # Thorough optimization
    )
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    # Display the recommendation
    print(results['recommendation'])
    
    print("\n" + "-"*70)
    print("DETAILED BREAKDOWN")
    print("-"*70)
    
    print(f"\n1. SHARE PURCHASE:")
    print(f"   Current Stock Price: ${results['current_stock_price']:.2f}")
    print(f"   Shares to Buy: {results['shares_needed']:,}")
    print(f"   Total Cost for Shares: ${results['capital_for_shares']:,.2f}")
    
    print(f"\n2. CALL OPTIONS TO SELL:")
    for strike, qty in sorted(results['optimal_positions'].items()):
        print(f"   Sell {qty} calls at ${strike:.2f} strike")
    
    print(f"\n3. FINANCIAL SUMMARY:")
    print(f"   Premium Collected: ${results['premium_collected']:,.2f}")
    print(f"   Net Capital After Premium: ${results['net_capital_after_premium']:,.2f}")
    print(f"   Expected P&L: ${results['expected_pnl']:,.2f}")
    print(f"   Win Rate: {results['win_rate']:.1f}%")
    print(f"   Return on Capital: {results['return_on_capital']:.2f}%")
    
    if results.get('var_95'):
        print(f"   95% VaR: ${results['var_95']:,.2f}")
    if results.get('max_gain'):
        print(f"   Maximum Gain: ${results['max_gain']:,.2f}")
    if results.get('max_loss'):
        print(f"   Maximum Loss: ${results['max_loss']:,.2f}")
    
    print("\n" + "="*70)
    print("EXECUTION INSTRUCTIONS")
    print("="*70)
    print(f"""
To execute this strategy:

1. BUY SHARES:
   Place a market order for {results['shares_needed']:,} shares of {ticker}
   Estimated cost: ${results['capital_for_shares']:,.2f}

2. SELL CALLS (after shares are filled):
""")
    
    for strike, qty in sorted(results['optimal_positions'].items()):
        print(f"   Sell {qty} {ticker} {expiration} ${strike:.2f} Call")
    
    print(f"""
3. MONITOR:
   - Premium collected immediately: ${results['premium_collected']:,.2f}
   - Hold until expiration ({expiration})
   - Shares will be called away if ITM or sold if OTM
    """)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPossible issues:")
    print("1. IB Gateway not running")
    print("2. Market might be closed")
    print("3. Connection settings incorrect")
    print("4. No market data subscription")
    print("\nTrying with demo data instead...")
    
    try:
        # Fallback to demo data
        results = find_best_options(
            ticker=ticker,
            expiration=expiration,
            capital=capital,
            use_live_data=False,  # Demo data
            n_simulations=200
        )
        
        print("\n" + "="*70)
        print("DEMO RESULTS (Live data unavailable)")
        print("="*70)
        print(results['recommendation'])
        
    except Exception as e2:
        print(f"Demo also failed: {e2}")

print("\n" + "="*70)
print("END OF TEST")
print("="*70)