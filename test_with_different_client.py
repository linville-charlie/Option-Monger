#!/usr/bin/env python3
"""
Test with a different client ID to avoid competing session errors
"""
import time
from datetime import datetime
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.market_data = {}
        
    def error(self, reqId, errorCode, errorString):
        print(f"Error {errorCode}: {errorString}")
        
    def nextValidId(self, orderId):
        print(f"Connected! Next Valid Order ID: {orderId}")
        self.nextOrderId = orderId
        
    def tickPrice(self, reqId, tickType, price, attrib):
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
        
        tick_names = {
            1: 'bid', 2: 'ask', 4: 'last', 9: 'close',
            66: 'delayed_bid', 67: 'delayed_ask', 68: 'delayed_last'
        }
        
        if tickType in tick_names:
            field = tick_names[tickType]
            self.market_data[reqId][field] = price
            print(f"  {field}: ${price:.2f}")

def test_stock_price(client_id=2):
    """Test with a specific client ID"""
    print("="*60)
    print(f"TESTING WITH CLIENT ID {client_id}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    app = TestApp()
    
    # Try different client IDs to avoid conflicts
    print(f"\nConnecting with Client ID {client_id}...")
    app.connect("127.0.0.1", 8000, clientId=client_id)
    
    # Start message processing
    import threading
    api_thread = threading.Thread(target=app.run, daemon=True)
    api_thread.start()
    
    # Wait for connection
    time.sleep(2)
    
    # Create stock contract
    print("\nRequesting AAPL stock data...")
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    
    # Try real-time data first
    print("Requesting real-time data (type 1)...")
    app.reqMarketDataType(1)
    app.reqMktData(100, contract, "", False, False, [])
    
    # Wait for data
    print("Waiting for data...")
    time.sleep(5)
    
    # Check if we got data
    if 100 in app.market_data and app.market_data[100]:
        print(f"\n✅ Got market data: {app.market_data[100]}")
    else:
        print("\n⚠️ No real-time data. Trying delayed data...")
        
        # Cancel and try delayed data
        app.cancelMktData(100)
        time.sleep(1)
        
        # Request delayed data
        print("Requesting delayed data (type 3)...")
        app.reqMarketDataType(3)
        app.reqMktData(101, contract, "", False, False, [])
        
        # Wait for delayed data
        print("Waiting for delayed data...")
        time.sleep(5)
        
        if 101 in app.market_data and app.market_data[101]:
            print(f"\n✅ Got delayed data: {app.market_data[101]}")
        else:
            print("\n❌ No data received")
    
    # Disconnect
    app.disconnect()
    print("\nDisconnected")

if __name__ == "__main__":
    # Try different client IDs
    for client_id in [2, 3, 4]:
        try:
            test_stock_price(client_id)
            break  # If successful, stop trying
        except Exception as e:
            print(f"Failed with client ID {client_id}: {e}")
            continue