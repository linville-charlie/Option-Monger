# OptionMonger - Covered Call Optimization for IBKR

A covered call optimization system for Interactive Brokers that finds the optimal strikes to sell calls against your owned shares.

## 🎯 What It Does

**COVERED CALLS ONLY** - This system helps you:
1. Determine how many shares to buy with your capital
2. Find the optimal call strikes to sell
3. Calculate expected P&L including premium collection
4. Handle mixed ITM/OTM outcomes at expiration

## 🚀 Quick Start

```python
from YOUR_MAIN_INTERFACE import find_best_options

# Find optimal covered calls for AAPL with $100,000
results = find_best_options('AAPL', '20250117', 100000)

print(results['recommendation'])
print(f"Buy {results['shares_needed']} shares")
print(f"Sell calls at: {results['optimal_positions']}")
print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
```

## 💰 How Covered Calls Work

### Money In:
1. **Buy shares**: Your capital purchases shares (100 per contract)
2. **Sell calls**: Collect premium immediately

### Money Out (At Expiration):
- **ITM strikes**: Shares called away at strike price
- **OTM strikes**: You sell shares at market price
- **Mixed outcomes**: Each contract handled independently

### P&L Formula:
```
Total P&L = Premium Collected + (Exit Price - Entry Price) × Shares
```

## 📁 Project Structure

```
OptionMonger/
│
├── YOUR_MAIN_INTERFACE.py      # ⭐ Main entry point - find_best_options()
│
├── core/                        # Core functionality
│   ├── covered_call_optimization.py  # Optimization logic
│   ├── simple_real_strikes.py        # Gets option data & stock price
│   ├── position_tracker.py           # P&L calculations
│   ├── ibkr_connection.py            # IB Gateway connection
│   └── ...
│
├── tests/                       # Test files
│   ├── test_covered_calls_only.py
│   ├── test_production_ready.py
│   └── ...
│
└── COVERED_CALLS_GUIDE.md      # Detailed covered call documentation
```

## 🔧 Installation

```bash
# Clone the repository
git clone <your-repo>

# Install requirements
pip install -r requirements.txt

# Configure IB Gateway connection
# Edit core/config.py with your settings
```

## 🔌 IB Gateway Setup

1. Run IB Gateway on Windows host
2. Add WSL IP to trusted IPs in IB Gateway
3. Connection details:
   - Host: 172.21.112.1
   - Port: 4002
   - Client ID: 1

## 📊 Example Results

```python
results = find_best_options('AAPL', '20250117', 100000)

# Output:
# Buy 400 shares at $223.00
# Sell 4 calls at $265.00 strike
# Premium collected: $204.00
# Expected P&L: $14,652.00
# Win Rate: 88.2%
```

## ⚠️ Important Notes

- **Covered Calls Only**: No long call buying functionality
- **Capital Requirements**: Need at least Stock Price × 100
- **Exit Strategy**: Always sell shares at expiration
- **Risk**: Upside capped at strike price

## 🧪 Testing

```bash
# Test covered call optimization
python test_covered_calls_only.py

# Test production readiness
python test_production_ready.py

# Test with demo data
python YOUR_MAIN_INTERFACE.py
```

## 📝 Key Functions

### Main Function:
- `find_best_options(ticker, expiration, capital)` - Complete covered call optimization

### Helper Functions:
- `get_option_data()` - Get bids, strikes, deltas vectors
- `create_positions()` - Create position vector with quantities
- `calculate_covered_call_pnl()` - Calculate P&L for covered calls

## 🤝 Contributing

This is a focused covered call system. Please maintain this focus in any contributions.

## 📄 License

[Your License Here]