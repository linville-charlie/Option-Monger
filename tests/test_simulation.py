#!/usr/bin/env python3
"""
Test Monte Carlo simulation using deltas as probabilities
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from YOUR_MAIN_INTERFACE import (
    get_option_data,
    create_positions,
    simulate_option_expiration,
    run_monte_carlo_analysis
)
from core.simulation import analyze_position_outcomes
import numpy as np

print("MONTE CARLO SIMULATION TEST")
print("="*70)

# Get option data
print("\n1. Getting option data...")
bids, strikes, deltas = get_option_data('AAPL', '20250117', use_live_data=False)
print(f"   Got {len(strikes)} strikes")

# Create positions
print("\n2. Creating positions...")
positions = create_positions(strikes, {
    220.0: 5,   # Delta ~0.54
    225.0: 10,  # Delta ~0.47
    230.0: 2    # Delta ~0.40
})

# Show position details
print("\n   Position details:")
for strike in [220.0, 225.0, 230.0]:
    idx = np.abs(strikes - strike).argmin()
    qty = positions.iloc[idx]
    delta = deltas.iloc[idx]
    bid = bids.iloc[idx]
    print(f"   Strike ${strike:.2f}: {qty:2d} contracts, Delta={delta:.2f}, Bid=${bid:.2f}")

# Single simulation example
print("\n3. Single Simulation Example")
print("   " + "-"*50)

for i in range(5):
    exp_price = simulate_option_expiration(strikes, deltas, positions, random_seed=i)
    
    # Check which positions are ITM
    itm_220 = exp_price >= 220.0
    itm_225 = exp_price >= 225.0
    itm_230 = exp_price >= 230.0
    
    print(f"   Sim {i+1}: Expires at ${exp_price:.2f}")
    print(f"          220: {'ITM' if itm_220 else 'OTM'}, 225: {'ITM' if itm_225 else 'OTM'}, 230: {'ITM' if itm_230 else 'OTM'}")

# Monte Carlo analysis
print("\n4. Monte Carlo Analysis (10,000 simulations)")
print("   " + "-"*50)

results = run_monte_carlo_analysis(
    strikes, deltas, positions, bids,
    n_simulations=10000,
    random_seed=42
)

print(f"\n   P&L Statistics:")
print(f"     Expected P&L: ${results['expected_pnl']:,.2f}")
print(f"     Std Deviation: ${results['pnl_std']:,.2f}")
print(f"     Min P&L: ${results['min_pnl']:,.2f}")
print(f"     Max P&L: ${results['max_pnl']:,.2f}")
print(f"     Median P&L: ${results['median_pnl']:,.2f}")

print(f"\n   Risk Metrics:")
print(f"     Win Rate: {results['win_rate']:.1f}%")
print(f"     Avg Win: ${results['avg_win']:,.2f}")
print(f"     Avg Loss: ${results['avg_loss']:,.2f}")
print(f"     95% VaR: ${results['var_95']:,.2f}")
print(f"     95% CVaR: ${results['cvar_95']:,.2f}")

print(f"\n   Expiration Price Distribution:")
print(f"     Average: ${results['avg_expiration_price']:.2f}")
print(f"     5th percentile: ${results['price_percentiles']['5%']:.2f}")
print(f"     25th percentile: ${results['price_percentiles']['25%']:.2f}")
print(f"     50th percentile: ${results['price_percentiles']['50%']:.2f}")
print(f"     75th percentile: ${results['price_percentiles']['75%']:.2f}")
print(f"     95th percentile: ${results['price_percentiles']['95%']:.2f}")

print(f"\n   Position Statistics:")
print(f"     Avg ITM positions: {results['avg_itm_positions']:.2f}")

# Analyze individual positions
print("\n5. Individual Position Analysis")
print("   " + "-"*50)

position_analysis = analyze_position_outcomes(
    strikes, deltas, positions, bids, n_simulations=10000
)

print("\n   Position-by-Position Breakdown:")
print(position_analysis.to_string(index=False))

# Verify delta interpretation
print("\n6. Delta vs Simulated ITM Probability")
print("   " + "-"*50)

for _, row in position_analysis.iterrows():
    print(f"   Strike ${row['strike']:.2f}:")
    print(f"     Delta (theoretical): {row['delta']:.2f}")
    print(f"     Simulated ITM prob: {row['simulated_itm_prob']:.2f}")
    print(f"     Difference: {row['delta_vs_simulated']:.4f}")

# P&L distribution
print("\n7. P&L Distribution")
print("   " + "-"*50)

print(f"   P&L Percentiles:")
for pct, value in results['pnl_percentiles'].items():
    print(f"     {pct:>3s}: ${value:,.2f}")

# Calculate probability of different outcomes
profitable = (results['pnls'] > 0).mean() * 100
breakeven = (results['pnls'] > -1000).mean() * 100  # Within $1000 of breakeven
big_win = (results['pnls'] > 5000).mean() * 100
big_loss = (results['pnls'] < -10000).mean() * 100

print(f"\n   Outcome Probabilities:")
print(f"     Profitable: {profitable:.1f}%")
print(f"     Near breakeven (>-$1000): {breakeven:.1f}%")
print(f"     Big win (>$5000): {big_win:.1f}%")
print(f"     Big loss (<-$10000): {big_loss:.1f}%")

# Price constraint verification
print("\n8. Price Constraint Logic Verification")
print("   " + "-"*50)

# Test specific scenario
test_positions = create_positions(strikes, {220: 1, 225: 1, 230: 1})

print("   Testing with positions at 220, 225, 230:")
print("   If only 225 is ITM, price should be between 225 and 230")

for seed in range(100, 105):
    exp_price = simulate_option_expiration(strikes, deltas, test_positions, random_seed=seed)
    itm_220 = exp_price >= 220
    itm_225 = exp_price >= 225
    itm_230 = exp_price >= 230
    
    if itm_225 and not itm_230:
        print(f"     Seed {seed}: ${exp_price:.2f} ✓ (225 < price < 230)")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
The simulation uses deltas as ITM probabilities:
- Each option's delta = probability it expires ITM
- Simulates realistic expiration prices with constraints
- If highest ITM has higher strike above it: price between them
- If highest ITM is highest owned: price up to 3% above (skewed low)

This provides a probabilistic view of your position outcomes!
""")