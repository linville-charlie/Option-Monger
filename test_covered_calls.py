#!/usr/bin/env python3
"""
Test covered call optimization
"""
from YOUR_MAIN_INTERFACE import find_best_options

print("COVERED CALL OPTIMIZATION TEST")
print("="*70)

# Test 1: Small capital (enough for 1-2 contracts)
print("\n1. Small Capital Test ($25,000)")
print("-"*50)

try:
    results = find_best_options(
        ticker='AAPL',
        expiration='20250117',
        capital=25000,
        strategy='covered_calls',  # Explicitly set to covered calls
        use_live_data=False
    )
    
    print(results['recommendation'])
    
except Exception as e:
    print(f"Error: {e}")

# Test 2: Medium capital
print("\n2. Medium Capital Test ($100,000)")
print("-"*50)

try:
    results = find_best_options(
        ticker='SPY',
        expiration='20250117',
        capital=100000,
        strategy='covered_calls',
        use_live_data=False
    )
    
    print(f"\nKey Metrics:")
    print(f"  Shares to buy: {results['shares_needed']}")
    print(f"  Share cost: ${results['capital_for_shares']:,.2f}")
    print(f"  Premium collected: ${results['premium_collected']:,.2f}")
    print(f"  Net capital needed: ${results['net_capital_after_premium']:,.2f}")
    print(f"  Expected P&L: ${results['expected_pnl']:,.2f}")
    print(f"  Return on capital: {results['return_on_capital']:.2f}%")
    print(f"  Win rate: {results['win_rate']:.1f}%")
    
    print(f"\nCall positions to sell:")
    for strike, qty in results['optimal_positions'].items():
        print(f"  Sell {qty} calls at ${strike:.2f} strike")
    
except Exception as e:
    print(f"Error: {e}")

# Test 3: Large capital
print("\n3. Large Capital Test ($500,000)")
print("-"*50)

try:
    results = find_best_options(
        ticker='AAPL',
        expiration='20250117',
        capital=500000,
        strategy='covered_calls',
        optimization_method='thorough',
        use_live_data=False
    )
    
    print(f"Contracts to sell: {results['contracts_sold']}")
    print(f"Shares needed: {results['shares_needed']}")
    print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
    print(f"Max possible gain: ${results.get('max_gain', 0):,.2f}")
    print(f"Max possible loss: ${results.get('max_loss', 0):,.2f}")
    print(f"95% VaR: ${results.get('var_95', 0):,.2f}")
    
except Exception as e:
    print(f"Error: {e}")

# Test 4: Compare to long calls
print("\n4. Comparison: Covered Calls vs Long Calls")
print("-"*50)

capital = 50000

# Covered calls
try:
    covered_results = find_best_options(
        ticker='AAPL',
        expiration='20250117',
        capital=capital,
        strategy='covered_calls',
        n_simulations=100,
        use_live_data=False
    )
    
    print(f"COVERED CALLS with ${capital:,}:")
    print(f"  Shares to buy: {covered_results['shares_needed']}")
    print(f"  Calls to sell: {covered_results['contracts_sold']} contracts")
    print(f"  Premium collected: ${covered_results['premium_collected']:,.2f}")
    print(f"  Expected P&L: ${covered_results['expected_pnl']:,.2f}")
    print(f"  Win Rate: {covered_results['win_rate']:.1f}%")
    print(f"  Return on capital: {covered_results['return_on_capital']:.2f}%")
except Exception as e:
    print(f"  Error: {e}")

# Long calls
try:
    long_results = find_best_options(
        ticker='AAPL',
        expiration='20250117',
        capital=capital,
        strategy='long_calls',
        n_simulations=100,
        use_live_data=False
    )
    
    print(f"\nLONG CALLS with ${capital:,}:")
    print(f"  Contracts to buy: {long_results['total_contracts']}")
    print(f"  Capital used: ${long_results['capital_used']:,.2f}")
    print(f"  Expected P&L: ${long_results['expected_pnl']:,.2f}")
    print(f"  Win Rate: {long_results['win_rate']:.1f}%")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
The find_best_options() function now supports covered calls!

For covered calls:
- Your capital buys the underlying shares (100 per contract)
- The function finds optimal strikes to sell calls against
- Returns include premium collection and expected P&L

Usage:
    results = find_best_options(
        'AAPL', '20250117', 100000,
        strategy='covered_calls'
    )
    
    # Buy the shares
    print(f"Buy {results['shares_needed']} shares")
    
    # Sell the recommended calls
    print(f"Sell calls at: {results['optimal_positions']}")
""")