#!/usr/bin/env python3
"""
Test live option data fetching now that we have market data subscription
"""
import time
import threading
from datetime import datetime
from YOUR_MAIN_INTERFACE import find_best_options

print("="*60)
print("LIVE OPTION DATA TEST - WITH SUBSCRIPTION")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# Test parameters
ticker = "AAPL"
expiration = "20250815"  # August 15, 2025 (Friday)
capital = 100000  # $100,000 to invest

print(f"\nTest Parameters:")
print(f"  Ticker: {ticker}")
print(f"  Expiration: {expiration}")
print(f"  Capital: ${capital:,}")
print(f"  Data Mode: LIVE (with subscription)")

print("\n" + "-"*60)
print("Running covered call optimization with LIVE data...")
print("-"*60)

try:
    # Run with LIVE data
    results = find_best_options(
        ticker=ticker,
        expiration=expiration,
        capital=capital,
        max_contracts_per_strike=50,
        n_simulations=1000,  # More simulations for better accuracy
        optimization_method='auto',
        use_live_data=True  # USE LIVE DATA
    )
    
    print("\n" + "="*60)
    print("LIVE OPTIMIZATION RESULTS")
    print("="*60)
    
    # Display results
    print(f"\nCurrent Stock Price: ${results['current_stock_price']:.2f}")
    print(f"Shares to Buy: {results['shares_needed']:,}")
    print(f"Share Purchase Cost: ${results['capital_for_shares']:,.2f}")
    print(f"Premium Collected: ${results['premium_collected']:,.2f}")
    print(f"Net Investment: ${results['net_capital_after_premium']:,.2f}")
    
    print(f"\nExpected P&L: ${results['expected_pnl']:,.2f}")
    print(f"Win Rate: {results['win_rate']:.1f}%")
    print(f"Return on Capital: {results['return_on_capital']:.2f}%")
    
    if results.get('var_95'):
        print(f"95% VaR: ${results['var_95']:,.2f}")
    if results.get('max_gain'):
        print(f"Max Gain: ${results['max_gain']:,.2f}")
    if results.get('max_loss'):
        print(f"Max Loss: ${results['max_loss']:,.2f}")
    
    print("\n" + "-"*60)
    print("OPTIMAL CALL POSITIONS TO SELL:")
    print("-"*60)
    
    if results['optimal_positions']:
        print(f"{'Strike':<10} {'Contracts':<12} {'Bid':<10} {'Delta':<10} {'Premium Collected':<20}")
        print("-"*60)
        
        total_premium = 0
        for detail in results['position_details']:
            if detail['quantity'] > 0:
                strike = detail['strike']
                qty = detail['quantity']
                bid = detail['bid']
                delta = detail['delta']
                premium = bid * 100 * qty
                total_premium += premium
                
                print(f"${strike:<9.2f} {qty:<12} ${bid:<9.2f} {delta:<10.4f} ${premium:<19,.2f}")
        
        print("-"*60)
        print(f"{'TOTAL':<34} ${total_premium:,.2f}")
    else:
        print("No optimal positions found")
    
    print("\n" + "="*60)
    print("DATA VALIDATION")
    print("="*60)
    
    # Validate we got real data
    if results.get('strikes') is not None and results.get('bids') is not None:
        strikes_with_bids = sum(1 for b in results['bids'] if b > 0)
        strikes_with_deltas = sum(1 for d in results['deltas'] if d > 0)
        
        print(f"Total strikes analyzed: {len(results['strikes'])}")
        print(f"Strikes with bid prices: {strikes_with_bids}")
        print(f"Strikes with delta values: {strikes_with_deltas}")
        
        # Show a sample of actual data
        print("\nSample of live data (first 5 ATM strikes):")
        stock_price = results['current_stock_price']
        atm_strikes = [(i, s) for i, s in enumerate(results['strikes']) 
                       if abs(s - stock_price) < 20][:5]
        
        for idx, strike in atm_strikes:
            bid = results['bids'].iloc[idx]
            delta = results['deltas'].iloc[idx]
            print(f"  Strike ${strike:.2f}: Bid=${bid:.2f}, Delta={delta:.4f}")
    
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)
    print(results['recommendation'])
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("1. Ensure IB Gateway is running")
    print("2. Market should be open (9:30 AM - 4:00 PM ET)")
    print("3. Check your OPRA subscription is active")

print("\n" + "="*60)
print("TEST COMPLETED")
print("="*60)