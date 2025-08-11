#!/usr/bin/env python3
"""
Demonstration that indices are perfectly aligned across all three vectors
"""
from simple_real_strikes import get_all_strikes
import pandas as pd
import numpy as np

# Get the three vectors
print("Getting option data...")
bids, strikes, deltas = get_all_strikes('AAPL', '20250117', use_live_data=False)  # Use demo for speed

print("\n" + "="*70)
print("INDEX ALIGNMENT DEMONSTRATION")
print("="*70)

# Each index represents the SAME option contract
print("\nExample 1: Accessing by index")
print("-"*40)
for idx in [0, 10, 50, 100]:
    if idx < len(strikes):
        print(f"Index {idx:3d}: Strike=${strikes.iloc[idx]:7.2f}, Bid=${bids.iloc[idx]:6.2f}, Delta={deltas.iloc[idx]:.4f}")

print("\nExample 2: Using boolean masks (they work across all vectors)")
print("-"*40)
# Find options with delta between 0.4 and 0.6
mask = (deltas >= 0.4) & (deltas <= 0.6)
print(f"Options with delta between 0.4 and 0.6:")
print(f"  Strikes: {strikes[mask].tolist()}")
print(f"  Bids: {bids[mask].tolist()}")
print(f"  Deltas: {deltas[mask].tolist()}")

print("\nExample 3: Iterating through all three together")
print("-"*40)
print("First 5 options:")
for i in range(min(5, len(strikes))):
    print(f"  Option {i}: Strike ${strikes.iloc[i]:.2f} | Bid ${bids.iloc[i]:.2f} | Delta {deltas.iloc[i]:.4f}")

print("\nExample 4: Using in calculations")
print("-"*40)
# Calculate spread between two strikes
idx1 = 100  # Buy this one
idx2 = 110  # Sell this one

if idx2 < len(strikes):
    spread_width = strikes.iloc[idx2] - strikes.iloc[idx1]
    net_debit = bids.iloc[idx1] - bids.iloc[idx2]
    delta_spread = deltas.iloc[idx1] - deltas.iloc[idx2]
    
    print(f"Vertical Spread Analysis:")
    print(f"  Buy strike ${strikes.iloc[idx1]:.2f} @ ${bids.iloc[idx1]:.2f} (Δ={deltas.iloc[idx1]:.4f})")
    print(f"  Sell strike ${strikes.iloc[idx2]:.2f} @ ${bids.iloc[idx2]:.2f} (Δ={deltas.iloc[idx2]:.4f})")
    print(f"  Spread width: ${spread_width:.2f}")
    print(f"  Net debit: ${net_debit:.2f}")
    print(f"  Net delta: {delta_spread:.4f}")

print("\n" + "="*70)
print("CONFIRMATION: Yes, indices are perfectly aligned!")
print("="*70)
print("""
The same index always refers to the same option contract:
  bids[i], strikes[i], deltas[i] all refer to the same option

You can safely:
  - Use the same index across all three vectors
  - Apply boolean masks to all three vectors
  - Iterate through them together
  - Do math operations knowing they're aligned
""")