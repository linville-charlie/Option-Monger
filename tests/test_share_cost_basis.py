#!/usr/bin/env python3
"""
Test share cost basis calculation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from YOUR_MAIN_INTERFACE import (
    get_option_data,
    create_positions,
    calculate_initial_share_cost,
    calculate_covered_call_total_pnl
)
import numpy as np

print("SHARE COST BASIS CALCULATION TEST")
print("="*70)

# Get option data
print("\n1. Getting option data...")
bids, strikes, deltas = get_option_data('AAPL', '20250117', use_live_data=False)
print(f"   Got {len(strikes)} strikes")

# Create positions
print("\n2. Creating covered call positions...")
positions = create_positions(strikes, {
    220.0: 5,   # 5 contracts at 220
    225.0: 10,  # 10 contracts at 225
    230.0: 2,   # 2 contracts at 230
    235.0: 1    # 1 contract at 235
})
print(f"   Total contracts: {positions.sum()}")

# Calculate share cost basis
initial_price = 200.0  # Bought shares at $200 each
print(f"\n3. Calculating cost basis (bought shares at ${initial_price:.2f})")

cost_basis = calculate_initial_share_cost(positions, purchase_price=initial_price)

# Show cost breakdown
print("\n   Cost basis breakdown:")
print("   Formula: positions × initial_price × 100")
print("   " + "-"*50)

for strike in [220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    qty = positions.iloc[idx]
    shares = qty * 100
    cost = cost_basis.iloc[idx]
    if qty > 0:
        print(f"   Strike ${strike:.2f}: {qty:2d} contracts × 100 × ${initial_price:.2f} = ${cost:,.2f}")
        print(f"                  ({shares:,} shares total)")

total_cost = cost_basis.sum()
total_shares = positions.sum() * 100
print(f"\n   Total shares: {total_shares:,}")
print(f"   Total cost basis: ${total_cost:,.2f}")
print(f"   Average per share: ${total_cost/total_shares:.2f}")

# Test different purchase prices
print("\n4. Testing Different Purchase Prices")
print("   " + "-"*50)

test_prices = [180.0, 200.0, 220.0, 240.0]
print("   Purchase Price | Total Cost Basis")
print("   " + "-"*35)

for price in test_prices:
    cost = calculate_initial_share_cost(positions, purchase_price=price)
    total = cost.sum()
    print(f"   ${price:6.2f}       | ${total:,.2f}")

# Complete covered call P&L example
print("\n5. Complete Covered Call P&L Analysis")
print("   " + "-"*50)

expiration_price = 227.50
print(f"   Initial share price: ${initial_price:.2f}")
print(f"   Expiration price: ${expiration_price:.2f}")

results = calculate_covered_call_total_pnl(
    positions, strikes, bids,
    initial_share_price=initial_price,
    expiration_price=expiration_price
)

print(f"\n   Investment:")
print(f"     Share cost basis: ${results['total_share_cost']:,.2f}")

print(f"\n   Income:")
print(f"     Premium collected: ${results['premium_collected']:,.2f}")
print(f"     ITM proceeds (called away): ${results['itm_proceeds']:,.2f}")
print(f"     OTM proceeds (sold at market): ${results['otm_proceeds']:,.2f}")

print(f"\n   Results:")
print(f"     Total proceeds: ${results['total_proceeds']:,.2f}")
print(f"     Net P&L: ${results['net_pnl']:,.2f}")
print(f"     Return: {results['return_pct']:.2f}%")

# Verify scalar multiplication
print("\n6. Scalar Multiplication Verification")
print("   " + "-"*50)

# Manual calculation: positions × initial_price × 100
manual_calc = positions * initial_price * 100

print(f"   Formula: positions × initial_price × 100")
print(f"   Manual calculation: ${manual_calc.sum():,.2f}")
print(f"   Function result: ${cost_basis.sum():,.2f}")
print(f"   Results match: {np.allclose(manual_calc, cost_basis)}")

# Show vector structure
print("\n7. Vector Structure")
print("   " + "-"*50)

print(f"   positions vector: {positions[positions > 0].to_dict()}")
print(f"   cost_basis vector sum: ${cost_basis.sum():,.2f}")
print(f"   Non-zero entries: {(cost_basis > 0).sum()}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
The calculate_initial_share_cost() function performs:
  positions × initial_share_price × 100

This gives you the total cost basis for shares underlying your options.

Perfect for:
- Covered calls: Cost of shares you bought to cover
- Long calls: Cost if you exercise and buy shares
- P&L calculations: Compare cost basis to proceeds
""")