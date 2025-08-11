#!/usr/bin/env python3
"""
Test Hadamard multiplication for premium calculation
"""
from simple_real_strikes import get_all_strikes
from position_tracker import (create_position_vector, create_itm_vector,
                             calculate_premium_paid_for_itm, 
                             calculate_net_pnl_vectors,
                             hadamard_multiply)
import pandas as pd
import numpy as np

print("HADAMARD MULTIPLICATION FOR PREMIUM CALCULATION")
print("="*70)

# Get the base vectors
print("\n1. Setting up option data...")
bids, strikes, deltas = get_all_strikes('AAPL', '20250117', use_live_data=False)
print(f"   Got {len(strikes)} strikes")

# Create position vector - bought some calls
bought_strikes = [220.0, 225.0, 230.0]
positions = create_position_vector(strikes, bought_strikes=bought_strikes)
print(f"\n2. Your positions: Bought calls at {bought_strikes}")

# Find indices and show premiums
for strike in bought_strikes:
    idx = np.abs(strikes - strike).argmin()
    print(f"   Strike ${strike:.2f}: Bid = ${bids.iloc[idx]:.2f}, Premium = ${bids.iloc[idx] * 100:.2f}")

# Stock hits 227.50 at expiration
hit_price = 227.50
itm = create_itm_vector(strikes, hit_strike=hit_price)
print(f"\n3. Stock expires at ${hit_price:.2f}")
print(f"   ITM: 220.0 ✓, 225.0 ✓, 230.0 ✗")

# HADAMARD MULTIPLICATION: positions ⊙ itm ⊙ (bids × 100)
print("\n4. Hadamard Multiplication: positions ⊙ itm ⊙ (bids × 100)")
print("   "+"="*50)

premium_paid = calculate_premium_paid_for_itm(positions, itm, bids, contract_multiplier=100)

# Show the calculation step by step
print("   Element-wise multiplication:")
print("   positions × itm × (bids × 100) = premium_paid")
print("\n   For your positions:")

for strike in bought_strikes:
    idx = np.abs(strikes - strike).argmin()
    pos_val = positions.iloc[idx]
    itm_val = itm.iloc[idx]
    bid_val = bids.iloc[idx]
    result = premium_paid.iloc[idx]
    
    print(f"   Strike ${strike:.2f}: {pos_val} × {itm_val} × (${bid_val:.2f} × 100) = ${result:.2f}")

# Total premium for ITM positions
total_premium_itm = premium_paid.sum()
print(f"\n   Total premium paid for ITM contracts: ${total_premium_itm:.2f}")

# Show full P&L calculation
print("\n5. Complete P&L Calculation Using Vectors")
print("   "+"="*50)

results = calculate_net_pnl_vectors(positions, itm, strikes, bids, hit_price)

print(f"   Premium paid (all positions): ${results['total_premium_paid_all']:.2f}")
print(f"   Premium paid (ITM only): ${results['total_premium_paid_itm']:.2f}")
print(f"   Intrinsic value received: ${results['total_intrinsic_received']:.2f}")
print(f"   Net P&L: ${results['total_pnl']:.2f}")

# Show the vectors
print("\n6. Vector Details")
print("   "+"="*50)

# Create a DataFrame showing only positions you own
df_positions = pd.DataFrame({
    'strike': strikes[positions == 1],
    'bid': bids[positions == 1],
    'position': positions[positions == 1],
    'itm': itm[positions == 1],
    'premium_paid': premium_paid[positions == 1],
    'intrinsic_received': results['intrinsic_received_vector'][positions == 1],
    'pnl': results['pnl_vector'][positions == 1]
})

print(df_positions.to_string())

# Test the generic Hadamard multiply function
print("\n7. Using Generic Hadamard Multiply")
print("   "+"="*50)

# Three ways to get the same result
result1 = positions * itm * (bids * 100)
result2 = calculate_premium_paid_for_itm(positions, itm, bids)
result3 = hadamard_multiply(positions, itm, bids * 100)

print(f"   Method 1 (manual): Total = ${result1.sum():.2f}")
print(f"   Method 2 (function): Total = ${result2.sum():.2f}") 
print(f"   Method 3 (hadamard_multiply): Total = ${result3.sum():.2f}")
print(f"   All methods equal? {np.allclose(result1, result2) and np.allclose(result2, result3)}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
The function calculate_premium_paid_for_itm() performs:
  positions ⊙ itm ⊙ (bids × 100)

Where ⊙ is Hadamard (element-wise) multiplication.

This gives you a vector showing:
  - Premium paid for positions that ended up ITM
  - 0 for positions that ended up OTM
  - 0 for strikes you didn't buy

Usage:
  premium_paid = calculate_premium_paid_for_itm(positions, itm, bids)
  total = premium_paid.sum()
""")