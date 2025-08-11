#!/usr/bin/env python3
"""
EXACT copy of your working test.py structure - no threading, no complexity
"""
from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import Contract
import time

class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 
        self.data = {}
        
    def nextValidId(self, orderId):
        print(f"Connected! Next Valid Order ID: {orderId}")
        
    def error(self, reqId, errorCode, errorString):
        print(f"Error {errorCode}: {errorString}")
        
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        print(f"Account: {account}, {tag}: {value} {currency}")
    
    def accountSummaryEnd(self, reqId: int):
        print("Account Summary End")
        
    def contractDetails(self, reqId, contractDetails):
        symbol = contractDetails.contract.symbol
        strike = contractDetails.contract.strike
        expiry = contractDetails.contract.lastTradeDateOrContractMonth
        print(f"Option: {symbol} {strike} {expiry}")
        
    def contractDetailsEnd(self, reqId):
        print(f"End of contract details for request {reqId}")

print("TESTING EXACTLY LIKE YOUR WORKING CODE")
print("="*60)

# EXACTLY your configuration
app = TradeApp()      
app.connect("127.0.0.1", 8000, clientId=0)
time.sleep(1)

# Request account summary like your code
print("\n1. Testing account summary (like your test.py):")
app.reqAccountSummary(9001, "All", 'NetLiquidation')

# Also test options
print("\n2. Testing options data:")
contract = Contract()
contract.symbol = "AAPL"
contract.secType = "OPT"
contract.exchange = "SMART"
contract.currency = "USD"
contract.lastTradeDateOrContractMonth = "20250919"
contract.right = "C"  # Calls only

app.reqContractDetails(1, contract)

# Run exactly like your code - NO THREADING
app.run()  # This blocks and processes messages