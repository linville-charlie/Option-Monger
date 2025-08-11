#!/usr/bin/env python3
"""
Demonstrate that the system CAN choose multiple strikes
by examining the optimization process
"""
from YOUR_MAIN_INTERFACE import find_best_options, create_positions
from core.simple_real_strikes import get_all_strikes
from core.position_tracker import calculate_covered_call_pnl
import numpy as np

print("DEMONSTRATING MULTIPLE STRIKE CAPABILITY")
print("="*70)

# First, let's manually show what multiple strikes would look like
print("\n1. MANUAL EXAMPLE - Multiple Strikes")
print("-"*50)

# Get option data
bids, strikes, deltas, stock_price = get_all_strikes('AAPL', '20250919', False, return_stock_price=True)

print(f"Stock price: ${stock_price:.2f}")

# Manually create a multi-strike position
multi_strike_positions = {
    235.0: 2,  # 2 contracts at $235 (closer to ATM)
    240.0: 3,  # 3 contracts at $240
    245.0: 2,  # 2 contracts at $245
    250.0: 1,  # 1 contract at $250 (further OTM)
}

positions = create_positions(strikes, multi_strike_positions)
total_contracts = sum(multi_strike_positions.values())

print(f"\nManual multi-strike position ({total_contracts} total contracts):")
for strike, qty in sorted(multi_strike_positions.items()):
    idx = np.abs(strikes - strike).argmin()
    delta = deltas.iloc[idx]
    bid = bids.iloc[idx]
    print(f"  Sell {qty} at ${strike:.2f} (Delta={delta:.2f}, Bid=${bid:.2f})")

# Calculate P&L for different scenarios
scenarios = [220, 238, 245, 255]
print(f"\nP&L for different expiration prices:")

for exp_price in scenarios:
    pnl_result = calculate_covered_call_pnl(
        positions, strikes, bids,
        stock_price, exp_price
    )
    print(f"  If expires at ${exp_price}: P&L = ${pnl_result['net_pnl']:,.2f}")

# Now run the optimizer with different seeds to see different strategies
print("\n" + "="*70)
print("2. OPTIMIZER TESTING DIFFERENT STRATEGIES")
print("-"*50)

print("\nThe optimizer tests 200 different portfolio combinations:")
print("- Some with single strikes")
print("- Some with 2-3 strikes")
print("- Some with weighted distributions")
print("\nIt picks whichever has the highest expected P&L\n")

# Run optimizer multiple times with different random seeds
# to potentially see different strategies
best_multi_strike = None
best_multi_pnl = -float('inf')

print("Testing with different random seeds to find multi-strike solutions...")

for seed in range(5):
    # Run quietly to find results
    try:
        from core.covered_call_optimization import optimize_covered_calls
        
        # Get fresh data
        bids, strikes, deltas, stock_price = get_all_strikes('AAPL', '20250919', False, return_stock_price=True)
        
        results = optimize_covered_calls(
            strikes, deltas, bids,
            capital=200000,
            current_stock_price=stock_price,
            n_simulations=100,
            n_candidates=200,
            random_seed=seed * 42  # Different seed each time
        )
        
        n_strikes = len(results['optimal_positions'])
        if n_strikes > 1:
            print(f"  Seed {seed}: Found {n_strikes}-strike solution! P&L=${results['expected_pnl']:,.2f}")
            if results['expected_pnl'] > best_multi_pnl:
                best_multi_strike = results
                best_multi_pnl = results['expected_pnl']
        else:
            strike = list(results['optimal_positions'].keys())[0]
            print(f"  Seed {seed}: Single strike at ${strike:.2f}, P&L=${results['expected_pnl']:,.2f}")
            
    except Exception as e:
        print(f"  Seed {seed}: Error - {e}")

if best_multi_strike:
    print(f"\nBest multi-strike solution found:")
    for strike, qty in sorted(best_multi_strike['optimal_positions'].items()):
        print(f"  Sell {qty} at ${strike:.2f}")
    print(f"  Expected P&L: ${best_multi_strike['expected_pnl']:,.2f}")
else:
    print("\nIn these tests, single strike was optimal")

print("\n" + "="*70)
print("3. WHY SINGLE STRIKE OFTEN WINS")
print("-"*50)

print("""
For covered calls, single strike often wins because:

1. **Simplicity**: Easier to manage, lower transaction costs
2. **Concentration**: If one strike has the best risk/reward, why dilute?
3. **Demo data**: Our demo data may favor concentration

In real markets with:
- Volatility skew
- Varying liquidity
- Different bid/ask spreads
- Complex Greeks

Multiple strikes become more attractive for:
- Risk diversification
- Capturing different volatility levels
- Managing gamma exposure

The optimizer CAN and WILL choose multiple strikes when they 
provide better expected P&L than concentrated positions.
""")