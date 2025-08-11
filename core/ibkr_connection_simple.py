"""
Simple IBKR Connection - No Threading, Like Your Working test.py
This version matches your working configuration exactly.
"""
import time
import logging
from typing import Optional, Dict, List, Any
from queue import Queue

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import TickerId, TickAttrib

from .config import Config

logger = Config.setup_logging()


class SimpleIBKRApp(EWrapper, EClient):
    """Simple IBKR API Application - No Threading"""
    
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.nextOrderId = None
        self.contract_details = {}
        self.market_data = {}
        self.option_chains = {}
        self.accounts = []
        self._errors = []
        self._last_request_id = 0
        
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        """Handle errors from IB"""
        if errorCode == 202:
            logger.warning(f"Order cancelled: {errorString}")
        elif errorCode == 502:
            logger.error(f"Cannot connect: {errorString}")
            self._errors.append((errorCode, errorString))
        elif errorCode >= 2000:
            logger.error(f"Error {errorCode}: {errorString}")
            self._errors.append((errorCode, errorString))
        else:
            logger.info(f"Info {errorCode}: {errorString}")
            
    def nextValidId(self, orderId: int):
        """Receive next valid order ID"""
        self.nextOrderId = orderId
        self.connected = True
        logger.info(f"Connected! Next Valid Order ID: {orderId}")
        
    def contractDetails(self, reqId: int, contractDetails):
        """Receive contract details"""
        if reqId not in self.contract_details:
            self.contract_details[reqId] = []
        self.contract_details[reqId].append(contractDetails)
        
    def contractDetailsEnd(self, reqId: int):
        """End of contract details"""
        logger.debug(f"Contract details complete for request {reqId}")
        
    def tickPrice(self, reqId: TickerId, tickType, price: float, attrib: TickAttrib):
        """Receive tick price"""
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
            
        # Map tick types to field names
        tick_map = {
            1: 'bid',
            2: 'ask',
            4: 'last',
            6: 'high',
            7: 'low',
            9: 'close'
        }
        
        if tickType in tick_map:
            self.market_data[reqId][tick_map[tickType]] = price
            
    def tickSize(self, reqId: TickerId, tickType, size: int):
        """Receive tick size"""
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
            
        # Map tick types to field names
        tick_map = {
            0: 'bid_size',
            3: 'ask_size',
            5: 'last_size',
            8: 'volume'
        }
        
        if tickType in tick_map:
            self.market_data[reqId][tick_map[tickType]] = size
            
    def tickOptionComputation(self, reqId: TickerId, tickType,
                            impliedVol: float, delta: float, optPrice: float,
                            pvDividend: float, gamma: float, vega: float,
                            theta: float, undPrice: float):
        """Receive option Greeks"""
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
            
        # Model Greeks (tickType 13)
        if tickType == 13:
            self.market_data[reqId]['greeks'] = {
                'implied_vol': impliedVol if impliedVol != -1 else None,
                'delta': delta if delta != -2 else None,
                'gamma': gamma if gamma != -2 else None,
                'vega': vega if vega != -2 else None,
                'theta': theta if theta != -2 else None,
                'opt_price': optPrice if optPrice != -1 else None,
                'und_price': undPrice if undPrice != -1 else None
            }
            
    def managedAccounts(self, accountsList: str):
        """Receive managed accounts list"""
        self.accounts = accountsList.split(',')
        logger.info(f"Managed accounts: {self.accounts}")
        
    def currentTime(self, time: int):
        """Receive current server time"""
        from datetime import datetime
        server_time = datetime.fromtimestamp(time)
        logger.info(f"Server time: {server_time}")

    def get_next_request_id(self) -> int:
        """Get next request ID"""
        self._last_request_id += 1
        return self._last_request_id


class SimpleIBKRConnection:
    """Simple connection manager - No Threading, Like Your test.py"""
    
    def __init__(self):
        self.app: Optional[SimpleIBKRApp] = None
        self.config = Config
        self._connected = False
        
    def connect(self) -> bool:
        """Connect to IB Gateway/TWS without threading"""
        if self._connected and self.app and self.app.connected:
            logger.info("Already connected to IB Gateway")
            return True
            
        try:
            self.app = SimpleIBKRApp()
            
            # Connect exactly like your test.py
            logger.info(f"Connecting to IB Gateway at {self.config.TWS_HOST}:{self.config.get_port()}")
            self.app.connect(
                self.config.TWS_HOST,
                self.config.get_port(),
                clientId=self.config.TWS_CLIENT_ID
            )
            
            # Small delay like your test.py
            time.sleep(1)
            
            # Check if connected (don't run yet)
            if self.app.isConnected():
                # Start the message processing
                # This will process initial messages
                import threading
                self.thread = threading.Thread(target=self.app.run, daemon=True)
                self.thread.start()
                
                # Wait for connection callback
                time.sleep(2)
                
                if self.app.connected:
                    self._connected = True
                    logger.info("Successfully connected to IB Gateway")
                    return True
                else:
                    logger.warning("Connection failed - no callback received")
                    self.disconnect()
                    return False
            else:
                logger.error("Failed to establish socket connection")
                return False
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from IB Gateway"""
        if self.app:
            try:
                self.app.disconnect()
                self._connected = False
                logger.info("Disconnected from IB Gateway")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
                
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected and self.app and self.app.connected
        
    def get_app(self) -> Optional[SimpleIBKRApp]:
        """Get the app instance"""
        if not self.is_connected():
            if not self.connect():
                return None
        return self.app
        
    def test_connection(self) -> bool:
        """Test the connection"""
        if not self.connect():
            return False
            
        try:
            # Request current time as a test
            self.app.reqCurrentTime()
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False