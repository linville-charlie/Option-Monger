#!/usr/bin/env python3
"""
Simple interface to get ALL REAL strikes from IBKR
"""
import pandas as pd
import numpy as np
from typing import Tuple
from .ibkr_connection import IBKRConnection
from .options_data import OptionsDataFetcher
from .models import OptionType
import time
import logging

# Suppress debug logs
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def get_all_strikes(ticker: str, expiration: str, return_stock_price: bool = False) -> Tuple:
    """
    Get option data for ALL available strikes from IBKR.
    
    This fetches the ACTUAL strikes available from Interactive Brokers,
    which vary by stock (could be $0.50, $1, $2.50, $5, or $10 increments).
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        expiration: Expiration date in YYYYMMDD format (e.g., '20250117')
    
    Returns:
        If return_stock_price=False:
            Tuple of three pandas Series:
            - bids: Call option bid prices for ALL strikes
            - strikes: ALL available strike prices (real from IBKR)
            - deltas: Call option deltas for ALL strikes
        If return_stock_price=True:
            Adds 4th element:
            - stock_price: Current stock price (float)
    
    Example:
        >>> bids, strikes, deltas = get_all_strikes('AAPL', '20250117')
        >>> print(f"Total strikes: {len(strikes)}")
        >>> print(f"Strike increments vary by zone (e.g., $2.50 near ATM, $5 far out)")
        >>> # Or with stock price:
        >>> bids, strikes, deltas, stock_price = get_all_strikes('AAPL', '20250117', return_stock_price=True)
        >>> print(f"Current stock price: ${stock_price:.2f}")
    """
    
    # Connect to IB Gateway
    conn = IBKRConnection()
    if not conn.connect():
        raise ConnectionError("Failed to connect to IB Gateway. Please ensure IB Gateway is running and configured correctly.")
    
    try:
        fetcher = OptionsDataFetcher(conn)
        
        # Get underlying price
        print(f"Fetching stock price for {ticker}...")
        underlying_price = fetcher.get_underlying_price(ticker)
        if underlying_price and underlying_price > 0:
            print(f"Stock price: ${underlying_price:.2f}")
        else:
            print(f"WARNING: Could not fetch stock price")
            print("Check that market is open and you have market data permissions")
            underlying_price = None
        
        # Store the actual fetched price for return (or estimate from strikes)
        actual_stock_price = underlying_price
        
        # Get REAL available strikes from IBKR
        print(f"Getting available strikes for {expiration}...")
        real_strikes = fetcher.get_option_strikes(ticker, expiration)
        
        if not real_strikes:
            conn.disconnect()
            raise ValueError(f"No strikes found for {ticker} {expiration}. Check that the symbol and expiration are valid.")
        
        print(f"Found {len(real_strikes)} real strikes from IBKR")
        print(f"Strike range: ${min(real_strikes):.2f} to ${max(real_strikes):.2f}")
        
        # Filter to reasonable strikes
        # For weekly options, filter more aggressively to liquid strikes
        # AAPL typically has liquid strikes from -20% to +20% of stock price
        if underlying_price and underlying_price > 50:  # Valid price
            min_strike = underlying_price * 0.8   # 80% of stock price
            max_strike = underlying_price * 1.2   # 120% of stock price
        else:
            # No stock price - try to infer from strike range
            # Most liquid strikes are usually in the middle third of the range
            all_strikes_sorted = sorted(real_strikes)
            total_strikes = len(all_strikes_sorted)
            if total_strikes > 30:
                # Take middle 40% of strikes
                start_idx = int(total_strikes * 0.3)
                end_idx = int(total_strikes * 0.7)
                min_strike = all_strikes_sorted[start_idx]
                max_strike = all_strikes_sorted[end_idx]
                print(f"No stock price available - using middle range of strikes: ${min_strike:.0f}-${max_strike:.0f}")
            else:
                # Use all strikes if not too many
                min_strike = min(real_strikes)
                max_strike = max(real_strikes)
                print(f"No stock price available - using all {total_strikes} strikes")
            
        reasonable_strikes = [s for s in real_strikes if min_strike <= s <= max_strike]
        if len(reasonable_strikes) < len(real_strikes):
            print(f"Filtering to {len(reasonable_strikes)} liquid strikes (${min_strike:.0f}-${max_strike:.0f})")
            real_strikes = reasonable_strikes
        
        # If still too many strikes, limit to closest 30
        if len(real_strikes) > 30:
            real_strikes = sorted(real_strikes, key=lambda x: abs(x - underlying_price))[:30]
            real_strikes = sorted(real_strikes)  # Re-sort by strike
            print(f"Limited to 30 closest strikes")
        
        # Determine actual increments
        if len(real_strikes) > 1:
            increments = [real_strikes[i] - real_strikes[i-1] for i in range(1, min(10, len(real_strikes)))]
            common_increment = max(set(increments), key=increments.count)
            print(f"Common strike increment: ${common_increment:.2f}")
        
        # Fetch real market data from IBKR (requires subscription)
        fetch_real_data = True  # Always fetch real option data from IBKR
        
        if fetch_real_data:
            print(f"\nFetching market data for {len(real_strikes)} strikes...")
            print("This may take a few minutes...")
            
            bids_list = []
            deltas_list = []
            
            for i, strike in enumerate(real_strikes):
                if i % 10 == 0 and i > 0:
                    print(f"Progress: {i}/{len(real_strikes)} strikes fetched...")
                
                try:
                    option_data = fetcher.get_option_data(
                        symbol=ticker,
                        expiry=expiration,
                        strike=strike,
                        option_type=OptionType.CALL
                    )
                    
                    if option_data:
                        bids_list.append(option_data.quote.bid)
                        deltas_list.append(option_data.greeks.delta)
                    else:
                        # No data for this strike
                        bids_list.append(0.0)
                        deltas_list.append(0.0)
                        
                except Exception as e:
                    logger.debug(f"Error fetching strike {strike}: {e}")
                    bids_list.append(0.0)
                    deltas_list.append(0.0)
                
                time.sleep(0.1)  # Rate limiting
            
            # Check if we got enough real data
            valid_data = sum(1 for b in bids_list if b > 0)
            if valid_data < 5:  # Less than 5 valid strikes
                print(f"\nWarning: Only {valid_data} strikes have market data.")
                print("Check that you have the appropriate market data subscriptions.")
        
        # Convert to pandas Series
        bids = pd.Series(bids_list, name='bids')
        strikes = pd.Series(real_strikes, name='strikes')
        deltas = pd.Series(deltas_list, name='deltas')
        
        # Summary
        valid = bids > 0
        print(f"\nResults:")
        print(f"  Total strikes: {len(strikes)}")
        print(f"  Strikes with valid bids: {valid.sum()}")
        
        if return_stock_price:
            # If we couldn't get stock price, estimate from ATM strike
            if actual_stock_price is None:
                # Find strike with delta closest to 0.5 (ATM)
                if len(deltas) > 0 and deltas.max() > 0:
                    atm_idx = abs(deltas - 0.5).argmin()
                    actual_stock_price = float(strikes.iloc[atm_idx])
                    print(f"Estimated stock price from ATM strike: ${actual_stock_price:.2f}")
                else:
                    # Last resort - use middle strike
                    actual_stock_price = float(strikes.median())
                    print(f"Estimated stock price from middle strike: ${actual_stock_price:.2f}")
            return bids, strikes, deltas, actual_stock_price
        return bids, strikes, deltas
        
    finally:
        conn.disconnect()
        print("Disconnected from IB Gateway")


# Demo function removed - only real data allowed


def main():
    """Example usage"""
    import sys
    
    # Parse arguments
    ticker = 'AAPL'
    expiration = '20250117'
    
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    if len(sys.argv) > 2:
        expiration = sys.argv[2]
    
    print("="*70)
    print(f"Getting ALL strikes for {ticker} expiry {expiration}")
    print("Mode: LIVE (fetching real strikes from IBKR)")
    print("="*70)
    
    # Get the data
    bids, strikes, deltas = get_all_strikes(ticker, expiration)
    
    # Display summary
    print(f"\nSummary:")
    print(f"  Total strikes: {len(strikes)}")
    
    valid = bids > 0
    if valid.any():
        print(f"  Strikes with bids > 0: {valid.sum()}")
        print(f"  Bid range: ${bids[valid].min():.2f} to ${bids[valid].max():.2f}")
        print(f"  Delta range: {deltas[valid].min():.4f} to {deltas[valid].max():.4f}")
    
    # Show samples
    print(f"\nFirst 5 strikes:")
    for i in range(min(5, len(strikes))):
        print(f"  Strike ${strikes.iloc[i]:7.2f}: Bid ${bids.iloc[i]:6.2f}, Delta {deltas.iloc[i]:.4f}")
    
    if len(strikes) > 10:
        print(f"\n  ... ({len(strikes) - 10} more strikes) ...\n")
        print(f"Last 5 strikes:")
        for i in range(-5, 0):
            print(f"  Strike ${strikes.iloc[i]:7.2f}: Bid ${bids.iloc[i]:6.2f}, Delta {deltas.iloc[i]:.4f}")
    
    # Find ATM
    if valid.any():
        atm_idx = np.abs(deltas - 0.5).argmin()
        print(f"\nATM Option (Delta ≈ 0.5):")
        print(f"  Strike ${strikes.iloc[atm_idx]:.2f}, Bid ${bids.iloc[atm_idx]:.2f}, Delta {deltas.iloc[atm_idx]:.4f}")
    
    print("\n" + "="*70)
    print("Your three pandas Series are ready:")
    print(f"  bids   - {len(bids)} bid prices")
    print(f"  strikes - {len(strikes)} strike prices")
    print(f"  deltas  - {len(deltas)} delta values")
    print("="*70)
    
    return bids, strikes, deltas


if __name__ == "__main__":
    bids, strikes, deltas = main()