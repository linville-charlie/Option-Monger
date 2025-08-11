#!/usr/bin/env python3
"""
Example of how to use the three vectors in your trading strategy
"""
from simple_real_strikes import get_all_strikes
import pandas as pd
import numpy as np

# THIS IS THE SIMPLE INTERFACE YOU REQUESTED
# Input: ticker and expiration
# Output: three pandas vectors (bids, strikes, deltas)

def run_your_strategy():
    """Example of using the vectors in your strategy"""
    
    # 1. GET YOUR THREE VECTORS - IT'S THIS SIMPLE!
    ticker = 'AAPL'
    expiration = '20250117'
    
    print(f"Getting option data for {ticker} expiry {expiration}...")
    bids, strikes, deltas = get_all_strikes(ticker, expiration, use_live_data=True)
    
    print(f"\n✓ Got {len(strikes)} strikes from IBKR!")
    print(f"  - bids: {len(bids)} bid prices")
    print(f"  - strikes: {len(strikes)} strike prices")
    print(f"  - deltas: {len(deltas)} delta values")
    
    # 2. USE THE VECTORS IN YOUR STRATEGY
    
    # Example 1: Find ATM option
    atm_idx = np.abs(deltas - 0.5).argmin()
    print(f"\nATM Option:")
    print(f"  Strike: ${strikes.iloc[atm_idx]:.2f}")
    print(f"  Bid: ${bids.iloc[atm_idx]:.2f}")
    print(f"  Delta: {deltas.iloc[atm_idx]:.4f}")
    
    # Example 2: Find 30-delta option
    target_delta = 0.30
    delta_30_idx = np.abs(deltas - target_delta).argmin()
    print(f"\n30-Delta Option:")
    print(f"  Strike: ${strikes.iloc[delta_30_idx]:.2f}")
    print(f"  Bid: ${bids.iloc[delta_30_idx]:.2f}")
    print(f"  Delta: {deltas.iloc[delta_30_idx]:.4f}")
    
    # Example 3: Filter for liquid options (bid > 0)
    liquid_mask = bids > 0
    liquid_strikes = strikes[liquid_mask]
    liquid_bids = bids[liquid_mask]
    liquid_deltas = deltas[liquid_mask]
    
    print(f"\nLiquid Options:")
    print(f"  Count: {len(liquid_strikes)} out of {len(strikes)}")
    print(f"  Strike range: ${liquid_strikes.min():.2f} - ${liquid_strikes.max():.2f}")
    
    # Example 4: Find options in a specific delta range
    delta_min, delta_max = 0.25, 0.75
    delta_range_mask = (deltas >= delta_min) & (deltas <= delta_max)
    range_strikes = strikes[delta_range_mask]
    range_bids = bids[delta_range_mask]
    range_deltas = deltas[delta_range_mask]
    
    print(f"\nOptions with Delta between {delta_min} and {delta_max}:")
    print(f"  Count: {len(range_strikes)}")
    if len(range_strikes) > 0:
        print(f"  Strike range: ${range_strikes.min():.2f} - ${range_strikes.max():.2f}")
    
    # Example 5: Calculate a vertical spread
    buy_delta_target = 0.40
    sell_delta_target = 0.30
    
    buy_idx = np.abs(deltas - buy_delta_target).argmin()
    sell_idx = np.abs(deltas - sell_delta_target).argmin()
    
    spread_cost = bids.iloc[buy_idx] - bids.iloc[sell_idx]
    max_profit = strikes.iloc[sell_idx] - strikes.iloc[buy_idx] - spread_cost
    
    print(f"\nVertical Spread (40-delta long, 30-delta short):")
    print(f"  Buy: ${strikes.iloc[buy_idx]:.2f} @ ${bids.iloc[buy_idx]:.2f}")
    print(f"  Sell: ${strikes.iloc[sell_idx]:.2f} @ ${bids.iloc[sell_idx]:.2f}")
    print(f"  Net Debit: ${spread_cost:.2f}")
    print(f"  Max Profit: ${max_profit:.2f}")
    
    return bids, strikes, deltas


def get_multiple_expirations():
    """Example of getting multiple expiration dates"""
    
    ticker = 'AAPL'
    expirations = ['20250117', '20250221', '20250321']  # Jan, Feb, Mar
    
    all_data = {}
    
    for exp in expirations:
        print(f"\nFetching {ticker} {exp}...")
        bids, strikes, deltas = get_all_strikes(ticker, exp, use_live_data=True)
        all_data[exp] = {
            'bids': bids,
            'strikes': strikes,
            'deltas': deltas
        }
        print(f"  Got {len(strikes)} strikes")
    
    return all_data


def quick_demo():
    """Quick demo without connecting to IB Gateway"""
    
    print("DEMO MODE (with $0.50 increments as requested)")
    print("="*50)
    
    # Use demo mode to avoid IB Gateway connection
    ticker = 'AAPL'
    expiration = '20250117'
    
    bids, strikes, deltas = get_all_strikes(ticker, expiration, use_live_data=False)
    
    print(f"\nGot {len(strikes)} strikes with $0.50 increments")
    print(f"Strike range: ${strikes.min():.2f} to ${strikes.max():.2f}")
    
    # Show you can use them as vectors
    print("\nUsing as numpy arrays:")
    strikes_array = strikes.values
    bids_array = bids.values
    deltas_array = deltas.values
    
    print(f"  strikes_array.shape = {strikes_array.shape}")
    print(f"  bids_array.shape = {bids_array.shape}")
    print(f"  deltas_array.shape = {deltas_array.shape}")
    
    return bids, strikes, deltas


if __name__ == "__main__":
    import sys
    
    if '--demo' in sys.argv:
        # Run without IB Gateway
        bids, strikes, deltas = quick_demo()
    else:
        # Run with real IBKR data
        bids, strikes, deltas = run_your_strategy()
    
    print("\n" + "="*50)
    print("YOUR THREE VECTORS ARE READY!")
    print("="*50)
    print("\nUse them in your code like this:")
    print("  from simple_real_strikes import get_all_strikes")
    print("  bids, strikes, deltas = get_all_strikes('AAPL', '20250117')")
    print("\nThat's it! You have your three pandas vectors.")