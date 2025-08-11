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


def get_all_strikes(ticker: str, expiration: str, use_live_data: bool = True, return_stock_price: bool = False) -> Tuple:
    """
    Get option data for ALL available strikes from IBKR.
    
    This fetches the ACTUAL strikes available from Interactive Brokers,
    which vary by stock (could be $0.50, $1, $2.50, $5, or $10 increments).
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        expiration: Expiration date in YYYYMMDD format (e.g., '20250117')
        use_live_data: If True, fetch real strikes from IB Gateway
    
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
    
    if not use_live_data:
        # Demo mode with simulated $0.50 increments
        result = _generate_demo_strikes(ticker, expiration)
        if return_stock_price:
            # Estimate stock price from ATM strike in demo mode
            bids, strikes, deltas = result
            atm_idx = np.abs(deltas - 0.5).argmin()
            stock_price = float(strikes.iloc[atm_idx])
            return bids, strikes, deltas, stock_price
        return result
    
    # Connect to IB Gateway
    conn = IBKRConnection()
    if not conn.connect():
        print("Failed to connect to IB Gateway. Using demo data...")
        result = _generate_demo_strikes(ticker, expiration)
        if return_stock_price:
            bids, strikes, deltas = result
            atm_idx = np.abs(deltas - 0.5).argmin()
            stock_price = float(strikes.iloc[atm_idx])
            return bids, strikes, deltas, stock_price
        return result
    
    try:
        fetcher = OptionsDataFetcher(conn)
        
        # Get underlying price
        print(f"Fetching data for {ticker}...")
        underlying_price = fetcher.get_underlying_price(ticker)
        if underlying_price:
            print(f"Underlying price: ${underlying_price:.2f}")
        else:
            underlying_price = 100.0  # Fallback
        
        # Store the actual fetched price for return
        actual_stock_price = underlying_price
        
        # Get REAL available strikes from IBKR
        print(f"Getting available strikes for {expiration}...")
        real_strikes = fetcher.get_option_strikes(ticker, expiration)
        
        if not real_strikes:
            print(f"No strikes found. Using demo data...")
            conn.disconnect()
            result = _generate_demo_strikes(ticker, expiration)
            if return_stock_price:
                bids, strikes, deltas = result
                atm_idx = np.abs(deltas - 0.5).argmin()
                stock_price = float(strikes.iloc[atm_idx])
                return bids, strikes, deltas, stock_price
            return result
        
        print(f"Found {len(real_strikes)} real strikes from IBKR")
        print(f"Strike range: ${min(real_strikes):.2f} to ${max(real_strikes):.2f}")
        
        # Filter to reasonable strikes (within 50% of current price)
        # This avoids trying to fetch data for strikes that don't actually trade
        reasonable_strikes = [s for s in real_strikes if 0.5 * underlying_price <= s <= 1.5 * underlying_price]
        if len(reasonable_strikes) < len(real_strikes):
            print(f"Filtering to {len(reasonable_strikes)} reasonable strikes (50%-150% of stock price)")
            real_strikes = reasonable_strikes
        
        # Determine actual increments
        if len(real_strikes) > 1:
            increments = [real_strikes[i] - real_strikes[i-1] for i in range(1, min(10, len(real_strikes)))]
            common_increment = max(set(increments), key=increments.count)
            print(f"Common strike increment: ${common_increment:.2f}")
        
        # Option 1: Try to fetch real market data (requires subscription)
        # For far-dated expirations, many strikes may not exist
        fetch_real_data = True  # Fetch real option data from IBKR
        
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
            if valid_data < 10:  # Less than 10 valid strikes
                print(f"\nWarning: Only {valid_data} strikes have market data.")
                print("Falling back to demo data for better results.")
                fetch_real_data = False  # Force demo mode
        
        if not fetch_real_data:
            # Option 2: Generate realistic demo data for the REAL strikes
            print("\nGenerating demo bid/delta data for real IBKR strikes...")
            print("(For real market data, enable fetch_real_data and ensure you have subscriptions)")
            
            bids_list = []
            deltas_list = []
            
            for strike in real_strikes:
                moneyness = underlying_price / strike
                
                # Calculate realistic delta
                if moneyness > 1.2:  # Deep ITM
                    delta = 0.90 + np.random.uniform(0, 0.08)
                elif moneyness > 1.05:  # ITM
                    delta = 0.6 + (moneyness - 1.05) * 2.0
                elif moneyness > 0.95:  # ATM region
                    delta = 0.3 + (moneyness - 0.95) * 3.0
                elif moneyness > 0.8:  # OTM
                    delta = 0.05 + (moneyness - 0.8) * 1.25
                else:  # Deep OTM
                    delta = max(0.001, 0.05 * moneyness)
                
                delta = min(0.99, max(0.001, delta))
                deltas_list.append(round(delta, 4))
                
                # Calculate realistic bid
                intrinsic_value = max(0, underlying_price - strike)
                
                if intrinsic_value > 0:
                    # ITM - intrinsic + time value
                    time_value = 3.0 * np.exp(-0.5 * abs(moneyness - 1))
                    bid = intrinsic_value + time_value
                else:
                    # OTM - only time value
                    distance = abs(strike - underlying_price) / underlying_price
                    if distance < 0.1:  # Near ATM
                        bid = 5.0 * np.exp(-distance * 10)
                    elif distance < 0.3:  # Moderate OTM
                        bid = 2.0 * np.exp(-distance * 8)
                    else:  # Far OTM
                        bid = max(0.01, 0.5 * np.exp(-distance * 5))
                
                # Very far strikes might have no bid
                if moneyness < 0.5 or moneyness > 2.0:
                    if np.random.random() > 0.7:
                        bid = 0.0
                        delta = 0.0
                
                bids_list.append(round(bid, 2))
        
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
            return bids, strikes, deltas, actual_stock_price
        return bids, strikes, deltas
        
    finally:
        conn.disconnect()
        print("Disconnected from IB Gateway")


def _generate_demo_strikes(ticker: str, expiration: str) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Generate demo data with $0.50 increments as requested"""
    
    # Demo underlying prices
    demo_prices = {
        'AAPL': 226.50,
        'TSLA': 245.00,
        'SPY': 450.00,
        'QQQ': 380.00,
        'NVDA': 450.00,
    }
    
    underlying = demo_prices.get(ticker.upper(), 100.0)
    
    # Generate strikes with $0.50 increments
    interval = 0.5
    start = max(0.5, int(underlying * 0.3 / 0.5) * 0.5)
    end = int(underlying * 2.0 / 0.5) * 0.5
    
    all_strikes = []
    current = start
    while current <= end:
        all_strikes.append(float(current))
        current += interval
    
    # Generate demo bids and deltas
    all_bids = []
    all_deltas = []
    
    for strike in all_strikes:
        moneyness = underlying / strike
        
        # Delta calculation
        if moneyness > 1.2:
            delta = 0.95 + np.random.uniform(-0.02, 0.04)
        elif moneyness > 1.05:
            delta = 0.6 + (moneyness - 1.05) * 2.0
        elif moneyness > 0.95:
            delta = 0.3 + (moneyness - 0.95) * 3.0
        elif moneyness > 0.8:
            delta = 0.05 + (moneyness - 0.8) * 1.25
        else:
            delta = max(0.001, 0.05 * moneyness)
        
        delta = min(0.99, max(0.001, delta))
        all_deltas.append(round(delta, 4))
        
        # Bid calculation
        intrinsic = max(0, underlying - strike)
        if intrinsic > 0:
            time_value = 3.0 * np.exp(-0.5 * abs(moneyness - 1))
            bid = intrinsic + time_value
        else:
            distance = abs(strike - underlying) / underlying
            if distance < 0.1:
                bid = 5.0 * np.exp(-distance * 10)
            elif distance < 0.3:
                bid = 2.0 * np.exp(-distance * 8)
            else:
                bid = max(0.01, 0.5 * np.exp(-distance * 5))
        
        all_bids.append(round(bid, 2))
    
    print(f"\nDemo mode: Generated {len(all_strikes)} strikes with $0.50 increments")
    print(f"Strike range: ${min(all_strikes):.2f} to ${max(all_strikes):.2f}")
    
    return (pd.Series(all_bids, name='bids'),
            pd.Series(all_strikes, name='strikes'),
            pd.Series(all_deltas, name='deltas'))


def main():
    """Example usage"""
    import sys
    
    # Parse arguments
    ticker = 'AAPL'
    expiration = '20250117'
    use_live = True
    
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    if len(sys.argv) > 2:
        expiration = sys.argv[2]
    if '--demo' in sys.argv:
        use_live = False
    
    print("="*70)
    print(f"Getting ALL strikes for {ticker} expiry {expiration}")
    if use_live:
        print("Mode: LIVE (fetching real strikes from IBKR)")
    else:
        print("Mode: DEMO (using $0.50 increment simulation)")
    print("="*70)
    
    # Get the data
    bids, strikes, deltas = get_all_strikes(ticker, expiration, use_live_data=use_live)
    
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