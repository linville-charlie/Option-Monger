#!/usr/bin/env python3
"""
Test the simplified one-step optimization function
"""
from YOUR_MAIN_INTERFACE import find_best_options
import json

print("ONE-STEP OPTIMIZATION TEST")
print("="*70)

# Test 1: Small capital with fast optimization
print("\n1. Small Capital Test ($5,000)")
print("-"*50)

try:
    results = find_best_options(
        ticker='AAPL',
        expiration='20250117',
        capital=5000,
        use_live_data=False  # Use demo data
    )
    
    print(results['recommendation'])
    
    print(f"\nDetails:")
    print(f"  Total contracts: {results['total_contracts']}")
    print(f"  Number of strikes: {results['n_positions']}")
    print(f"  Capital remaining: ${results['capital_remaining']:,.2f}")
    
except Exception as e:
    print(f"Error: {e}")

# Test 2: Medium capital with balanced optimization
print("\n2. Medium Capital Test ($15,000)")
print("-"*50)

try:
    results = find_best_options(
        ticker='SPY',
        expiration='20250117',
        capital=15000,
        use_live_data=False
    )
    
    print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
    print(f"Win Rate: {results['win_rate']:.1f}%")
    print(f"Capital Used: ${results['capital_used']:,.2f}")
    
    print("\nOptimal Positions:")
    for strike, qty in results['optimal_positions'].items():
        print(f"  ${strike:.2f}: {qty} contracts")
    
except Exception as e:
    print(f"Error: {e}")

# Test 3: Large capital with thorough optimization
print("\n3. Large Capital Test ($50,000)")
print("-"*50)

try:
    results = find_best_options(
        ticker='AAPL',
        expiration='20250117',
        capital=50000,
        optimization_method='thorough',
        use_live_data=False
    )
    
    print(f"Optimization method used: {results['optimization_method']}")
    print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
    print(f"95% VaR: ${results['var_95']:,.2f}")
    
    # Show position details
    print("\nPosition Details:")
    for detail in results['position_details'][:5]:  # Show top 5
        print(f"  Strike ${detail['strike']:.2f}:")
        print(f"    Quantity: {detail['quantity']}")
        print(f"    Delta: {detail['delta']:.2f}")
        print(f"    ITM Probability: {detail['itm_probability']:.1f}%")
        print(f"    Cost: ${detail['cost']:,.2f}")
    
except Exception as e:
    print(f"Error: {e}")

# Test 4: Compare optimization methods
print("\n4. Comparing Optimization Methods")
print("-"*50)

capital = 10000
methods = ['fast', 'thorough']

for method in methods:
    try:
        results = find_best_options(
            ticker='AAPL',
            expiration='20250117',
            capital=capital,
            optimization_method=method,
            n_simulations=100,  # Keep low for speed
            use_live_data=False
        )
        
        print(f"\n{method.upper()} Method:")
        print(f"  Expected P&L: ${results['expected_pnl']:,.2f}")
        print(f"  Win Rate: {results['win_rate']:.1f}%")
        print(f"  Positions: {len(results['optimal_positions'])} strikes")
        print(f"  Total contracts: {results['total_contracts']}")
        
    except Exception as e:
        print(f"  Error with {method}: {e}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
The find_best_options() function provides a simple interface for
option portfolio optimization. Just provide:
- ticker: Stock symbol
- expiration: Date in YYYYMMDD format
- capital: Amount to invest

The function automatically:
1. Fetches option data
2. Chooses optimization method based on capital
3. Runs Monte Carlo simulations
4. Returns optimal positions with analysis

Example usage:
    results = find_best_options('AAPL', '20250117', 10000)
    positions = results['optimal_positions']
""")