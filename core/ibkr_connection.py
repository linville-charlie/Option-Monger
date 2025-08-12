"""
IBKR Connection using official ibapi
"""
import threading
import time
import logging
from typing import Optional, Dict, List, Any
from queue import Queue, Empty

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.common import TickerId, TickAttrib

from .config import Config

logger = Config.setup_logging()


class IBKRApp(EWrapper, EClient):
    """Official IBKR API Application"""
    
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.nextOrderId = None
        self.data_queue = Queue()
        self.contract_details = {}
        self.market_data = {}
        self.option_chains = {}
        self.accounts = []
        self._errors = []
        
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        """Handle errors from IB"""
        if errorCode == 202:
            logger.warning(f"Order cancelled: {errorString}")
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
        
        tick_names = {
            1: 'bid',
            2: 'ask',
            4: 'last',
            6: 'high',
            7: 'low',
            9: 'close',
            14: 'open',
            66: 'delayed_bid',
            67: 'delayed_ask',
            68: 'delayed_last',
            72: 'delayed_high',
            73: 'delayed_low',
            75: 'delayed_close'
        }
        
        if tickType in tick_names:
            field_name = tick_names[tickType]
            self.market_data[reqId][field_name] = price
            # Also store delayed data as regular data if regular not available
            if tickType >= 66 and field_name.startswith('delayed_'):
                regular_field = field_name.replace('delayed_', '')
                if regular_field not in self.market_data[reqId]:
                    self.market_data[reqId][regular_field] = price
            
    def tickSize(self, reqId: TickerId, tickType, size):
        """Receive tick size"""
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
            
        size_names = {
            0: 'bid_size',
            3: 'ask_size',
            5: 'last_size',
            8: 'volume'
        }
        
        if tickType in size_names:
            self.market_data[reqId][size_names[tickType]] = size
            
    def tickGeneric(self, reqId: TickerId, tickType, value: float):
        """Receive generic tick"""
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
            
    def tickOptionComputation(self, reqId: TickerId, tickType, tickAttrib,
                            impliedVol: float, delta: float, optPrice: float,
                            pvDividend: float, gamma: float, vega: float,
                            theta: float, undPrice: float):
        """Receive option Greeks
        
        Tick types according to IBKR docs:
        10 = Bid Option Computation
        11 = Ask Option Computation  
        12 = Last Option Computation
        13 = Model Option Computation
        53 = Delayed Bid Option Computation
        54 = Delayed Ask Option Computation
        55 = Delayed Last Option Computation
        56 = Delayed Model Option Computation
        """
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
            
        # Map tick types to field names
        tick_type_names = {
            10: 'bid_greeks',
            11: 'ask_greeks',
            12: 'last_greeks',
            13: 'model_greeks',
            53: 'delayed_bid_greeks',
            54: 'delayed_ask_greeks',
            55: 'delayed_last_greeks',
            56: 'delayed_model_greeks'
        }
        
        if tickType in tick_type_names:
            field_name = tick_type_names[tickType]
            
            # Store the Greeks data
            greeks_data = {
                'implied_vol': impliedVol if impliedVol > 0 else None,
                'delta': delta if delta != -2 and delta != -1 else None,
                'gamma': gamma if gamma != -2 and gamma != -1 else None,
                'vega': vega if vega != -2 and vega != -1 else None,
                'theta': theta if theta != -2 and theta != -1 else None,
                'opt_price': optPrice if optPrice > 0 else None,
                'und_price': undPrice if undPrice > 0 else None
            }
            
            self.market_data[reqId][field_name] = greeks_data
            
            # For backward compatibility, also store model Greeks as 'greeks'
            if tickType == 13:
                self.market_data[reqId]['greeks'] = greeks_data
            # Use delayed model if model not available
            elif tickType == 56 and 'greeks' not in self.market_data[reqId]:
                self.market_data[reqId]['greeks'] = greeks_data
            
    def securityDefinitionOptionParameter(self, reqId: int, exchange: str,
                                         underlyingConId: int, tradingClass: str,
                                         multiplier: str, expirations, strikes):
        """Receive option chain parameters"""
        if reqId not in self.option_chains:
            self.option_chains[reqId] = []
            
        self.option_chains[reqId].append({
            'exchange': exchange,
            'trading_class': tradingClass,
            'multiplier': multiplier,
            'expirations': list(expirations),
            'strikes': list(strikes)
        })
        
    def securityDefinitionOptionParameterEnd(self, reqId: int):
        """End of option chain parameters"""
        logger.debug(f"Option chain parameters complete for request {reqId}")
        
    def managedAccounts(self, accountsList: str):
        """Receive managed accounts list"""
        self.accounts = accountsList.split(',')
        logger.info(f"Managed accounts: {self.accounts}")
        
    def currentTime(self, time: int):
        """Receive current server time"""
        from datetime import datetime
        server_time = datetime.fromtimestamp(time)
        logger.info(f"Server time: {server_time}")
    
    def marketDataType(self, reqId: TickerId, marketDataType: int):
        """Receive market data type notification
        1 = Real-time
        2 = Frozen
        3 = Delayed
        4 = Delayed-frozen
        """
        data_types = {1: "Real-time", 2: "Frozen", 3: "Delayed", 4: "Delayed-frozen"}
        logger.debug(f"Market data type for {reqId}: {data_types.get(marketDataType, marketDataType)}")


class IBKRConnection:
    """Connection manager for official IBKR API"""
    
    def __init__(self):
        self.app: Optional[IBKRApp] = None
        self.thread: Optional[threading.Thread] = None
        self.config = Config
        self._connected = False
        
    def connect(self) -> bool:
        """Connect to IB Gateway/TWS - matching your working test.py"""
        if self._connected and self.app and self.app.connected:
            logger.info("Already connected to IB Gateway")
            return True
            
        attempt = 0
        while attempt < self.config.MAX_RETRY_ATTEMPTS:
            try:
                self.app = IBKRApp()
                
                # Connect to IB Gateway exactly like your test.py
                logger.info(f"Connecting to IB Gateway at {self.config.TWS_HOST}:{self.config.get_port()}")
                self.app.connect(
                    self.config.TWS_HOST,
                    self.config.get_port(),
                    clientId=self.config.TWS_CLIENT_ID
                )
                
                # Wait briefly for socket connection like your test.py
                time.sleep(1)
                
                # Check if socket is connected
                if self.app.isConnected():
                    # Start message processing thread
                    self.thread = threading.Thread(target=self._run_loop, daemon=True)
                    self.thread.start()
                    
                    # Wait for connection callback
                    timeout = 3  # Shorter timeout for initial connection
                    start_time = time.time()
                    
                    while not self.app.connected and time.time() - start_time < timeout:
                        time.sleep(0.1)
                        
                    if self.app.connected:
                        self._connected = True
                        logger.info(f"Successfully connected to IB Gateway")
                        return True
                    else:
                        logger.warning(f"Connection attempt {attempt + 1} - no callback received")
                        self.disconnect()
                else:
                    logger.warning(f"Connection attempt {attempt + 1} - socket connection failed")
                    self.disconnect()
                    
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                
            attempt += 1
            if attempt < self.config.MAX_RETRY_ATTEMPTS:
                logger.info(f"Retrying in {self.config.RETRY_DELAY_SECONDS} seconds...")
                time.sleep(self.config.RETRY_DELAY_SECONDS)
                
        logger.error("Max retry attempts reached. Connection failed.")
        return False
        
    def _run_loop(self):
        """Run the message processing loop"""
        try:
            self.app.run()
        except Exception as e:
            logger.error(f"Error in message loop: {e}")
            self._connected = False
            
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
        
    def get_app(self) -> Optional[IBKRApp]:
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
            
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()