#!/usr/bin/env python3
"""
Example of using option vectors for trading strategies
"""
import pandas as pd
import numpy as np
from get_option_vectors import get_option_vectors, get_option_dataframe


def example_usage():
    """
    Example of how to use the option vectors in a trading strategy
    """
    
    # Get option data for AAPL
    symbol = 'AAPL'
    expiry = '20250815'  # August 15, 2025
    
    print(f"Fetching option data for {symbol} expiry {expiry}...")
    
    # Method 1: Get as separate vectors
    bids, strikes, deltas = get_option_vectors(symbol, expiry)
    
    print("\n" + "="*60)
    print("METHOD 1: SEPARATE VECTORS")
    print("="*60)
    
    print(f"\nNumber of options: {len(strikes)}")
    print(f"\nStrikes: {strikes.values}")
    print(f"\nBids: {bids.values}")
    print(f"\nDeltas: {deltas.values}")
    
    # You can use these vectors directly in calculations
    # Example: Find ATM option (delta closest to 0.5)
    atm_index = np.abs(deltas - 0.5).argmin()
    print(f"\nATM Option:")
    print(f"  Strike: ${strikes.iloc[atm_index]:.2f}")
    print(f"  Bid: ${bids.iloc[atm_index]:.2f}")
    print(f"  Delta: {deltas.iloc[atm_index]:.4f}")
    
    # Example: Find options with delta between 0.3 and 0.7
    mask = (deltas >= 0.3) & (deltas <= 0.7)
    filtered_strikes = strikes[mask]
    filtered_bids = bids[mask]
    filtered_deltas = deltas[mask]
    
    print(f"\nOptions with delta 0.3-0.7:")
    for i in range(len(filtered_strikes)):
        print(f"  Strike ${filtered_strikes.iloc[i]:.2f}: Bid ${filtered_bids.iloc[i]:.2f}, Delta {filtered_deltas.iloc[i]:.4f}")
    
    # Method 2: Get as DataFrame (might be easier for some strategies)
    print("\n" + "="*60)
    print("METHOD 2: DATAFRAME")
    print("="*60)
    
    df = get_option_dataframe(symbol, expiry)
    print(f"\n{df.head(10)}")
    
    # Example calculations with DataFrame
    print(f"\nDataFrame operations:")
    print(f"  Mean bid: ${df['bid'].mean():.2f}")
    print(f"  Max delta: {df['delta'].max():.4f}")
    print(f"  Min delta: {df['delta'].min():.4f}")
    
    # Filter for specific delta range
    filtered_df = df[(df['delta'] >= 0.4) & (df['delta'] <= 0.6)]
    print(f"\nOptions with delta 0.4-0.6:")
    print(filtered_df)
    
    return bids, strikes, deltas


def advanced_example():
    """
    More advanced example with multiple expirations
    """
    symbol = 'AAPL'
    expirations = ['20250815', '20250919']  # Multiple expirations
    
    print("\n" + "="*60)
    print("ADVANCED: MULTIPLE EXPIRATIONS")
    print("="*60)
    
    all_data = {}
    
    for expiry in expirations:
        try:
            bids, strikes, deltas = get_option_vectors(symbol, expiry)
            all_data[expiry] = {
                'bids': bids,
                'strikes': strikes,
                'deltas': deltas
            }
            print(f"\nLoaded {len(strikes)} options for {expiry}")
        except Exception as e:
            print(f"Error loading {expiry}: {e}")
    
    # Compare ATM options across expirations
    print("\nATM Options Comparison:")
    for expiry, data in all_data.items():
        atm_index = np.abs(data['deltas'] - 0.5).argmin()
        print(f"  {expiry}: Strike ${data['strikes'].iloc[atm_index]:.2f}, "
              f"Bid ${data['bids'].iloc[atm_index]:.2f}, "
              f"Delta {data['deltas'].iloc[atm_index]:.4f}")
    
    return all_data


if __name__ == "__main__":
    # Run basic example
    try:
        bids, strikes, deltas = example_usage()
        
        # Uncomment to run advanced example
        # advanced_data = advanced_example()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure IB Gateway is running and connected!")