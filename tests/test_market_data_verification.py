#!/usr/bin/env python3
"""
Comprehensive test to verify live market data is working correctly
Tests stock price, option chain, and specific strike data
"""
import time
from datetime import datetime
from core.ibkr_connection import IBKRConnection
from core.options_data import OptionsDataFetcher
from core.models import OptionType

def test_market_hours():
    """Check if market is open"""
    from datetime import datetime
    import pytz
    
    # Get current time in ET
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    
    # Market hours: 9:30 AM - 4:00 PM ET, weekdays only
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
    
    is_weekday = now_et.weekday() < 5  # Monday=0, Friday=4
    is_market_hours = market_open <= now_et <= market_close
    
    print(f"Current time (ET): {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Market hours: 9:30 AM - 4:00 PM ET")
    print(f"Is weekday: {is_weekday}")
    print(f"Is market hours: {is_market_hours}")
    
    return is_weekday and is_market_hours

def test_stock_data(ticker="AAPL"):
    """Test fetching stock market data"""
    print("\n" + "="*60)
    print(f"TESTING STOCK DATA FOR {ticker}")
    print("="*60)
    
    conn = IBKRConnection()
    if not conn.connect():
        print("❌ Failed to connect to IB Gateway")
        return False
    
    try:
        fetcher = OptionsDataFetcher(conn)
        
        # Get stock data
        print(f"\nFetching stock data for {ticker}...")
        stock_data = fetcher.get_stock_data(ticker)
        
        if stock_data:
            print("✅ Stock data received:")
            print(f"  Symbol: {stock_data['symbol']}")
            print(f"  Last: ${stock_data.get('last', 'N/A')}")
            print(f"  Bid: ${stock_data.get('bid', 'N/A')}")
            print(f"  Ask: ${stock_data.get('ask', 'N/A')}")
            print(f"  Volume: {stock_data.get('volume', 'N/A'):,}")
            
            # Get underlying price
            price = fetcher.get_underlying_price(ticker)
            if price:
                print(f"  Underlying Price: ${price:.2f}")
                return True
            else:
                print("❌ Could not get underlying price")
                return False
        else:
            print("❌ No stock data received")
            return False
            
    finally:
        conn.disconnect()

def test_option_chain(ticker="AAPL", expiration="20250815"):
    """Test fetching option chain data"""
    print("\n" + "="*60)
    print(f"TESTING OPTION CHAIN FOR {ticker}")
    print("="*60)
    
    conn = IBKRConnection()
    if not conn.connect():
        print("❌ Failed to connect to IB Gateway")
        return False
    
    try:
        fetcher = OptionsDataFetcher(conn)
        
        # Get available expirations
        print(f"\nFetching available expirations for {ticker}...")
        expirations = fetcher.get_option_chain_dates(ticker)
        
        if expirations:
            print(f"✅ Found {len(expirations)} expiration dates")
            print(f"  First 5: {expirations[:5]}")
            
            if expiration not in expirations:
                print(f"  ⚠️ {expiration} not in list, using first available")
                expiration = expirations[0]
        else:
            print("❌ No expirations found")
            return False
        
        # Get strikes for expiration
        print(f"\nFetching strikes for {expiration}...")
        strikes = fetcher.get_option_strikes(ticker, expiration)
        
        if strikes:
            print(f"✅ Found {len(strikes)} strikes")
            print(f"  Range: ${min(strikes):.2f} - ${max(strikes):.2f}")
            
            # Determine strike increments
            if len(strikes) > 1:
                increments = [strikes[i] - strikes[i-1] for i in range(1, min(10, len(strikes)))]
                common_increment = max(set(increments), key=increments.count)
                print(f"  Common increment: ${common_increment:.2f}")
            
            return True
        else:
            print("❌ No strikes found")
            return False
            
    finally:
        conn.disconnect()

def test_specific_option(ticker="AAPL", expiration="20250815", strike=230.0):
    """Test fetching specific option data"""
    print("\n" + "="*60)
    print(f"TESTING SPECIFIC OPTION: {ticker} {strike}C {expiration}")
    print("="*60)
    
    conn = IBKRConnection()
    if not conn.connect():
        print("❌ Failed to connect to IB Gateway")
        return False
    
    try:
        fetcher = OptionsDataFetcher(conn)
        
        # Get underlying price first
        print(f"\nGetting underlying price...")
        underlying_price = fetcher.get_underlying_price(ticker)
        if underlying_price:
            print(f"  Stock price: ${underlying_price:.2f}")
            
            # Adjust strike to be near ATM
            strikes = fetcher.get_option_strikes(ticker, expiration)
            if strikes:
                # Find closest strike to current price
                closest_strike = min(strikes, key=lambda x: abs(x - underlying_price))
                if abs(closest_strike - strike) > 10:
                    print(f"  Adjusting strike from {strike} to {closest_strike} (closer to ATM)")
                    strike = closest_strike
        
        # Get option data
        print(f"\nFetching option data for {ticker} {strike}C {expiration}...")
        option_data = fetcher.get_option_data(
            symbol=ticker,
            expiry=expiration,
            strike=strike,
            option_type=OptionType.CALL
        )
        
        if option_data:
            print("✅ Option data received:")
            print(f"\nQuote:")
            print(f"  Bid: ${option_data.quote.bid:.2f}")
            print(f"  Ask: ${option_data.quote.ask:.2f}")
            print(f"  Last: ${option_data.quote.last:.2f}")
            print(f"  Volume: {option_data.quote.volume}")
            
            print(f"\nGreeks:")
            print(f"  Delta: {option_data.greeks.delta:.4f}")
            print(f"  Gamma: {option_data.greeks.gamma:.4f}")
            print(f"  Theta: {option_data.greeks.theta:.4f}")
            print(f"  Vega: {option_data.greeks.vega:.4f}")
            print(f"  IV: {option_data.greeks.implied_volatility:.2%}")
            
            return True
        else:
            print("❌ No option data received")
            return False
            
    finally:
        conn.disconnect()

def main():
    """Run all tests"""
    print("="*60)
    print("MARKET DATA VERIFICATION TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check market hours
    is_market_open = test_market_hours()
    if not is_market_open:
        print("\n⚠️ Market is closed. Data may be delayed or unavailable.")
        print("Run this test during market hours (9:30 AM - 4:00 PM ET) for best results.")
    
    # Track results
    results = {}
    
    # Test 1: Stock data
    results['stock'] = test_stock_data("AAPL")
    
    # Test 2: Option chain
    results['chain'] = test_option_chain("AAPL", "20250815")
    
    # Test 3: Specific option
    results['option'] = test_specific_option("AAPL", "20250815", 230.0)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.capitalize()} Test: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Your market data subscription is working correctly.")
        print("\nYou can now run live covered call optimization with:")
        print("  python test_live_options.py")
    else:
        print("\n⚠️ Some tests failed. Check:")
        print("1. IB Gateway is running on port 8000")
        print("2. You have an active OPRA subscription")
        print("3. Market is open (if testing real-time data)")
        print("4. Your account has permissions for options trading")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)