# OptionMonger

A covered call optimization system for Interactive Brokers that uses Monte Carlo simulation to find optimal strike prices, maximizing premium income while managing assignment risk.

## Overview

OptionMonger connects to IB Gateway, fetches live options chain data, and runs thousands of Monte Carlo scenarios to identify the best covered call positions for a given portfolio and capital allocation. It evaluates every available strike across multiple expiration dates, calculating expected P&L, win rates, and risk metrics to produce actionable trade recommendations.

## Features

- **Live Market Data Integration** -- Real-time options chains and stock prices from Interactive Brokers via IB Gateway
- **Monte Carlo Optimization** -- Simulates thousands of price paths to evaluate expected outcomes for each strike
- **Vectorized P&L Engine** -- All positions calculated simultaneously using NumPy for fast batch evaluation
- **Risk Metrics** -- Value at Risk (VaR), win rate, expected P&L, and return on capital for every candidate position
- **Position Tracking** -- Monitor open positions with real-time P&L updates
- **Interactive Notebooks** -- Jupyter notebooks for live trading analysis and visualization

## Architecture

```
OptionMonger/
├── YOUR_MAIN_INTERFACE.py         # Main entry point: find_best_options()
├── core/
│   ├── covered_call_optimization.py   # Optimization engine
│   ├── simple_real_strikes.py         # Options data + stock price retrieval
│   ├── position_tracker.py            # P&L tracking
│   └── ibkr_connection.py             # IB Gateway connection management
├── tests/                         # Unit and integration tests
├── notebooks/                     # Jupyter notebooks for live analysis
├── utilities/                     # Connection debugging tools
└── docs/                          # Documentation
```

## How It Works

### Covered Call Mechanics

1. **Buy shares** with available capital (100 shares per contract)
2. **Sell call options** against those shares, collecting premium upfront
3. **At expiration**: ITM strikes result in shares called away at the strike price; OTM strikes let you sell shares at market price

### P&L Formula

```
Total P&L = Premium Collected + (Exit Price - Entry Price) x Shares
```

The optimizer evaluates every available strike at this formula across Monte Carlo price paths, then ranks positions by risk-adjusted return.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Broker API | Interactive Brokers (ib_insync) |
| Numerical | NumPy, SciPy (Monte Carlo, vectorized math) |
| Data | Pandas |
| Visualization | Jupyter, Matplotlib |

## Getting Started

### Prerequisites

- Python 3.11+
- Interactive Brokers account with IB Gateway running
- OPRA market data subscription (for options data)

### Installation

```bash
git clone https://github.com/linville-charlie/OptionMonger.git
cd OptionMonger
pip install -r requirements.txt
```

### Configuration

Set IB Gateway connection details in your `.env` file (see `.env.example`):

```
IB_HOST=127.0.0.1
IB_PORT=4002
IB_CLIENT_ID=1
```

### Usage

```python
from YOUR_MAIN_INTERFACE import find_best_options

results = find_best_options('AAPL', '20250815', 100000)

print(f"Buy {results['shares_needed']} shares")
print(f"Sell calls at: {results['optimal_positions']}")
print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
print(f"Win Rate: {results['win_rate']:.1%}")
```

## License

MIT License
