#!/usr/bin/env python3
"""
Test covered call OTM share sale calculation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from YOUR_MAIN_INTERFACE import (
    get_option_data, 
    create_positions, 
    create_itm_mask,
    calculate_otm_share_sale_proceeds
)
import numpy as np

print("COVERED CALL OTM SHARE SALE TEST")
print("="*70)

# Get option data
print("\n1. Setting up covered call scenario...")
bids, strikes, deltas = get_option_data('AAPL', '20250117', use_live_data=False)
print(f"   Got {len(strikes)} strikes")

# Create covered call positions (these are calls you SOLD)
print("\n2. Your covered call positions (calls sold):")
positions = create_positions(strikes, {
    220.0: 5,   # Sold 5 calls at 220 strike
    225.0: 10,  # Sold 10 calls at 225 strike  
    230.0: 2,   # Sold 2 calls at 230 strike
    235.0: 1    # Sold 1 call at 235 strike
})

for strike in [220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    qty = positions.iloc[idx]
    premium = qty * bids.iloc[idx] * 100
    print(f"   Strike ${strike:.2f}: Sold {qty:2d} calls, collected ${premium:,.2f} premium")

total_premium_collected = (positions * bids * 100).sum()
print(f"   Total premium collected: ${total_premium_collected:,.2f}")

# Stock closes at expiration
stock_price = 227.50
print(f"\n3. Stock closes at ${stock_price:.2f} at expiration")

# Determine ITM/OTM
itm = create_itm_mask(strikes, stock_price)
print("\n   What happens to each position:")
for strike in [220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    qty = positions.iloc[idx]
    if itm.iloc[idx] == 1:
        print(f"   Strike ${strike:.2f}: ITM - {qty:2d} × 100 shares called away at ${strike:.2f}")
    else:
        print(f"   Strike ${strike:.2f}: OTM - Keep {qty:2d} × 100 shares, sell at ${stock_price:.2f}")

# Calculate proceeds from selling shares (OTM positions only)
print(f"\n4. Selling shares from OTM positions at ${stock_price:.2f}")

share_proceeds = calculate_otm_share_sale_proceeds(
    positions, strikes, 
    stock_price=stock_price
)

# Show OTM share sales
print("\n   OTM share sale breakdown:")
otm_mask = 1 - itm
total_otm_shares = 0
for strike in [220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    if otm_mask.iloc[idx] == 1 and positions.iloc[idx] > 0:
        proceeds = share_proceeds.iloc[idx]
        qty = positions.iloc[idx]
        shares = qty * 100
        total_otm_shares += shares
        print(f"   Strike ${strike:.2f}: {qty} contracts × 100 shares × ${stock_price:.2f} = ${proceeds:,.2f}")

total_share_proceeds = share_proceeds.sum()
print(f"\n   Total shares sold: {total_otm_shares}")
print(f"   Total proceeds from share sales: ${total_share_proceeds:,.2f}")

# Complete P&L for covered calls
print("\n5. Complete Covered Call P&L")
print("   " + "-"*50)

# Calculate all components
premium_collected = (positions * bids * 100).sum()

# ITM: shares called away at strike
itm_proceeds = (positions * itm * strikes * 100).sum()

# OTM: sell shares at current price
otm_proceeds = share_proceeds.sum()

total_proceeds = itm_proceeds + otm_proceeds

print(f"   Premium collected: ${premium_collected:,.2f}")
print(f"   ITM shares called away: ${itm_proceeds:,.2f}")
print(f"   OTM shares sold at market: ${otm_proceeds:,.2f}")
print(f"   Total received: ${total_proceeds + premium_collected:,.2f}")

# Cost basis comparison (assuming you bought shares at various prices)
print("\n6. Profit Analysis (example cost basis)")
print("   " + "-"*50)

# Assume you bought shares at these prices
cost_basis = {
    220.0: 210.0,  # Bought at $210 for 220 calls
    225.0: 215.0,  # Bought at $215 for 225 calls
    230.0: 220.0,  # Bought at $220 for 230 calls
    235.0: 225.0   # Bought at $225 for 235 calls
}

total_profit = 0
for strike in [220.0, 225.0, 230.0, 235.0]:
    idx = np.abs(strikes - strike).argmin()
    qty = positions.iloc[idx]
    shares = qty * 100
    basis = cost_basis[strike]
    premium = bids.iloc[idx] * qty * 100
    
    if itm.iloc[idx] == 1:
        # ITM: sold at strike
        sale_price = strike
        profit = (sale_price - basis) * shares + premium
        print(f"   Strike ${strike:.2f} (ITM): ({sale_price:.2f} - {basis:.2f}) × {shares} + {premium:.2f} = ${profit:,.2f}")
    else:
        # OTM: sold at market
        sale_price = stock_price
        profit = (sale_price - basis) * shares + premium
        print(f"   Strike ${strike:.2f} (OTM): ({sale_price:.2f} - {basis:.2f}) × {shares} + {premium:.2f} = ${profit:,.2f}")
    
    total_profit += profit

print(f"\n   Total profit: ${total_profit:,.2f}")

# Verify Hadamard multiplication
print("\n7. Hadamard Multiplication Verification")
print("   " + "-"*50)

# Manual calculation: positions ⊙ (1 - itm) × stock_price × 100
otm = 1 - itm
manual_calc = positions * otm * stock_price * 100

print(f"   Formula: positions ⊙ (1 - itm) × stock_price × 100")
print(f"   Manual calculation: ${manual_calc.sum():,.2f}")
print(f"   Function result: ${share_proceeds.sum():,.2f}")
print(f"   Results match: {np.allclose(manual_calc, share_proceeds)}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"""
For covered calls that expire OTM:
- You keep your shares (they don't get called away)
- You sell them immediately at market price (${stock_price:.2f})

The calculate_otm_share_sale_proceeds() function calculates:
  positions ⊙ (1 - itm) × stock_price × 100

This gives you the proceeds from selling shares for OTM covered calls.
""")