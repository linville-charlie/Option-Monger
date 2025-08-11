#!/usr/bin/env python3
"""
Test OTM sale calculation with Hadamard multiplication
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from YOUR_MAIN_INTERFACE import (
    get_option_data, 
    create_positions, 
    create_itm_mask,
    calculate_otm_sale_proceeds,
    calculate_pnl_with_otm_sale
)
import numpy as np

print("OTM SALE CALCULATION TEST")
print("="*70)

# Get option data
print("\n1. Getting option data...")
bids, strikes, deltas = get_option_data('AAPL', '20250117', use_live_data=False)
print(f"   Got {len(strikes)} strikes")

# Create positions
print("\n2. Creating positions...")
positions = create_positions(strikes, {
    215.0: 2,   # Buy 2 contracts at 215
    220.0: 5,   # Buy 5 contracts at 220
    225.0: 10,  # Buy 10 contracts at 225
    230.0: 3,   # Buy 3 contracts at 230
    235.0: 1    # Buy 1 contract at 235
})
print(f"   Total contracts bought: {positions.sum()}")

# Show costs
print("\n3. Position costs:")
for strike in [215.0, 220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    qty = positions.iloc[idx]
    cost = qty * bids.iloc[idx] * 100
    print(f"   Strike ${strike:.2f}: {qty:2d} contracts × ${bids.iloc[idx]:.2f} = ${cost:,.2f}")

total_cost = (positions * bids * 100).sum()
print(f"   Total premium paid: ${total_cost:,.2f}")

# Scenario: Stock at 227.50
expiration_price = 227.50
print(f"\n4. Scenario: Stock expires at ${expiration_price:.2f}")

# Determine ITM/OTM
itm = create_itm_mask(strikes, expiration_price)
print("\n   Position status:")
for strike in [215.0, 220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    status = "ITM" if itm.iloc[idx] == 1 else "OTM"
    qty = positions.iloc[idx]
    print(f"   Strike ${strike:.2f}: {qty:2d} contracts - {status}")

# Calculate OTM sale proceeds
otm_sale_price = 0.50  # Sell each OTM contract for $0.50
print(f"\n5. Selling OTM contracts for ${otm_sale_price:.2f} each")

sale_proceeds = calculate_otm_sale_proceeds(
    positions, strikes, 
    expiration_price=expiration_price,
    sale_price_per_contract=otm_sale_price
)

# Show OTM sales
print("\n   OTM sale breakdown:")
otm_mask = 1 - itm
for strike in [215.0, 220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    if otm_mask.iloc[idx] == 1 and positions.iloc[idx] > 0:
        proceeds = sale_proceeds.iloc[idx]
        qty = positions.iloc[idx]
        print(f"   Strike ${strike:.2f}: {qty} contracts × ${otm_sale_price:.2f} × 100 = ${proceeds:.2f}")

total_otm_proceeds = sale_proceeds.sum()
print(f"\n   Total OTM sale proceeds: ${total_otm_proceeds:.2f}")

# Compare P&L with and without OTM sale
print("\n6. P&L Comparison")
print("   " + "-"*50)

# Without selling OTM
results_no_sale = calculate_pnl_with_otm_sale(
    positions, bids, strikes,
    hit_price=expiration_price,
    otm_sale_price=0  # Don't sell OTM
)

print("   WITHOUT selling OTM contracts:")
print(f"     Premium paid: ${results_no_sale['total_premium_paid']:,.2f}")
print(f"     ITM intrinsic received: ${results_no_sale['itm_intrinsic_received']:,.2f}")
print(f"     Total P&L: ${results_no_sale['total_pnl_without_sale']:,.2f}")

# With selling OTM
results_with_sale = calculate_pnl_with_otm_sale(
    positions, bids, strikes,
    hit_price=expiration_price,
    otm_sale_price=otm_sale_price
)

print("\n   WITH selling OTM contracts:")
print(f"     Premium paid: ${results_with_sale['total_premium_paid']:,.2f}")
print(f"     ITM intrinsic received: ${results_with_sale['itm_intrinsic_received']:,.2f}")
print(f"     OTM sale proceeds: ${results_with_sale['otm_sale_proceeds']:,.2f}")
print(f"     Total P&L: ${results_with_sale['total_pnl_with_sale']:,.2f}")

print(f"\n   P&L improvement from selling OTM: ${results_with_sale['pnl_improvement_from_sale']:,.2f}")

# Test different OTM sale prices
print("\n7. OTM Sale Price Sensitivity")
print("   " + "-"*50)

sale_prices = [0, 0.10, 0.25, 0.50, 0.75, 1.00]
print("   Sale Price | OTM Proceeds | Total P&L | Improvement")
print("   " + "-"*50)

for price in sale_prices:
    results = calculate_pnl_with_otm_sale(
        positions, bids, strikes,
        hit_price=expiration_price,
        otm_sale_price=price
    )
    proceeds = results['otm_sale_proceeds']
    pnl = results['total_pnl_with_sale']
    improvement = results['pnl_improvement_from_sale']
    
    print(f"   ${price:4.2f}      | ${proceeds:8.2f}    | ${pnl:9.2f} | ${improvement:8.2f}")

# Verify Hadamard multiplication
print("\n8. Hadamard Multiplication Verification")
print("   " + "-"*50)

# Manual calculation: positions ⊙ (1 - itm) × sale_price × 100
otm = 1 - itm
manual_calc = positions * otm * otm_sale_price * 100

# Compare with function result
sale_proceeds_func = calculate_otm_sale_proceeds(
    positions, strikes,
    expiration_price=expiration_price,
    sale_price_per_contract=otm_sale_price
)

print(f"   Manual calculation total: ${manual_calc.sum():.2f}")
print(f"   Function result total: ${sale_proceeds_func.sum():.2f}")
print(f"   Results match: {np.allclose(manual_calc, sale_proceeds_func)}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
The calculate_otm_sale_proceeds() function performs:
  positions ⊙ (1 - itm) × sale_price × 100

Where:
  - positions: Your quantities at each strike
  - (1 - itm): Binary mask for OTM strikes
  - sale_price: Price per contract you sell for
  - 100: Contract multiplier

This allows you to capture value from OTM options before they expire worthless!
""")