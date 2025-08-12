#!/usr/bin/env python3
"""
Diagnostic script to see what market data we can actually get
"""
import time
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class DataTestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.data_received = {}
        
    def error(self, reqId, errorCode, errorString):
        print(f"Error {errorCode}: {errorString}")
        
    def nextValidId(self, orderId):
        self.connected = True
        print(f"Connected! Next Order ID: {orderId}")
        
    def marketDataType(self, reqId, marketDataType):
        types = {1: "Real-time", 2: "Frozen", 3: "Delayed", 4: "Delayed-frozen"}
        print(f"[{reqId}] Market data type: {types.get(marketDataType, marketDataType)}")
        
    def tickPrice(self, reqId, tickType, price, attrib):
        print(f"[{reqId}] PRICE TICK {tickType}: ${price:.2f}")
        if reqId not in self.data_received:
            self.data_received[reqId] = {}
        self.data_received[reqId][f'price_{tickType}'] = price
        
    def tickSize(self, reqId, tickType, size):
        print(f"[{reqId}] SIZE TICK {tickType}: {size}")
        
    def tickGeneric(self, reqId, tickType, value):
        print(f"[{reqId}] GENERIC TICK {tickType}: {value}")
        
    def tickString(self, reqId, tickType, value):
        # Only show non-exchange strings
        if tickType not in [32, 33, 45, 84]:
            print(f"[{reqId}] STRING TICK {tickType}: {value}")
            
    def tickOptionComputation(self, reqId, tickType, tickAttrib, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice):
        print(f"[{reqId}] GREEKS TICK {tickType}:")
        if delta > -2:
            print(f"  Delta={delta:.4f}, Gamma={gamma:.4f}, Theta={theta:.4f}, Vega={vega:.4f}")
        if impliedVol > 0:
            print(f"  IV={impliedVol:.2%}")


def test_data():
    app = DataTestApp()
    app.connect("127.0.0.1", 8000, clientId=0)
    
    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()
    time.sleep(2)
    
    if not app.connected:
        print("Failed to connect!")
        return
        
    print("\n" + "="*60)
    print("TESTING WHAT DATA WE CAN GET")
    print("="*60)
    
    # Test 1: Stock data (should work)
    print("\n1. Testing STOCK data (AAPL)...")
    stock = Contract()
    stock.symbol = "AAPL"
    stock.secType = "STK"
    stock.exchange = "SMART"
    stock.currency = "USD"
    
    app.reqMarketDataType(3)  # Request DELAYED data
    app.reqMktData(100, stock, "", False, False, [])
    time.sleep(3)
    app.cancelMktData(100)
    
    # Test 2: Option with different generic tick lists
    print("\n2. Testing OPTION data (AAPL 230C Aug 15) - Empty tick list...")
    option = Contract()
    option.symbol = "AAPL"
    option.secType = "OPT"
    option.exchange = "SMART"
    option.currency = "USD"
    option.lastTradeDateOrContractMonth = "20250815"
    option.strike = 230.0
    option.right = "C"
    option.multiplier = "100"
    
    app.reqMarketDataType(3)  # DELAYED
    app.reqMktData(101, option, "", False, False, [])  # Empty string
    time.sleep(3)
    app.cancelMktData(101)
    
    # Test 3: With specific generic ticks
    print("\n3. Testing OPTION with tick list '100,101,104,106'...")
    app.reqMktData(102, option, "100,101,104,106", False, False, [])
    time.sleep(3)
    app.cancelMktData(102)
    
    # Test 4: With bid/ask size ticks
    print("\n4. Testing OPTION with tick list '0,1,2,3,4,5'...")
    app.reqMktData(103, option, "0,1,2,3,4,5", False, False, [])
    time.sleep(3)
    app.cancelMktData(103)
    
    # Test 5: Snapshot mode
    print("\n5. Testing OPTION snapshot mode...")
    app.reqMktData(104, option, "", True, False, [])  # snapshot=True
    time.sleep(3)
    
    print("\n" + "="*60)
    print("SUMMARY OF DATA RECEIVED:")
    print("="*60)
    for req_id, data in app.data_received.items():
        print(f"Request {req_id}: {data}")
    
    if not app.data_received:
        print("NO PRICE DATA RECEIVED!")
        print("\nPossible issues:")
        print("1. No market data subscription for options (need OPRA)")
        print("2. Market is closed and no delayed data available")
        print("3. Need to subscribe to delayed data in IB Gateway")
        print("\nTo fix:")
        print("1. In IB Gateway: Configure > Settings > API > Settings")
        print("2. Check 'Download open orders on connection'")
        print("3. Configure > Settings > Market Data")
        print("4. Enable delayed data if you don't have subscriptions")
    
    app.disconnect()


if __name__ == "__main__":
    test_data()