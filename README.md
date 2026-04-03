# OptionMonger

A covered call optimization system for Interactive Brokers that uses Monte Carlo simulation to find optimal strike prices, maximizing premium income while managing assignment risk.

## Overview

OptionMonger connects to IB Gateway, fetches live options chain data, and runs thousands of Monte Carlo scenarios to identify the best covered call positions for a given capital allocation. It evaluates every available strike, calculating expected P&L, win rates, and risk metrics to produce actionable trade recommendations. The entire math pipeline is vectorized with NumPy for fast batch evaluation across hundreds of candidate positions.

## How Covered Calls Work

### Money In

1. **Buy shares** with available capital (100 shares per contract)
2. **Sell call options** against those shares, collecting premium upfront

### Money Out (At Expiration)

- **ITM strikes**: Shares are called away at the strike price -- you keep the premium plus the difference between strike and purchase price
- **OTM strikes**: You keep the shares and the full premium -- sell shares at market price
- **Mixed outcomes**: Each contract is evaluated independently

### P&L Formula

```
Total P&L = Premium Collected + (Exit Price - Entry Price) x Shares
```

Where exit price is the strike price (if ITM) or market price (if OTM).

## Features

- **Live Market Data Integration** -- Real-time options chains, bid prices, deltas, and stock prices from Interactive Brokers via IB Gateway
- **Monte Carlo Optimization** -- Simulates thousands of price paths using option deltas as ITM probabilities to evaluate expected outcomes at each strike
- **Vectorized P&L Engine** -- Positions, ITM masks, exercise vectors, and premium calculations all use Hadamard (element-wise) multiplication on aligned pandas Series
- **Multi-Strike Optimization** -- Spreads contracts across multiple strikes when capital supports it, testing dozens of candidate portfolios
- **Risk Metrics** -- Value at Risk (VaR), win rate, expected P&L, and return on capital for every candidate position
- **Position Tracking** -- Binary position vectors with quantities, ITM/OTM classification, and net P&L decomposition
- **Interactive Notebooks** -- Jupyter notebooks for live trading analysis and visualization during market hours
- **Capital-Aware Sizing** -- Automatically calculates maximum shares and contracts from available capital and current stock price

## Architecture

```
OptionMonger/
├── YOUR_MAIN_INTERFACE.py              # Main API: find_best_options(), get_option_data()
│
├── core/
│   ├── covered_call_optimization.py    # Strike optimization engine
│   ├── simulation.py                   # Monte Carlo price path simulation
│   ├── position_tracker.py             # Vector math: positions, ITM, exercise, P&L
│   ├── simple_real_strikes.py          # Options chain + stock price retrieval
│   ├── options_data.py                 # Options data structures and processing
│   ├── ibkr_connection.py              # IB Gateway connection management
│   ├── ibkr_connection_simple.py       # Simplified connection wrapper
│   ├── models.py                       # Data models
│   └── config.py                       # Connection and runtime configuration
│
├── notebooks/
│   ├── live_options_trading.ipynb             # Full interactive trading notebook
│   └── live_options_trading_optimized.ipynb   # Streamlined version for live use
│
├── utilities/
│   ├── debug_stock_price.py            # Stock price retrieval debugging
│   ├── check_sessions.py               # Check for competing IB sessions
│   ├── kill_all_connections.py          # Reset all IB client connections
│   └── use_next_client_id.py           # Auto-increment client ID
│
├── tests/                              # Unit and integration tests
├── docs/                               # Detailed documentation
│   ├── API_REFERENCE.md                # Complete API reference
│   ├── SYSTEM_ARCHITECTURE.md          # System design and data flow
│   ├── COVERED_CALLS_GUIDE.md          # Strategy guide with examples
│   ├── USER_GUIDE.md                   # End-to-end usage instructions
│   ├── IB_GATEWAY_SETUP.md             # IB Gateway configuration
│   ├── NEW_DEVICE_SETUP.md             # Environment setup from scratch
│   └── INSTALLATION.md                 # Installation steps
└── examples/                           # Usage examples
```

## Core API

### `find_best_options(ticker, expiration, capital)`

The main entry point. Returns optimal covered call positions for a given ticker, expiration, and capital.

```python
from YOUR_MAIN_INTERFACE import find_best_options

results = find_best_options('AAPL', '20250815', 100000)

print(f"Buy {results['shares_needed']} shares at ${results['current_stock_price']:.2f}")
print(f"Capital for shares: ${results['capital_for_shares']:,.2f}")
print(f"Sell calls at: {results['optimal_positions']}")
print(f"Premium collected: ${results['premium_collected']:,.2f}")
print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
print(f"Return on capital: {results['return_on_capital']:.2%}")
```

### `get_option_data(ticker, expiration)`

Returns three aligned vectors for manual analysis:

```python
from YOUR_MAIN_INTERFACE import get_option_data

# Three aligned pandas Series
bids, strikes, deltas = get_option_data('AAPL', '20250117')

# Or with stock price
bids, strikes, deltas, stock_price = get_option_data('AAPL', '20250117', return_stock_price=True)
```

- **bids** -- Call option bid prices (what you collect when selling)
- **strikes** -- Strike prices
- **deltas** -- Call option deltas (used as ITM probabilities in simulation)

### `create_positions(strikes, bought_contracts)`

Creates a position vector showing contract quantities at each strike:

```python
from YOUR_MAIN_INTERFACE import create_positions

# Dict form (recommended)
positions = create_positions(strikes, {220: 5, 225: 10, 230: 2})

# List with uniform quantity
positions = create_positions(strikes, [220, 225, 230], quantities=5)
```

### `create_itm_mask(strikes, expiration_price)`

Binary vector showing which strikes are in-the-money at a given expiration price:

```python
from YOUR_MAIN_INTERFACE import create_itm_mask

itm = create_itm_mask(strikes, 227.50)
itm_strikes = strikes[itm == 1]
```

### Vector Math Pipeline

The P&L calculation uses Hadamard (element-wise) multiplication across aligned vectors:

```
positions  [0, 0, 5, 10, 2, 0, ...]     # contracts at each strike
    x
itm_mask   [1, 1, 1,  0, 0, 0, ...]     # which strikes are ITM
    x
bids*100   [850, 420, 310, 95, 50, ...]  # premium per contract in dollars
    =
itm_pnl    [0, 0, 1550, 0, 0, 0, ...]   # premium from ITM positions
```

OTM positions are handled separately -- shares are sold at market price and combined with the collected premium for total P&L.

## Monte Carlo Simulation

The optimizer uses option deltas as ITM probabilities to simulate thousands of expiration scenarios:

1. For each simulation, a random draw determines which strikes finish ITM based on their delta
2. An expiration price is generated consistent with the ITM/OTM outcome
3. P&L is calculated for the candidate position using the vectorized pipeline
4. After all simulations, positions are ranked by expected P&L, win rate, and risk-adjusted return

The simulation accounts for the full covered call P&L including:
- Premium collected from selling calls
- Capital gains/losses on shares (called away at strike or sold at market)
- Net cost basis after premium offset

## Optimization Methods

The function automatically selects based on portfolio size:

| Capital / Contracts | Method | Description |
|-------------------|--------|-------------|
| < 5 contracts | Fast | Single-strike focus, quick evaluation |
| 5-20 contracts | Balanced | Tests multiple strike combinations |
| > 20 contracts | Thorough | Extensive multi-strike optimization |

Override with `optimization_method='fast'` or `optimization_method='thorough'`.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Broker API | Interactive Brokers (ib_insync) |
| Numerical | NumPy, SciPy (Monte Carlo simulation, vectorized math) |
| Data | Pandas (aligned Series for vector operations) |
| Visualization | Jupyter, Matplotlib |
| Configuration | python-dotenv |

## Getting Started

### Prerequisites

- Python 3.11+
- Interactive Brokers account with IB Gateway running
- OPRA market data subscription (required for options data)

### Installation

```bash
git clone https://github.com/linville-charlie/OptionMonger.git
cd OptionMonger
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and set your IB Gateway connection:

```
IB_HOST=127.0.0.1
IB_PORT=4002
IB_CLIENT_ID=1
ACCOUNT_ID=YOUR_ACCOUNT_ID
```

### IB Gateway Setup

1. Run IB Gateway on your host machine
2. Add your machine's IP to the trusted IPs list in IB Gateway settings
3. Ensure the API port matches your `.env` configuration
4. Subscribe to OPRA market data for options

See [docs/IB_GATEWAY_SETUP.md](docs/IB_GATEWAY_SETUP.md) for detailed instructions.

### Interactive Analysis

Use the Jupyter notebooks for live market analysis:

```bash
jupyter notebook notebooks/live_options_trading_optimized.ipynb
```

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Connection timeout | Restart IB Gateway, verify port in `.env` |
| Competing session error | Use a unique client ID or run `utilities/kill_all_connections.py` |
| No market data | Check OPRA subscription is active |
| Insufficient capital | Need at least `Stock Price x 100` for one contract |

## Documentation

- [API Reference](docs/API_REFERENCE.md) -- Complete function signatures and return types
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md) -- Data flow and component design
- [Covered Calls Guide](docs/COVERED_CALLS_GUIDE.md) -- Strategy guide with worked examples
- [User Guide](docs/USER_GUIDE.md) -- End-to-end workflow walkthrough

## License

MIT License
