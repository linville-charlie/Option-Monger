# OptionMonger API Reference

## Main Interface

### `find_best_options()`
Primary function for covered call optimization.

```python
find_best_options(
    ticker: str,
    expiration: str,
    capital: float,
    verbose: bool = True
) -> Dict
```

#### Parameters
- `ticker` (str): Stock symbol (e.g., 'AAPL', 'MSFT')
- `expiration` (str): Option expiration date in YYYYMMDD format
- `capital` (float): Total capital to invest in buying shares
- `verbose` (bool): Print progress messages (default: True)

#### Returns
Dictionary containing:
- `shares_needed` (int): Number of shares to purchase
- `optimal_positions` (Dict[float, int]): {strike_price: num_contracts}
- `expected_pnl` (float): Expected profit/loss
- `win_rate` (float): Percentage chance of profit
- `premium_collected` (float): Total premium from selling calls
- `capital_for_shares` (float): Cost to buy shares
- `return_on_capital` (float): Return as percentage
- `var_95` (float): 5th percentile loss (Value at Risk)
- `max_gain` (float): Maximum possible profit
- `max_loss` (float): Maximum possible loss
- `recommendation` (str): Human-readable recommendation

#### Example
```python
results = find_best_options('AAPL', '20250117', 100000)
print(f"Buy {results['shares_needed']} shares")
print(f"Sell {results['optimal_positions']}")
```

---

## Data Fetching

### `get_all_strikes()`
Fetches all available option strikes from IBKR.

```python
get_all_strikes(
    ticker: str,
    expiration: str,
    return_stock_price: bool = False
) -> Tuple[pd.Series, pd.Series, pd.Series] or 
     Tuple[pd.Series, pd.Series, pd.Series, float]
```

#### Parameters
- `ticker` (str): Stock symbol
- `expiration` (str): Expiration date (YYYYMMDD)
- `return_stock_price` (bool): Include current stock price in return

#### Returns
- `bids` (pd.Series): Bid prices for each strike
- `strikes` (pd.Series): Strike prices
- `deltas` (pd.Series): Delta values for each strike
- `stock_price` (float): Current stock price (if requested)

#### Example
```python
# Without stock price
bids, strikes, deltas = get_all_strikes('AAPL', '20250117')

# With stock price
bids, strikes, deltas, price = get_all_strikes(
    'AAPL', '20250117', return_stock_price=True
)
```

### `get_option_data()`
Wrapper for get_all_strikes() with consistent naming.

```python
get_option_data(
    ticker: str,
    expiration: str,
    return_stock_price: bool = False
) -> Tuple
```

Same parameters and returns as `get_all_strikes()`.

---

## Optimization Functions

### `optimize_covered_calls()`
Optimizes covered call positions using Monte Carlo simulation.

```python
optimize_covered_calls(
    strikes: pd.Series,
    deltas: pd.Series,
    bids: pd.Series,
    capital: float,
    current_stock_price: float,
    max_contracts_per_strike: int = 100,
    n_simulations: int = 1000,
    n_candidates: int = 50,
    random_seed: Optional[int] = None
) -> Dict
```

#### Parameters
- `strikes` (pd.Series): Available strike prices
- `deltas` (pd.Series): Delta values (ITM probabilities)
- `bids` (pd.Series): Premium received per contract
- `capital` (float): Total capital for buying shares
- `current_stock_price` (float): Current stock price
- `max_contracts_per_strike` (int): Max contracts per strike
- `n_simulations` (int): Number of Monte Carlo simulations
- `n_candidates` (int): Number of portfolios to test
- `random_seed` (int, optional): For reproducibility

#### Returns
Dictionary with optimization results (same as find_best_options).

#### Example
```python
results = optimize_covered_calls(
    strikes, deltas, bids,
    capital=100000,
    current_stock_price=223.50,
    n_simulations=1000
)
```

### `optimize_covered_calls_continuous()`
Enhanced optimization with more thorough search.

```python
optimize_covered_calls_continuous(
    strikes: pd.Series,
    deltas: pd.Series,
    bids: pd.Series,
    capital: float,
    current_stock_price: float,
    max_contracts: Optional[int] = None,
    n_simulations: int = 200,
    random_seed: Optional[int] = None
) -> Dict
```

Similar parameters to `optimize_covered_calls()` but uses enhanced search strategies.

---

## Position Management

### `calculate_covered_call_pnl()`
Calculates P&L for covered call positions.

```python
calculate_covered_call_pnl(
    positions: pd.Series,
    strikes: pd.Series,
    bids: pd.Series,
    entry_price: float,
    exit_price: float,
    contract_multiplier: int = 100
) -> Dict
```

#### Parameters
- `positions` (pd.Series): Number of contracts at each strike
- `strikes` (pd.Series): Strike prices
- `bids` (pd.Series): Premium received per contract
- `entry_price` (float): Stock purchase price
- `exit_price` (float): Stock price at expiration
- `contract_multiplier` (int): Shares per contract (default: 100)

#### Returns
Dictionary containing:
- `premium_collected` (float): Total premium received
- `stock_pnl` (float): P&L from stock price movement
- `net_pnl` (float): Total P&L including premium
- `itm_positions` (pd.Series): Which positions expired ITM
- `shares_called` (int): Number of shares called away

#### Example
```python
pnl = calculate_covered_call_pnl(
    positions, strikes, bids,
    entry_price=223.00,
    exit_price=230.00
)
print(f"Net P&L: ${pnl['net_pnl']:,.2f}")
```

### `create_position_vector()`
Creates position vector with quantities.

```python
create_position_vector(
    strikes: pd.Series,
    positions: Dict[float, int]
) -> pd.Series
```

#### Parameters
- `strikes` (pd.Series): All available strikes
- `positions` (Dict): {strike_price: quantity}

#### Returns
- `pd.Series`: Position quantities aligned with strikes

#### Example
```python
positions_dict = {225.0: 5, 230.0: 3}
position_vector = create_position_vector(strikes, positions_dict)
```

---

## Connection Management

### `IBKRConnection`
Manages connection to IB Gateway.

```python
class IBKRConnection:
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 client_id: int = None)
    
    def connect(self, timeout: int = 30) -> bool
    def disconnect() -> None
    def is_connected() -> bool
```

#### Methods

##### `connect(timeout=30)`
Establishes connection to IB Gateway.
- Returns: `True` if successful, `False` otherwise

##### `disconnect()`
Cleanly disconnects from IB Gateway.

##### `is_connected()`
Checks connection status.
- Returns: `True` if connected, `False` otherwise

#### Example
```python
conn = IBKRConnection()
if conn.connect():
    # Use connection
    conn.disconnect()
```

---

## Data Fetching Classes

### `OptionsDataFetcher`
Fetches option data from IBKR.

```python
class OptionsDataFetcher:
    def __init__(self, connection: IBKRConnection)
    
    def get_underlying_price(self, symbol: str) -> float
    def get_option_strikes(self, symbol: str, expiry: str) -> List[float]
    def get_option_data(self, symbol: str, expiry: str, 
                       strike: float, option_type: OptionType) -> OptionData
```

#### Methods

##### `get_underlying_price(symbol)`
Gets current stock price.
- Returns: Current price as float

##### `get_option_strikes(symbol, expiry)`
Gets available strikes for expiration.
- Returns: List of strike prices

##### `get_option_data(symbol, expiry, strike, option_type)`
Gets full option details including Greeks.
- Returns: OptionData object with quote and Greeks

#### Example
```python
fetcher = OptionsDataFetcher(conn)
price = fetcher.get_underlying_price('AAPL')
strikes = fetcher.get_option_strikes('AAPL', '20250117')
```

---

## Data Models

### `OptionData`
Complete option information.

```python
@dataclass
class OptionData:
    contract: OptionContract
    quote: OptionQuote
    greeks: OptionGreeks
```

### `OptionContract`
Option contract details.

```python
@dataclass
class OptionContract:
    symbol: str
    expiry: str
    strike: float
    option_type: OptionType
```

### `OptionQuote`
Market quotes for option.

```python
@dataclass
class OptionQuote:
    bid: float
    ask: float
    last: float
    volume: int
    open_interest: int
```

### `OptionGreeks`
Option Greeks values.

```python
@dataclass
class OptionGreeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    implied_vol: float
```

---

## Utility Functions

### `monte_carlo_simulation()`
Runs Monte Carlo simulation for option positions.

```python
monte_carlo_simulation(
    positions: pd.Series,
    strikes: pd.Series,
    deltas: pd.Series,
    bids: pd.Series,
    current_price: float,
    n_simulations: int = 1000,
    random_seed: Optional[int] = None
) -> Dict
```

#### Returns
Dictionary with simulation results:
- `expected_pnl` (float): Mean P&L across simulations
- `std_pnl` (float): Standard deviation of P&L
- `var_95` (float): 5th percentile (Value at Risk)
- `cvar_95` (float): Conditional VaR
- `win_rate` (float): Percentage of profitable outcomes

---

## Configuration

### Environment Variables
Set in `.env` file:

```python
TWS_HOST = "172.21.112.1"  # IB Gateway host
TWS_PORT = 8000            # IB Gateway port
TWS_CLIENT_ID = 1          # Client ID (avoid conflicts)
ACCOUNT_ID = "YOUR_ACCOUNT_ID"   # Your IB account
```

### Accessing Config
```python
from core.config import Config

config = Config()
print(config.tws_host)
print(config.tws_port)
```

---

## Error Handling

### Custom Exceptions

```python
class ConnectionError(Exception):
    """Failed to connect to IB Gateway"""

class InsufficientCapitalError(ValueError):
    """Not enough capital for minimum position"""

class NoDataError(Exception):
    """No market data available"""
```

### Error Handling Example
```python
try:
    results = find_best_options('AAPL', '20250117', 10000)
except InsufficientCapitalError as e:
    print(f"Need more capital: {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except NoDataError as e:
    print(f"No market data: {e}")
```

---

## Constants

### Trading Constants
```python
CONTRACT_MULTIPLIER = 100  # Shares per option contract
MIN_PREMIUM = 0.50        # Minimum acceptable bid
MAX_CONTRACTS = 100       # Default max per strike
DEFAULT_SIMULATIONS = 1000  # Monte Carlo iterations
```

### Connection Constants
```python
DEFAULT_PORT = 8000       # IB Gateway port
DEFAULT_CLIENT_ID = 1     # Avoid competing sessions
CONNECTION_TIMEOUT = 30   # Seconds to wait
RATE_LIMIT_DELAY = 0.1   # Between API calls
```

---

## Type Definitions

```python
from typing import Dict, List, Tuple, Optional, Union
import pandas as pd
import numpy as np

# Custom type aliases
StrikePositions = Dict[float, int]  # {strike: quantity}
OptionVector = pd.Series           # Aligned series
PnLResult = Dict[str, float]       # P&L components
```

---

## Quick Examples

### Basic Covered Call
```python
# Simple covered call optimization
results = find_best_options('SPY', '20250117', 50000)
print(results['recommendation'])
```

### Advanced Analysis
```python
# Get data and optimize manually
bids, strikes, deltas, price = get_all_strikes(
    'AAPL', '20250117', return_stock_price=True
)

results = optimize_covered_calls(
    strikes, deltas, bids,
    capital=100000,
    current_stock_price=price,
    n_simulations=5000  # More simulations
)
```

### Multiple Expirations
```python
# Compare different expiration dates
expirations = ['20250117', '20250221', '20250321']
best_return = 0
best_expiry = None

for expiry in expirations:
    results = find_best_options('AAPL', expiry, 100000, verbose=False)
    if results['return_on_capital'] > best_return:
        best_return = results['return_on_capital']
        best_expiry = expiry

print(f"Best expiration: {best_expiry} ({best_return:.2f}%)")
```