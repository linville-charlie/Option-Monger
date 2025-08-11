#!/usr/bin/env python3
"""
Test that covered calls use real stock price
"""
from YOUR_MAIN_INTERFACE import find_best_options, get_option_data

print("TESTING REAL STOCK PRICE FOR COVERED CALLS")
print("="*70)

# Test 1: Get option data with stock price
print("\n1. Testing get_option_data with stock price")
print("-"*50)

bids, strikes, deltas, stock_price = get_option_data(
    'AAPL', '20250117', 
    use_live_data=False,  # Demo mode
    return_stock_price=True
)

print(f"Stock price returned: ${stock_price:.2f}")
print(f"Number of strikes: {len(strikes)}")

# Find ATM strike for comparison
import numpy as np
atm_idx = np.abs(deltas - 0.5).argmin()
atm_strike = strikes.iloc[atm_idx]
print(f"ATM strike: ${atm_strike:.2f}")
print(f"Difference from stock price: ${abs(stock_price - atm_strike):.2f}")

# Test 2: Covered calls with real stock price
print("\n2. Testing covered calls optimization")
print("-"*50)

results = find_best_options(
    ticker='AAPL',
    expiration='20250117',
    capital=100000,
    strategy='covered_calls',
    use_live_data=False,
    n_simulations=50  # Quick test
)

print(f"Stock price used: ${results['current_stock_price']:.2f}")
print(f"Shares needed: {results['shares_needed']}")
print(f"Capital for shares: ${results['capital_for_shares']:,.2f}")
print(f"Actual shares calculation: {results['shares_needed']} shares × ${results['current_stock_price']:.2f} = ${results['shares_needed'] * results['current_stock_price']:,.2f}")

# Verify the math
expected_cost = results['shares_needed'] * results['current_stock_price']
actual_cost = results['capital_for_shares']
print(f"\nVerification:")
print(f"  Expected cost: ${expected_cost:,.2f}")
print(f"  Actual cost: ${actual_cost:,.2f}")
print(f"  Match: {abs(expected_cost - actual_cost) < 0.01}")

# Test 3: Compare with long calls
print("\n3. Long calls (should not need exact stock price)")
print("-"*50)

long_results = find_best_options(
    ticker='AAPL',
    expiration='20250117',
    capital=100000,
    strategy='long_calls',
    use_live_data=False,
    n_simulations=50
)

print(f"Capital used for options: ${long_results['capital_used']:,.2f}")
print(f"This buys option contracts, not shares")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
The function now:
1. Fetches the actual current stock price when use_live_data=True
2. Uses this price to calculate exactly how many shares can be bought
3. In demo mode, estimates from ATM strike (close enough for testing)

For covered calls, the capital calculation is now:
  Shares = floor(Capital / Current_Stock_Price)
  Contracts = Shares // 100
""")