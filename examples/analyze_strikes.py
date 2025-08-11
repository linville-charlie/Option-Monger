#!/usr/bin/env python3
"""
Analyze strike increments from IBKR for different stocks
"""
from ibkr_connection import IBKRConnection
from options_data import OptionsDataFetcher
import numpy as np

def analyze_strike_increments(ticker: str, expiration: str):
    """Analyze the strike increments for a given stock"""
    
    conn = IBKRConnection()
    if not conn.connect():
        raise ConnectionError("Failed to connect to IB Gateway")
    
    try:
        fetcher = OptionsDataFetcher(conn)
        
        # Get underlying price
        print(f"\nAnalyzing {ticker}...")
        underlying_price = fetcher.get_underlying_price(ticker)
        if underlying_price:
            print(f"Underlying price: ${underlying_price:.2f}")
        
        # Get available strikes
        strikes = fetcher.get_option_strikes(ticker, expiration)
        
        if not strikes:
            print(f"No strikes found for {ticker} {expiration}")
            return None
            
        print(f"Found {len(strikes)} strikes")
        print(f"Strike range: ${min(strikes):.2f} to ${max(strikes):.2f}")
        
        # Analyze increments
        if len(strikes) > 1:
            increments = []
            for i in range(1, len(strikes)):
                increment = strikes[i] - strikes[i-1]
                increments.append(increment)
            
            # Find unique increments
            unique_increments = sorted(list(set(increments)))
            
            print(f"\nStrike increment analysis:")
            print(f"  Unique increments found: {[f'${x:.2f}' for x in unique_increments]}")
            
            # Count frequency of each increment
            from collections import Counter
            increment_counts = Counter([round(x, 2) for x in increments])
            
            print(f"\n  Increment frequency:")
            for inc, count in sorted(increment_counts.items()):
                print(f"    ${inc:.2f}: {count} times ({count/len(increments)*100:.1f}%)")
            
            # Determine zones
            if len(unique_increments) > 1:
                print(f"\n  Strike zones:")
                current_inc = increments[0]
                zone_start = strikes[0]
                
                for i in range(1, len(increments)):
                    if abs(increments[i] - current_inc) > 0.01:  # New increment zone
                        print(f"    ${zone_start:.2f} - ${strikes[i]:.2f}: ${current_inc:.2f} increments")
                        current_inc = increments[i]
                        zone_start = strikes[i]
                
                # Print last zone
                print(f"    ${zone_start:.2f} - ${strikes[-1]:.2f}: ${current_inc:.2f} increments")
        
        return strikes
        
    finally:
        conn.disconnect()


def test_multiple_stocks():
    """Test multiple stocks to see their strike patterns"""
    
    test_cases = [
        ('AAPL', '20250117'),   # High price stock
        ('F', '20250117'),      # Low price stock
        ('SPY', '20250117'),    # ETF
        ('TSLA', '20250117'),   # Mid-high price stock
        ('BAC', '20250117'),    # Low-mid price stock
    ]
    
    print("="*70)
    print("STRIKE INCREMENT ANALYSIS FOR DIFFERENT STOCKS")
    print("="*70)
    
    for ticker, expiration in test_cases:
        try:
            analyze_strike_increments(ticker, expiration)
            print("\n" + "-"*70)
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            print("\n" + "-"*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
        expiration = sys.argv[2] if len(sys.argv) > 2 else '20250117'
        analyze_strike_increments(ticker, expiration)
    else:
        # Run analysis on multiple stocks
        test_multiple_stocks()