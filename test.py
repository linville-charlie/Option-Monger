from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import Contract
import time
class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 
    def accountSummary(self, reqId: int, account: str, tag: str, value: str,currency: str):
        print("AccountSummary. ReqId:", reqId, "Account:", account,"Tag: ", tag, "Value:", value, "Currency:", currency)
    
    def accountSummaryEnd(self, reqId: int):
        print("AccountSummaryEnd. ReqId:", reqId)
    
app = TradeApp()      
app.connect("172.21.112.1", 8000, clientId=0)
time.sleep(1)
app.reqAccountSummary(9001, "All", 'NetLiquidation')
app.run()