"""
Options data fetcher using official IBKR API
"""
import time
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from collections import defaultdict

from ibapi.contract import Contract
from ibapi.order import Order

from .models import (
    OptionContract, OptionQuote, OptionGreeks,
    OptionData, OptionsChainData, OptionType
)
from .ibkr_connection import IBKRConnection
from .config import Config

logger = logging.getLogger(__name__)


class OptionsDataFetcher:
    """Fetch options data using official IBKR API"""
    
    def __init__(self, connection: Optional[IBKRConnection] = None):
        self.connection = connection or IBKRConnection()
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self._req_id_counter = 100
        
    def _get_next_req_id(self) -> int:
        """Get next request ID"""
        self._req_id_counter += 1
        return self._req_id_counter
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache is still valid"""
        if key not in self.cache_timestamps:
            return False
        elapsed = (datetime.now() - self.cache_timestamps[key]).total_seconds()
        return elapsed < Config.CACHE_EXPIRY_SECONDS
        
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        if self._is_cache_valid(key):
            logger.debug(f"Cache hit for {key}")
            return self.cache.get(key)
        return None
        
    def _save_to_cache(self, key: str, data: Any):
        """Save data to cache"""
        self.cache[key] = data
        self.cache_timestamps[key] = datetime.now()
        logger.debug(f"Cached data for {key}")
        
    def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock market data"""
        cache_key = f"stock_data_{symbol}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        app = self.connection.get_app()
        if not app:
            logger.error("Failed to get IBKR connection")
            return None
            
        try:
            # Create stock contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            req_id = self._get_next_req_id()
            
            # Request market data
            app.reqMktData(req_id, contract, "", False, False, [])
            
            # Wait for data
            time.sleep(3)
            
            # Cancel market data
            app.cancelMktData(req_id)
            
            if req_id in app.market_data:
                data = app.market_data[req_id]
                
                stock_data = {
                    'symbol': symbol,
                    'last': data.get('last'),
                    'bid': data.get('bid'),
                    'ask': data.get('ask'),
                    'open': data.get('open'),
                    'high': data.get('high'),
                    'low': data.get('low'),
                    'close': data.get('close'),
                    'volume': data.get('volume', 0),
                    'bid_size': data.get('bid_size', 0),
                    'ask_size': data.get('ask_size', 0),
                    'timestamp': datetime.now()
                }
                
                # Calculate change
                if stock_data['last'] and stock_data['close']:
                    stock_data['change'] = stock_data['last'] - stock_data['close']
                    stock_data['change_pct'] = (stock_data['change'] / stock_data['close']) * 100
                else:
                    stock_data['change'] = None
                    stock_data['change_pct'] = None
                    
                self._save_to_cache(cache_key, stock_data)
                return stock_data
            else:
                logger.warning(f"No market data received for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting stock data for {symbol}: {e}")
            return None
            
    def get_underlying_price(self, symbol: str) -> Optional[float]:
        """Get underlying stock price"""
        stock_data = self.get_stock_data(symbol)
        if stock_data:
            return stock_data.get('last') or stock_data.get('close')
        return None
        
    def get_option_chain_dates(self, symbol: str) -> List[str]:
        """Get available option expiration dates"""
        cache_key = f"chain_dates_{symbol}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        app = self.connection.get_app()
        if not app:
            return []
            
        try:
            # First, get the underlying contract ID
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            req_id = self._get_next_req_id()
            app.reqContractDetails(req_id, contract)
            time.sleep(2)
            
            underlying_con_id = 0
            if req_id in app.contract_details and app.contract_details[req_id]:
                underlying_con_id = app.contract_details[req_id][0].contract.conId
                logger.debug(f"Found underlying contract ID: {underlying_con_id}")
            
            # Now request option chain parameters with the correct contract ID
            req_id = self._get_next_req_id()
            app.reqSecDefOptParams(req_id, symbol, "", "STK", underlying_con_id)
            
            # Wait for response
            time.sleep(3)
            
            if req_id in app.option_chains:
                chains = app.option_chains[req_id]
                if chains:
                    # Get unique expirations from all exchanges
                    expirations = set()
                    for chain in chains:
                        expirations.update(chain['expirations'])
                    
                    expirations = sorted(list(expirations))
                    self._save_to_cache(cache_key, expirations)
                    return expirations
                    
            logger.warning(f"No option chains found for {symbol}")
            return []
            
        except Exception as e:
            logger.error(f"Error getting option chain dates for {symbol}: {e}")
            return []
            
    def get_option_strikes(self, symbol: str, expiry: str = None) -> List[float]:
        """Get available option strikes"""
        cache_key = f"strikes_{symbol}_{expiry}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        app = self.connection.get_app()
        if not app:
            return []
            
        try:
            # First, get the underlying contract ID
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            req_id = self._get_next_req_id()
            app.reqContractDetails(req_id, contract)
            time.sleep(2)
            
            underlying_con_id = 0
            if req_id in app.contract_details and app.contract_details[req_id]:
                underlying_con_id = app.contract_details[req_id][0].contract.conId
            
            # Now request option chain parameters
            req_id = self._get_next_req_id()
            app.reqSecDefOptParams(req_id, symbol, "", "STK", underlying_con_id)
            
            # Wait for response
            time.sleep(3)
            
            if req_id in app.option_chains:
                chains = app.option_chains[req_id]
                if chains:
                    # Get unique strikes from all exchanges
                    strikes = set()
                    for chain in chains:
                        strikes.update(chain['strikes'])
                    
                    strikes = sorted(list(strikes))
                    self._save_to_cache(cache_key, strikes)
                    return strikes
                    
            return []
            
        except Exception as e:
            logger.error(f"Error getting strikes for {symbol}: {e}")
            return []
            
    def get_option_data(self, symbol: str, expiry: str, strike: float,
                       option_type: OptionType) -> Optional[OptionData]:
        """Get data for a specific option"""
        app = self.connection.get_app()
        if not app:
            return None
            
        try:
            # Create option contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "OPT"
            contract.exchange = "SMART"
            contract.currency = "USD"
            contract.lastTradeDateOrContractMonth = expiry
            contract.strike = strike
            contract.right = option_type.value
            contract.multiplier = "100"
            
            req_id = self._get_next_req_id()
            
            # Request real-time market data (since you have subscription)
            # Use type 1 for real-time, type 3 for delayed
            app.reqMarketDataType(1)  # 1 = REAL-TIME (requires subscription)
            
            # Request market data with prices AND Greeks
            # Request both price ticks and computed Greeks (tick type 13)
            # Empty string gets bid/ask/last prices by default
            app.reqMktData(req_id, contract, "", False, False, [])
            
            # Wait for data (longer for delayed data)
            time.sleep(5)
            
            # Cancel market data
            app.cancelMktData(req_id)
            
            if req_id in app.market_data:
                data = app.market_data[req_id]
                
                # Create option contract model
                option_contract = OptionContract(
                    symbol=symbol,
                    strike=strike,
                    expiry=expiry,
                    option_type=option_type
                )
                
                # Create quote
                quote = OptionQuote(
                    bid=data.get('bid', 0.0),
                    ask=data.get('ask', 0.0),
                    last=data.get('last', 0.0),
                    bid_size=data.get('bid_size', 0),
                    ask_size=data.get('ask_size', 0),
                    last_size=data.get('last_size', 0),
                    volume=data.get('volume', 0),
                    open_interest=0,  # Not available in real-time
                    timestamp=datetime.now()
                )
                
                # Create Greeks
                greeks_data = data.get('greeks', {})
                underlying_price = self.get_underlying_price(symbol) or 0.0
                
                greeks = OptionGreeks(
                    delta=greeks_data.get('delta', 0.0),
                    gamma=greeks_data.get('gamma', 0.0),
                    theta=greeks_data.get('theta', 0.0),
                    vega=greeks_data.get('vega', 0.0),
                    rho=0.0,  # Not provided by default
                    implied_volatility=greeks_data.get('implied_vol', 0.0),
                    option_price=greeks_data.get('opt_price', 0.0),
                    underlying_price=underlying_price
                )
                
                return OptionData(
                    contract=option_contract,
                    quote=quote,
                    greeks=greeks
                )
            else:
                logger.warning(f"No option data received for {symbol} {expiry} {strike} {option_type.value}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting option data: {e}")
            return None
            
    def get_options_chain(self, symbol: str, expiry: Optional[str] = None,
                         min_strike: Optional[float] = None,
                         max_strike: Optional[float] = None) -> Optional[OptionsChainData]:
        """Get full options chain"""
        app = self.connection.get_app()
        if not app:
            return None
            
        try:
            # Get expiration dates if not provided
            if not expiry:
                expirations = self.get_option_chain_dates(symbol)
                if not expirations:
                    logger.error(f"No expirations found for {symbol}")
                    return None
                expiry = expirations[0]
                
            # Get underlying price
            underlying_price = self.get_underlying_price(symbol)
            if not underlying_price:
                logger.warning(f"Could not get underlying price for {symbol}")
                underlying_price = 0.0
                
            # Get strikes
            strikes = self.get_option_strikes(symbol, expiry)
            if not strikes:
                logger.error(f"No strikes found for {symbol}")
                return None
                
            # Filter strikes
            if min_strike is None:
                min_strike = underlying_price * 0.8
            if max_strike is None:
                max_strike = underlying_price * 1.2
                
            filtered_strikes = [s for s in strikes if min_strike <= s <= max_strike]
            
            calls = []
            puts = []
            
            # Fetch data for each strike
            for strike in filtered_strikes:
                logger.info(f"Fetching options for {symbol} {expiry} strike {strike}")
                
                # Get call data
                call_data = self.get_option_data(symbol, expiry, strike, OptionType.CALL)
                if call_data:
                    calls.append(call_data)
                    
                # Get put data
                put_data = self.get_option_data(symbol, expiry, strike, OptionType.PUT)
                if put_data:
                    puts.append(put_data)
                    
                # Small delay to avoid overwhelming the API
                time.sleep(0.2)
                
            return OptionsChainData(
                symbol=symbol,
                underlying_price=underlying_price,
                timestamp=datetime.now(),
                calls=calls,
                puts=puts
            )
            
        except Exception as e:
            logger.error(f"Error getting options chain: {e}")
            return None
            
    def export_to_dataframe(self, chain_data: OptionsChainData):
        """Export options chain to DataFrame"""
        import pandas as pd
        
        all_options = []
        
        for call in chain_data.calls:
            data = call.to_dict()
            all_options.append(data)
            
        for put in chain_data.puts:
            data = put.to_dict()
            all_options.append(data)
            
        df = pd.DataFrame(all_options)
        if not df.empty:
            df = df.sort_values(['type', 'strike'])
            
        return df
        
    def export_to_csv(self, chain_data: OptionsChainData, filename: str):
        """Export options chain to CSV"""
        df = self.export_to_dataframe(chain_data)
        df.to_csv(filename, index=False)
        logger.info(f"Exported options data to {filename}")