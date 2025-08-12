#!/usr/bin/env python3
"""
Test IBKR options data fetching according to official documentation
https://interactivebrokers.github.io/tws-api/options.html
https://interactivebrokers.github.io/tws-api/option_computations.html
"""
import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class TestOptionsApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.nextOrderId = None
        self.option_chains = {}
        self.market_data = {}
        
    def error(self, reqId, errorCode, errorString):
        print(f"Error {errorCode}: {errorString}")
        
    def nextValidId(self, orderId):
        self.nextOrderId = orderId
        self.connected = True
        print(f"Connected! Next Valid Order ID: {orderId}")
        
    def contractDetails(self, reqId, contractDetails):
        print(f"Contract: {contractDetails.contract.symbol} {contractDetails.contract.strike} {contractDetails.contract.right}")
        
    def contractDetailsEnd(self, reqId):
        print(f"Contract details complete for request {reqId}")
        
    def securityDefinitionOptionParameter(self, reqId, exchange, underlyingConId, tradingClass, multiplier, expirations, strikes):
        """Recommended method for getting option chains"""
        print(f"Option chain for {tradingClass} on {exchange}:")
        print(f"  Expirations: {list(expirations)[:5]}...")  # Show first 5
        print(f"  Strikes: {sorted(list(strikes))[:10]}...")  # Show first 10
        if reqId not in self.option_chains:
            self.option_chains[reqId] = []
        self.option_chains[reqId].append({
            'exchange': exchange,
            'strikes': list(strikes),
            'expirations': list(expirations)
        })
        
    def securityDefinitionOptionParameterEnd(self, reqId):
        print(f"Option chain complete for request {reqId}")
        
    def tickPrice(self, reqId, tickType, price, attrib):
        """Receive price ticks"""
        tick_names = {1: 'bid', 2: 'ask', 4: 'last', 66: 'delayed_bid', 67: 'delayed_ask', 68: 'delayed_last'}
        if tickType in tick_names:
            if reqId not in self.market_data:
                self.market_data[reqId] = {}
            self.market_data[reqId][tick_names[tickType]] = price
            print(f"  {tick_names[tickType]}: ${price:.2f}")
            
    def tickOptionComputation(self, reqId, tickType, tickAttrib, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice):
        """Receive option Greeks - THE KEY METHOD FOR OPTIONS"""
        tick_names = {
            10: 'Bid', 11: 'Ask', 12: 'Last', 13: 'Model',
            53: 'Delayed Bid', 54: 'Delayed Ask', 55: 'Delayed Last', 56: 'Delayed Model'
        }
        if tickType in tick_names:
            print(f"  {tick_names[tickType]} Greeks:")
            if delta != -2 and delta != -1:
                print(f"    Delta: {delta:.4f}")
            if gamma != -2 and gamma != -1:
                print(f"    Gamma: {gamma:.4f}")
            if theta != -2 and theta != -1:
                print(f"    Theta: {theta:.4f}")
            if vega != -2 and vega != -1:
                print(f"    Vega: {vega:.4f}")
            if impliedVol > 0:
                print(f"    IV: {impliedVol:.2%}")
                
    def marketDataType(self, reqId, marketDataType):
        """Market data type callback"""
        types = {1: "Real-time", 2: "Frozen", 3: "Delayed", 4: "Delayed-frozen"}
        print(f"Market data type: {types.get(marketDataType, marketDataType)}")


def test_option_data():
    """Test option data fetching according to IBKR documentation"""
    app = TestOptionsApp()
    
    # Connect to IB Gateway
    print("Connecting to IB Gateway...")
    app.connect("127.0.0.1", 8000, clientId=0)
    
    # Start the message processing in a thread
    import threading
    api_thread = threading.Thread(target=app.run, daemon=True)
    api_thread.start()
    
    # Wait for connection
    time.sleep(2)
    
    if not app.connected:
        print("Failed to connect!")
        return
        
    print("\n" + "="*60)
    print("TESTING OPTION DATA FETCHING")
    print("="*60)
    
    # 1. First get the underlying contract ID (needed for reqSecDefOptParams)
    print("\n1. Getting underlying contract details for AAPL...")
    stock_contract = Contract()
    stock_contract.symbol = "AAPL"
    stock_contract.secType = "STK"
    stock_contract.exchange = "SMART"
    stock_contract.currency = "USD"
    
    app.reqContractDetails(1, stock_contract)
    time.sleep(2)
    
    # 2. Use the RECOMMENDED method: reqSecDefOptParams
    print("\n2. Getting option chain using reqSecDefOptParams (RECOMMENDED)...")
    # Using AAPL's conId (265598)
    app.reqSecDefOptParams(2, "AAPL", "", "STK", 265598)
    time.sleep(3)
    
    # 3. Test getting market data for a specific option
    print("\n3. Testing market data for specific option (AAPL 230C Aug 15)...")
    
    # Create option contract according to documentation
    option = Contract()
    option.symbol = "AAPL"
    option.secType = "OPT"
    option.exchange = "SMART"
    option.currency = "USD"
    option.lastTradeDateOrContractMonth = "20250815"
    option.strike = 230.0
    option.right = "C"
    option.multiplier = "100"
    
    # Request delayed data if no real-time subscription
    print("Requesting delayed market data (free 15-min delayed)...")
    app.reqMarketDataType(3)  # 3 = DELAYED
    
    # Request market data - empty string gets all default ticks including Greeks
    print("Requesting market data with Greeks...")
    app.reqMktData(3, option, "", False, False, [])
    
    # Wait for data
    print("Waiting for data...")
    time.sleep(5)
    
    # Cancel market data
    app.cancelMktData(3)
    
    # 4. Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    if 2 in app.option_chains:
        chains = app.option_chains[2]
        total_strikes = set()
        for chain in chains:
            total_strikes.update(chain['strikes'])
        print(f"Total unique strikes found: {len(total_strikes)}")
        
        # Filter to reasonable strikes
        reasonable = [s for s in total_strikes if 100 <= s <= 350]
        print(f"Reasonable strikes (100-350): {len(reasonable)}")
        
    if 3 in app.market_data:
        print(f"Market data received: {app.market_data[3]}")
    
    # Disconnect
    print("\nDisconnecting...")
    app.disconnect()
    

if __name__ == "__main__":
    test_option_data()