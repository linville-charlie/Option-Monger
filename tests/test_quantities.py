#!/usr/bin/env python3
"""
Test position vectors with quantities (not just binary)
"""
from simple_real_strikes import get_all_strikes
from position_tracker import (create_position_vector, create_itm_vector,
                             calculate_premium_paid_for_itm, 
                             calculate_net_pnl_vectors)
import pandas as pd
import numpy as np

print("POSITION VECTORS WITH QUANTITIES")
print("="*70)

# Get the base vectors
print("\n1. Setting up option data...")
bids, strikes, deltas = get_all_strikes('AAPL', '20250117', use_live_data=False)
print(f"   Got {len(strikes)} strikes")

# Example 1: Single quantity for all positions
print("\n2. Example: Buy 3 contracts each at multiple strikes")
positions = create_position_vector(strikes, 
                                  bought_strikes=[220.0, 225.0, 230.0],
                                  quantities=3)
print(f"   Position vector sum: {positions.sum()} total contracts")
for strike in [220.0, 225.0, 230.0]:
    idx = np.abs(strikes - strike).argmin()
    print(f"   Strike ${strike:.2f}: {positions.iloc[idx]} contracts @ ${bids.iloc[idx]:.2f} each = ${positions.iloc[idx] * bids.iloc[idx] * 100:.2f} total")

# Example 2: Different quantities for each strike
print("\n3. Example: Buy different quantities at each strike")
positions = create_position_vector(strikes,
                                  bought_strikes=[220.0, 225.0, 230.0],
                                  quantities=[2, 5, 1])
print(f"   Position vector sum: {positions.sum()} total contracts")
for strike in [220.0, 225.0, 230.0]:
    idx = np.abs(strikes - strike).argmin()
    print(f"   Strike ${strike:.2f}: {positions.iloc[idx]} contracts @ ${bids.iloc[idx]:.2f} each = ${positions.iloc[idx] * bids.iloc[idx] * 100:.2f} total")

# Example 3: Using dict notation (most flexible)
print("\n4. Example: Using dict to specify quantities")
positions = create_position_vector(strikes,
                                  bought_strikes={
                                      215.0: 1,   # Buy 1 contract at 215
                                      220.0: 10,  # Buy 10 contracts at 220
                                      225.0: 5,   # Buy 5 contracts at 225
                                      230.0: 2,   # Buy 2 contracts at 230
                                      235.0: 1    # Buy 1 contract at 235
                                  })
print(f"   Position vector sum: {positions.sum()} total contracts")
print("\n   Position breakdown:")
for strike in [215.0, 220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    qty = positions.iloc[idx]
    if qty > 0:
        total_premium = qty * bids.iloc[idx] * 100
        print(f"   Strike ${strike:.2f}: {qty:2d} contracts × ${bids.iloc[idx]:.2f} = ${total_premium:,.2f}")

# Calculate P&L with quantities
print("\n5. P&L Calculation with Quantities")
print("   " + "="*50)

hit_price = 227.50
itm = create_itm_vector(strikes, hit_strike=hit_price)

# Calculate premium paid for ITM positions (with quantities)
premium_paid = calculate_premium_paid_for_itm(positions, itm, bids)

print(f"   Stock expires at ${hit_price:.2f}")
print("\n   ITM positions and premiums paid:")
for strike in [215.0, 220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    if positions.iloc[idx] > 0:
        itm_status = "ITM" if itm.iloc[idx] == 1 else "OTM"
        premium = premium_paid.iloc[idx]
        print(f"   Strike ${strike:.2f}: {positions.iloc[idx]:2d} contracts - {itm_status} - Premium paid: ${premium:,.2f}")

total_premium_all = (positions * bids * 100).sum()
total_premium_itm = premium_paid.sum()
print(f"\n   Total premium paid (all): ${total_premium_all:,.2f}")
print(f"   Total premium paid (ITM only): ${total_premium_itm:,.2f}")

# Calculate intrinsic value received
intrinsic_per_share = np.maximum(hit_price - strikes, 0)
intrinsic_received = positions * itm * intrinsic_per_share * 100
total_intrinsic = intrinsic_received.sum()

print(f"   Total intrinsic value received: ${total_intrinsic:,.2f}")
print(f"   Net P&L: ${total_intrinsic - total_premium_all:,.2f}")

# Show DataFrame with all calculations
print("\n6. Detailed Position Analysis")
print("   " + "="*50)

# Create DataFrame for positions we own
owned_mask = positions > 0
df = pd.DataFrame({
    'strike': strikes[owned_mask],
    'quantity': positions[owned_mask],
    'bid': bids[owned_mask],
    'total_premium': (positions * bids * 100)[owned_mask],
    'itm': itm[owned_mask],
    'premium_if_itm': premium_paid[owned_mask],
    'intrinsic_received': intrinsic_received[owned_mask],
    'pnl': (intrinsic_received - positions * bids * 100)[owned_mask]
})

print(df.to_string())

# Example with large position
print("\n7. Large Position Example")
print("   " + "="*50)

# Buy 100 contracts at ATM
atm_idx = np.abs(deltas - 0.5).argmin()
atm_strike = strikes.iloc[atm_idx]

positions_large = create_position_vector(strikes, bought_strikes={atm_strike: 100})

print(f"   Bought 100 contracts at ATM strike ${atm_strike:.2f}")
print(f"   Premium per contract: ${bids.iloc[atm_idx]:.2f}")
print(f"   Total premium paid: ${100 * bids.iloc[atm_idx] * 100:,.2f}")

# Test at different expiration prices
print("\n   P&L at different expiration prices:")
for scenario in [atm_strike - 5, atm_strike, atm_strike + 5, atm_strike + 10]:
    itm_scenario = create_itm_vector(strikes, hit_strike=scenario)
    intrinsic = max(0, scenario - atm_strike) * 100 * 100  # 100 contracts × 100 shares
    premium = 100 * bids.iloc[atm_idx] * 100
    pnl = intrinsic - premium
    status = "ITM" if scenario > atm_strike else "ATM" if scenario == atm_strike else "OTM"
    print(f"   Stock at ${scenario:.2f} ({status}): P&L = ${pnl:,.2f}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
Position vectors now support quantities (0, 1, 2, 3, ...)!

Three ways to specify quantities:
1. Single quantity for all: quantities=5
2. List of quantities: quantities=[2, 5, 1]  
3. Dict notation: bought_strikes={220.0: 2, 225.0: 5, 230.0: 1}

The calculations work seamlessly:
- positions × itm × bids × 100 = premium paid for ITM positions
- Automatically handles different quantities per strike
- Total P&L accounts for all contract quantities
""")