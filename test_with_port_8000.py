#!/usr/bin/env python3
"""
Test using YOUR WORKING configuration from test.py
Port 8000, clientId=0, localhost
"""
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import time
import threading

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        
    def error(self, reqId, errorCode, errorString):
        print(f"Error {errorCode}: {errorString}")
        
    def nextValidId(self, orderId):
        self.connected = True
        print(f"Connected! Next order ID: {orderId}")
        
    def accountSummary(self, reqId, account, tag, value, currency):
        print(f"Account: {account}, {tag}: {value} {currency}")
        
    def contractDetails(self, reqId, contractDetails):
        print(f"Contract: {contractDetails.contract.symbol}")
        print(f"  Strike: {contractDetails.contract.strike}")
        print(f"  Expiry: {contractDetails.contract.lastTradeDateOrContractMonth}")

print("TESTING WITH YOUR WORKING CONFIGURATION")
print("="*60)
print("Using: localhost:8000, clientId=0 (from your test.py)")
print("="*60)

# YOUR EXACT WORKING CONFIGURATION
HOST = "127.0.0.1"
PORT = 8000  # Your working port!
CLIENT_ID = 0  # Your working client ID!

app = TestApp()

# Connect exactly like your test.py
print(f"Connecting to {HOST}:{PORT} with clientId={CLIENT_ID}")
app.connect(HOST, PORT, CLIENT_ID)

# Small delay like your test.py
time.sleep(1)

# Start message thread
thread = threading.Thread(target=app.run, daemon=True)
thread.start()

# Wait for connection
time.sleep(2)

if app.connected:
    print("\n✅ CONNECTION SUCCESSFUL!")
    
    # Test account summary like your script
    print("\nRequesting account summary...")
    app.reqAccountSummary(9001, "All", 'NetLiquidation')
    time.sleep(2)
    
    # Test options data
    print("\nRequesting AAPL option chain...")
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "OPT"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.lastTradeDateOrContractMonth = "20250919"
    
    app.reqContractDetails(1, contract)
    time.sleep(3)
    
    app.disconnect()
else:
    print("❌ Failed to connect")
    print("Make sure IB Gateway is running on port 8000")

print("\n" + "="*60)
print("TO FIX OUR CODE:")
print("1. Update .env file:")
print("   TWS_HOST=127.0.0.1")
print("   TWS_PAPER_PORT=8000")
print("   TWS_CLIENT_ID=0")
print("2. Or set environment variables")
print("="*60)