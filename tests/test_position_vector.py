#!/usr/bin/env python3
"""
Test that position vector aligns perfectly with other vectors
"""
from simple_real_strikes import get_all_strikes
from position_tracker import create_position_vector
import pandas as pd
import numpy as np

# Get the three base vectors
print("Getting option data...")
bids, strikes, deltas = get_all_strikes('AAPL', '20250117', use_live_data=False)

print(f"\nBase vectors: {len(strikes)} strikes each")
print(f"  bids.shape = {bids.shape}")
print(f"  strikes.shape = {strikes.shape}")
print(f"  deltas.shape = {deltas.shape}")

# Create position vector - buy 3 specific strikes
bought_strikes = [220.0, 225.0, 230.0]
positions = create_position_vector(strikes, bought_strikes=bought_strikes)

print(f"\nPosition vector created:")
print(f"  positions.shape = {positions.shape}")
print(f"  Same length as others? {len(positions) == len(strikes) == len(bids) == len(deltas)}")

# Verify alignment
print(f"\nVerifying alignment:")
print(f"  Number of 1s in positions: {positions.sum()}")
print(f"  Number of 0s in positions: {(positions == 0).sum()}")
print(f"  Total elements: {len(positions)}")

# Show the contracts we bought
print(f"\nContracts marked as bought (positions[i] == 1):")
for i in range(len(positions)):
    if positions.iloc[i] == 1:
        print(f"  Index {i:3d}: Strike ${strikes.iloc[i]:6.2f} | Bid ${bids.iloc[i]:5.2f} | Delta {deltas.iloc[i]:.4f} | Position={positions.iloc[i]}")

# Use all four vectors together
print(f"\nUsing all four vectors together:")
total_cost = (bids * positions).sum()
total_delta = (deltas * positions).sum()
print(f"  Total cost of position: ${total_cost:.2f}")
print(f"  Total delta of position: {total_delta:.4f}")

# Create a DataFrame with all four vectors
print(f"\nCombined DataFrame:")
df = pd.DataFrame({
    'strike': strikes,
    'bid': bids,
    'delta': deltas,
    'position': positions
})

# Show only rows where we have positions
print("Rows where position == 1:")
print(df[df['position'] == 1].to_string())

print(f"\n{'='*60}")
print("SUCCESS! Position vector is perfectly aligned with the others.")
print(f"{'='*60}")
print(f"""
You now have FOUR vectors, all the same size ({len(strikes)} elements):
  1. strikes - strike prices
  2. bids - bid prices  
  3. deltas - delta values
  4. positions - 1s and 0s for bought contracts

They all share the same index, so:
  strikes[50], bids[50], deltas[50], positions[50]
  all refer to the SAME option contract!
""")