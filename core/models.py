from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class OptionType(Enum):
    CALL = 'C'
    PUT = 'P'

@dataclass
class OptionContract:
    symbol: str
    strike: float
    expiry: str
    option_type: OptionType
    contract_id: Optional[int] = None
    multiplier: int = 100
    exchange: str = 'SMART'
    currency: str = 'USD'
    
    def to_ib_contract(self):
        from ib_insync import Option
        return Option(
            symbol=self.symbol,
            lastTradeDateOrContractMonth=self.expiry,
            strike=self.strike,
            right=self.option_type.value,
            exchange=self.exchange,
            currency=self.currency,
            multiplier=str(self.multiplier)
        )

@dataclass
class OptionQuote:
    bid: float
    ask: float
    last: float
    bid_size: int
    ask_size: int
    last_size: int
    volume: int
    open_interest: int
    timestamp: datetime
    
    @property
    def mid(self) -> float:
        if self.bid > 0 and self.ask > 0:
            return (self.bid + self.ask) / 2
        return 0.0
    
    @property
    def spread(self) -> float:
        if self.bid > 0 and self.ask > 0:
            return self.ask - self.bid
        return 0.0

@dataclass
class OptionGreeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    implied_volatility: float
    option_price: float
    underlying_price: float
    
    def is_valid(self) -> bool:
        return (
            self.delta is not None and 
            not (self.delta == 0 and self.gamma == 0 and self.theta == 0 and self.vega == 0)
        )

@dataclass
class OptionData:
    contract: OptionContract
    quote: OptionQuote
    greeks: OptionGreeks
    
    def to_dict(self) -> dict:
        return {
            'symbol': self.contract.symbol,
            'strike': self.contract.strike,
            'expiry': self.contract.expiry,
            'type': self.contract.option_type.value,
            'bid': self.quote.bid,
            'ask': self.quote.ask,
            'last': self.quote.last,
            'volume': self.quote.volume,
            'open_interest': self.quote.open_interest,
            'delta': self.greeks.delta,
            'gamma': self.greeks.gamma,
            'theta': self.greeks.theta,
            'vega': self.greeks.vega,
            'iv': self.greeks.implied_volatility,
            'underlying_price': self.greeks.underlying_price
        }

@dataclass
class OptionsChainData:
    symbol: str
    underlying_price: float
    timestamp: datetime
    calls: List[OptionData]
    puts: List[OptionData]
    
    def filter_by_strike_range(self, min_strike: float, max_strike: float):
        self.calls = [c for c in self.calls if min_strike <= c.contract.strike <= max_strike]
        self.puts = [p for p in self.puts if min_strike <= p.contract.strike <= max_strike]
        return self
    
    def filter_by_delta_range(self, min_delta: float, max_delta: float):
        self.calls = [c for c in self.calls if min_delta <= abs(c.greeks.delta) <= max_delta]
        self.puts = [p for p in self.puts if min_delta <= abs(p.greeks.delta) <= max_delta]
        return self
    
    def get_atm_options(self, num_strikes: int = 5):
        sorted_calls = sorted(self.calls, key=lambda x: abs(x.contract.strike - self.underlying_price))
        sorted_puts = sorted(self.puts, key=lambda x: abs(x.contract.strike - self.underlying_price))
        
        return {
            'calls': sorted_calls[:num_strikes],
            'puts': sorted_puts[:num_strikes]
        }