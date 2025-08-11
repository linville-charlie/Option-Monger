#!/usr/bin/env python3
"""
Test the find_best_options function
"""
from YOUR_MAIN_INTERFACE import find_best_options
import json

print("="*60)
print("Testing find_best_options() - Covered Call Optimization")
print("="*60)

# Test parameters
ticker = "AAPL"
expiration = "20250815"  # August 15, 2025 (Friday after tomorrow)
capital = 100000  # $100,000 to invest

print(f"\nParameters:")
print(f"  Ticker: {ticker}")
print(f"  Expiration: {expiration}")
print(f"  Capital: ${capital:,}")
print(f"  Strategy: Covered Calls (buy shares, sell calls)")

print("\nRunning optimization...")
print("-"*60)

try:
    # Run the optimization
    results = find_best_options(
        ticker=ticker,
        expiration=expiration,
        capital=capital,
        max_contracts_per_strike=50,
        n_simulations=200,
        optimization_method='auto',
        use_live_data=True  # Use real IBKR data
    )
    
    print("\n" + "="*60)
    print("OPTIMIZATION RESULTS")
    print("="*60)
    
    # Display results
    print(f"\nShares to Buy: {results['shares_needed']:,}")
    print(f"Share Purchase Cost: ${results['capital_for_shares']:,.2f}")
    print(f"Premium Collected: ${results['premium_collected']:,.2f}")
    print(f"Net Investment: ${results['net_capital_after_premium']:,.2f}")
    
    print(f"\nExpected P&L: ${results['expected_pnl']:,.2f}")
    print(f"Expected Return: {results['return_on_capital']:.2f}%")
    
    print(f"\nOptimization Method Used: {results['optimization_method']}")
    
    print("\n" + "-"*60)
    print("OPTIMAL POSITIONS (Calls to Sell):")
    print("-"*60)
    
    if results['optimal_positions']:
        print(f"{'Strike':<10} {'Contracts':<12} {'Premium/Contract':<18} {'Total Premium':<15} {'Delta':<10}")
        print("-"*60)
        
        for strike, contracts in results['optimal_positions'].items():
            if contracts > 0:
                # Get the bid and delta for this strike from position_details
                detail = next((d for d in results['position_details'] if d['strike'] == strike), None)
                if detail:
                    bid = detail['bid']
                    delta = detail['delta']
                else:
                    # Fallback to finding in arrays
                    idx = list(results['strikes']).index(strike)
                    bid = results['bids'].iloc[idx]
                    delta = results['deltas'].iloc[idx]
                
                premium_per_contract = bid * 100
                total_premium = premium_per_contract * contracts
                
                print(f"${strike:<9.2f} {contracts:<12} ${premium_per_contract:<17.2f} ${total_premium:<14.2f} {delta:<10.3f}")
    else:
        print("No optimal positions found - check if market is open and data is available")
    
    print("\n" + "="*60)
    print("RISK ANALYSIS")
    print("="*60)
    
    # Calculate some risk metrics
    if results['optimal_positions']:
        total_contracts = sum(results['optimal_positions'].values())
        shares_covered = total_contracts * 100
        
        print(f"\nTotal Contracts: {total_contracts}")
        print(f"Shares Covered: {shares_covered:,}")
        print(f"Coverage Ratio: {shares_covered}/{results['shares_needed']} = {shares_covered/results['shares_needed']:.1%}")
        
        # Show strike distribution
        strikes_used = [s for s, c in results['optimal_positions'].items() if c > 0]
        if strikes_used:
            print(f"\nStrike Range: ${min(strikes_used):.2f} - ${max(strikes_used):.2f}")
            print(f"Number of Different Strikes: {len(strikes_used)}")
    
    # Show debug info if needed
    if 'error' in results:
        print(f"\n⚠️ Warning: {results['error']}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure IB Gateway is running on port 8000")
    print("2. Check that market is open (or use use_live_data=False for demo)")
    print("3. Verify you have market data subscriptions")
    print("4. Try with a different ticker or expiration date")