#!/usr/bin/env python3
"""
Test the ITM (in-the-money) vector creation
"""
from simple_real_strikes import get_all_strikes
from position_tracker import (create_position_vector, create_itm_vector, 
                             create_exercise_vector, calculate_expiration_value)
import numpy as np

print("ITM VECTOR DEMONSTRATION")
print("="*70)

# Get the base vectors
print("\n1. Getting option data...")
bids, strikes, deltas = get_all_strikes('AAPL', '20250117', use_live_data=False)
print(f"   Got {len(strikes)} strikes from ${strikes.min():.2f} to ${strikes.max():.2f}")

# Create position vector - bought some calls
bought_strikes = [215.0, 220.0, 225.0, 230.0, 235.0]
positions = create_position_vector(strikes, bought_strikes=bought_strikes)
print(f"\n2. Your positions: Bought calls at {bought_strikes}")

# Scenario 1: Stock hits 227.50 at expiration
hit_price = 227.50
print(f"\n3. Scenario: Stock expires at ${hit_price:.2f}")

# Create ITM vector
itm = create_itm_vector(strikes, hit_strike=hit_price)
print(f"   ITM strikes (calls): {itm.sum()} out of {len(strikes)}")
print(f"   ITM range: ${strikes[itm == 1].min():.2f} to ${strikes[itm == 1].max():.2f}")

# Show which of YOUR positions are ITM
exercised = create_exercise_vector(strikes, positions, hit_strike=hit_price)
print(f"\n4. Your positions that will be exercised:")
for i in range(len(strikes)):
    if exercised.iloc[i] == 1:
        intrinsic = max(0, hit_price - strikes.iloc[i])
        profit = intrinsic - bids.iloc[i]
        print(f"   Strike ${strikes.iloc[i]:.2f}: Intrinsic=${intrinsic:.2f}, Paid=${bids.iloc[i]:.2f}, P&L=${profit:.2f}")

# Calculate total P&L
results = calculate_expiration_value(strikes, bids, positions, hit_price)
print(f"\n5. Expiration P&L Summary:")
print(f"   Stock closed at: ${results['hit_strike']:.2f}")
print(f"   ITM positions: {results['itm_positions']} out of {int(results['total_positions'])}")
print(f"   Exercised strikes: {results['exercised_strikes']}")
print(f"   Total P&L: ${results['total_pnl']:.2f}")

# Test different scenarios
print("\n" + "="*70)
print("TESTING MULTIPLE SCENARIOS")
print("="*70)

scenarios = [220.0, 225.0, 230.0, 235.0, 240.0]
print(f"\nYour positions: {bought_strikes}")
print("\nP&L at different expiration prices:")
print("-"*40)

for scenario_price in scenarios:
    itm = create_itm_vector(strikes, hit_strike=scenario_price)
    exercised = positions * itm  # Which of your positions are ITM
    
    # Calculate P&L
    intrinsic_values = np.maximum(scenario_price - strikes, 0)
    position_pnl = positions * (intrinsic_values - bids)
    total_pnl = position_pnl.sum()
    
    itm_count = exercised.sum()
    print(f"Stock at ${scenario_price:.2f}: {itm_count} ITM, P&L = ${total_pnl:.2f}")

# Show the vector usage
print("\n" + "="*70)
print("HOW TO USE ITM VECTORS")
print("="*70)

print("""
# Create ITM vector for any strike price
hit_price = 227.50
itm = create_itm_vector(strikes, hit_strike=hit_price)

# itm[i] = 1 for all strikes at or below hit_price (for calls)
# itm[i] = 0 for all strikes above hit_price

# Combine with your positions to see what gets exercised
exercised = positions * itm

# Calculate intrinsic value at expiration
intrinsic = np.maximum(hit_price - strikes, 0) * itm

# Calculate P&L
pnl = positions * (intrinsic - bids)
total_pnl = pnl.sum()

# Find all ITM strikes
itm_strikes = strikes[itm == 1]
print(f"ITM strikes: {itm_strikes.tolist()}")
""")