#!/usr/bin/env python3
"""
Quick test to verify live data is working
Run this during market hours for best results
"""
from datetime import datetime
from core.simple_real_strikes import get_all_strikes

print("="*60)
print("QUICK LIVE DATA TEST")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# Test with AAPL
ticker = "AAPL"
expiration = "20250815"  # August 15, 2025

print(f"\nFetching live data for {ticker} {expiration}...")
print("This should take about 30-60 seconds...\n")

try:
    # Get live data with stock price
    bids, strikes, deltas, stock_price = get_all_strikes(
        ticker, 
        expiration, 
        use_live_data=True,
        return_stock_price=True
    )
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    print(f"\nCurrent Stock Price: ${stock_price:.2f}")
    print(f"Total Strikes: {len(strikes)}")
    print(f"Strikes with Bids: {sum(bids > 0)}")
    print(f"Strikes with Deltas: {sum(deltas > 0)}")
    
    # Find ATM options
    if len(strikes) > 0 and stock_price > 0:
        closest_idx = abs(strikes - stock_price).argmin()
        atm_strike = strikes.iloc[closest_idx]
        atm_bid = bids.iloc[closest_idx]
        atm_delta = deltas.iloc[closest_idx]
        
        print(f"\nATM Option:")
        print(f"  Strike: ${atm_strike:.2f}")
        print(f"  Bid: ${atm_bid:.2f}")
        print(f"  Delta: {atm_delta:.4f}")
    
    # Show sample of data
    print("\nSample of strikes near ATM:")
    start_idx = max(0, closest_idx - 2)
    end_idx = min(len(strikes), closest_idx + 3)
    
    for i in range(start_idx, end_idx):
        s = strikes.iloc[i]
        b = bids.iloc[i]
        d = deltas.iloc[i]
        moneyness = "ATM" if i == closest_idx else ("ITM" if s < stock_price else "OTM")
        print(f"  ${s:7.2f} ({moneyness:3s}): Bid=${b:6.2f}, Delta={d:.4f}")
    
    print("\n✅ Live data successfully fetched!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure IB Gateway is running on port 8000")
    print("2. Check you're running during market hours (9:30 AM - 4:00 PM ET)")
    print("3. Verify your OPRA subscription is active")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)