#!/usr/bin/env python3
"""
Quick test to get real strikes from IBKR
"""
from ibkr_connection import IBKRConnection
from options_data import OptionsDataFetcher
import pandas as pd
import numpy as np

def get_real_strikes_only(ticker: str, expiration: str):
    """Just get the available strikes without fetching all market data"""
    
    conn = IBKRConnection()
    if not conn.connect():
        raise ConnectionError("Failed to connect to IB Gateway")
    
    try:
        fetcher = OptionsDataFetcher(conn)
        
        # Get underlying price
        print(f"Getting data for {ticker}...")
        underlying_price = fetcher.get_underlying_price(ticker)
        if underlying_price:
            print(f"Underlying price: ${underlying_price:.2f}")
        
        # Get available strikes
        print(f"Fetching available strikes for {expiration}...")
        strikes = fetcher.get_option_strikes(ticker, expiration)
        
        if not strikes:
            print("No strikes found")
            return None, None, None
            
        print(f"\nFound {len(strikes)} real strikes from IBKR:")
        print(f"Strike range: ${min(strikes):.2f} to ${max(strikes):.2f}")
        
        # Determine actual increment
        if len(strikes) > 1:
            increment = strikes[1] - strikes[0]
            print(f"Strike increment: ${increment:.2f}")
        
        # Create demo bid and delta data for ALL real strikes
        strikes_series = pd.Series(strikes, name='strikes')
        
        # Generate realistic bids and deltas
        bids_list = []
        deltas_list = []
        
        for strike in strikes:
            moneyness = underlying_price / strike if underlying_price else 100.0 / strike
            
            # Calculate delta
            if moneyness > 1.1:
                delta = 0.90 + np.random.uniform(0, 0.09)
            elif moneyness > 1.0:
                delta = 0.5 + (moneyness - 1) * 3
            elif moneyness > 0.9:
                delta = 0.5 * (moneyness - 0.9) / 0.1
            else:
                delta = max(0.01, 0.5 * moneyness - 0.4)
            
            delta = min(0.99, max(0.01, delta))
            deltas_list.append(delta)
            
            # Calculate bid
            intrinsic = max(0, (underlying_price or 100) - strike)
            if intrinsic > 0:
                time_value = 2.0 * np.exp(-0.1 * abs(moneyness - 1))
            else:
                time_value = max(0.01, 5.0 * np.exp(-10 * (1 - moneyness)**2))
            
            bid = round(intrinsic + time_value, 2)
            bids_list.append(bid)
        
        bids_series = pd.Series(bids_list, name='bids')
        deltas_series = pd.Series(deltas_list, name='deltas')
        
        # Show sample
        print(f"\nFirst 5 strikes:")
        for i in range(min(5, len(strikes))):
            print(f"  Strike ${strikes[i]:6.2f}: Bid ${bids_list[i]:6.2f} (demo), Delta {deltas_list[i]:.4f} (demo)")
        
        if len(strikes) > 10:
            print(f"\n  ... ({len(strikes) - 10} more strikes) ...\n")
            print(f"Last 5 strikes:")
            for i in range(-5, 0):
                print(f"  Strike ${strikes[i]:6.2f}: Bid ${bids_list[i]:6.2f} (demo), Delta {deltas_list[i]:.4f} (demo)")
        
        return bids_series, strikes_series, deltas_series
        
    finally:
        conn.disconnect()
        print("\nDisconnected from IB Gateway")


if __name__ == "__main__":
    import sys
    
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    expiration = sys.argv[2] if len(sys.argv) > 2 else '20250117'
    
    print(f"Testing with {ticker} expiry {expiration}")
    print("="*60)
    
    bids, strikes, deltas = get_real_strikes_only(ticker, expiration)
    
    if strikes is not None:
        print(f"\nSummary:")
        print(f"  Total strikes: {len(strikes)}")
        print(f"  You now have three pandas Series:")
        print(f"  - bids: {len(bids)} bid prices (demo data)")
        print(f"  - strikes: {len(strikes)} strike prices (real from IBKR)")
        print(f"  - deltas: {len(deltas)} delta values (demo data)")
        print(f"\nNote: Using real strikes from IBKR with demo bid/delta data")
        print(f"      Real market data requires subscriptions")