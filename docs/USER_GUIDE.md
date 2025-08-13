# OptionMonger User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Interactive Analysis](#interactive-analysis)
4. [Understanding Results](#understanding-results)
5. [Trading Workflow](#trading-workflow)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Getting Started

### Prerequisites
- Interactive Brokers account with options trading enabled
- IB Gateway installed and configured
- OPRA market data subscription
- Python 3.8+ environment
- At least 100 × Stock Price in capital

### Initial Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-username/OptionMonger.git
cd OptionMonger
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure IB Gateway**
- Start IB Gateway on port 8000
- Enable API connections
- Add your IP to trusted list

4. **Set environment variables**
Create `.env` file:
```
TWS_HOST=172.21.112.1  # Your IB Gateway IP
TWS_PORT=8000
TWS_CLIENT_ID=1
ACCOUNT_ID=YOUR_ACCOUNT
```

## Basic Usage

### Quick Start - Find Best Options

```python
from YOUR_MAIN_INTERFACE import find_best_options

# Find optimal covered calls for AAPL with $100,000
results = find_best_options('AAPL', '20250117', 100000)

# Display results
print(f"Buy {results['shares_needed']} shares")
print(f"Sell calls at: {results['optimal_positions']}")
print(f"Expected profit: ${results['expected_pnl']:,.2f}")
print(f"Win rate: {results['win_rate']:.1f}%")
```

### Understanding Parameters

- **ticker**: Stock symbol (e.g., 'AAPL', 'MSFT', 'SPY')
- **expiration**: Option expiration in YYYYMMDD format
- **capital**: Total capital to invest in buying shares

## Interactive Analysis

### Using Jupyter Notebooks

1. **Start the notebook**
```bash
# Windows
scripts\start_notebook.bat

# Linux/Mac
jupyter notebook notebooks/live_options_trading_optimized.ipynb
```

2. **Configure parameters**
```python
TICKER = 'AAPL'           # Stock to trade
EXPIRATION = '20250815'   # Option expiration
CAPITAL = 100000          # Investment amount
```

3. **Run analysis**
- Execute cells sequentially
- Data is fetched once and reused
- View interactive charts and metrics

### Notebook Features

#### Live Data Fetching
```python
# Fetches current market data
bids, strikes, deltas, stock_price = get_option_data(
    TICKER, EXPIRATION, return_stock_price=True
)
```

#### Optimization
```python
# Finds optimal strikes to sell
results = optimize_covered_calls(
    strikes, deltas, bids, CAPITAL, stock_price
)
```

#### Visualization
- P&L curves at different stock prices
- Risk/return profiles
- Strike distribution charts

## Understanding Results

### Key Metrics Explained

#### Financial Metrics
- **shares_needed**: Number of shares to purchase
- **capital_for_shares**: Total cost of shares
- **premium_collected**: Income from selling calls
- **net_capital_after_premium**: Actual cash outlay

#### Performance Metrics
- **expected_pnl**: Average expected profit/loss
- **win_rate**: Percentage of profitable scenarios
- **return_on_capital**: Return as percentage of investment
- **var_95**: Value at Risk (5th percentile loss)

#### Position Details
- **optimal_positions**: Dictionary of {strike: quantity}
- **contracts_sold**: Total number of call contracts

### Example Output Interpretation

```
Results for AAPL:
  Buy 400 shares at $223.00
  Sell 4 calls at $265.00 strike
  Premium collected: $204.00
  Expected P&L: $1,652.00
  Win Rate: 88.2%
  Return: 1.85%
```

**Interpretation**:
- You buy 400 AAPL shares for $89,200
- Sell 4 call contracts at $265 strike
- Collect $204 premium immediately
- 88.2% chance of profit at expiration
- Expected return of 1.85% on capital

## Trading Workflow

### Step 1: Analysis
```python
# Analyze multiple expiration dates
expirations = ['20250117', '20250221', '20250321']
for exp in expirations:
    results = find_best_options('AAPL', exp, 100000)
    print(f"{exp}: Return {results['return_on_capital']:.2f}%")
```

### Step 2: Position Entry

1. **Buy shares first**
   - Market or limit order
   - Quantity: `results['shares_needed']`
   - Wait for fill confirmation

2. **Sell call options**
   - Action: SELL TO OPEN
   - Strike: From `results['optimal_positions']`
   - Quantity: Number of contracts
   - Limit price: At or above bid

### Step 3: Position Management

#### If Stock Price Rises (ITM)
- Shares will be called away at strike
- You keep the premium
- Profit = Premium + (Strike - Purchase Price) × Shares

#### If Stock Price Falls (OTM)
- Calls expire worthless
- You keep shares and premium
- Can sell new calls next cycle

### Step 4: Exit at Expiration

**Automatic exit (ITM)**:
- Shares called away automatically
- No action needed

**Manual exit (OTM)**:
- Sell shares at market price
- Or keep shares for next cycle

## Troubleshooting

### Common Issues and Solutions

#### Connection Error
```
Error: Failed to connect to IB Gateway
```
**Solution**:
- Verify IB Gateway is running on port 8000
- Check firewall settings
- Confirm IP in .env file

#### Competing Session Error
```
Error 10197: No market data during competing live session
```
**Solution**:
```bash
# Kill existing connections
python utilities/kill_all_connections.py

# Or change client ID
python utilities/use_next_client_id.py
```

#### No Market Data
```
Warning: Only 0 strikes have market data
```
**Solution**:
- Verify OPRA subscription is active
- Check market hours (9:30 AM - 4:00 PM ET)
- Ensure ticker and expiration are valid

#### Insufficient Capital
```
Error: Need at least $22,300 for one contract
```
**Solution**:
- Increase capital amount
- Choose lower-priced stock
- Wait for stock price to decrease

### Debug Tools

```bash
# Test connection
python test.py

# Debug stock price fetching
python utilities/debug_stock_price.py

# Check active sessions
python utilities/check_sessions.py

# Verify market data
python test_market_data_verification.py
```

## Best Practices

### Position Sizing
1. **Never use margin** for covered calls
2. **Reserve cash** for potential adjustments
3. **Diversify** across multiple stocks
4. **Limit exposure** to 20-30% per position

### Strike Selection
1. **OTM strikes** (5-10% above current price)
   - Lower assignment probability
   - Keep upside potential
   
2. **High delta strikes** (0.3-0.4)
   - Better premium
   - Acceptable risk

3. **Liquid strikes**
   - Minimum $0.50 bid
   - Tight bid-ask spread

### Timing Considerations

#### Best Times to Sell Calls
- After stock purchase on down days
- When IV is elevated
- 30-45 days to expiration
- After earnings (if holding through)

#### Avoid Selling Calls
- Before dividend ex-date
- During strong uptrend
- With upcoming catalysts
- When IV is very low

### Risk Management

1. **Set profit targets**
```python
# Example: Close if 50% profit achieved
if current_value >= entry_value * 1.5:
    close_position()
```

2. **Monitor assignments**
- Track ITM probability
- Be prepared for early assignment
- Have exit plan ready

3. **Portfolio allocation**
- Maximum 5-10 positions
- Vary expiration dates
- Different sectors/correlations

### Record Keeping

Track each trade:
```python
trade_log = {
    'date': '2025-08-13',
    'ticker': 'AAPL',
    'shares': 400,
    'strike': 265,
    'premium': 204,
    'expiration': '20250117',
    'result': 'pending'
}
```

## Advanced Strategies

### Rolling Covered Calls
```python
# If stock rises above strike before expiration
if days_to_expiry > 7 and stock_price > strike * 0.95:
    # Buy back current call
    # Sell new call at higher strike/later date
    roll_position(ticker, current_strike, new_strike, new_expiry)
```

### Multiple Strikes
```python
# Ladder strikes for different outcomes
results = find_best_options('SPY', '20250117', 200000)
# May recommend multiple strikes like:
# {450: 2, 455: 2, 460: 1}  # Different strikes
```

### Defensive Strategies
```python
# Use more conservative strikes in volatile markets
if market_volatility > threshold:
    # Sell further OTM calls
    conservative_capital = capital * 0.7
    results = find_best_options(ticker, expiry, conservative_capital)
```

## Quick Reference

### Essential Commands
```bash
# Run optimization
python YOUR_MAIN_INTERFACE.py

# Start notebook
scripts\start_notebook.bat

# Test connection
python quick_test.py

# Debug issues
python utilities/debug_stock_price.py
```

### Key Functions
```python
# Main optimization
find_best_options(ticker, expiration, capital)

# Get option data
get_all_strikes(ticker, expiration)

# Calculate P&L
calculate_covered_call_pnl(positions, strikes, bids, entry, exit)
```

### Important Files
- `YOUR_MAIN_INTERFACE.py` - Main API
- `notebooks/live_options_trading_optimized.ipynb` - Interactive analysis
- `.env` - Configuration
- `CLAUDE.md` - Development notes

## Support

For issues or questions:
1. Check troubleshooting section
2. Review error messages carefully
3. Verify market hours and data subscriptions
4. Test with known-good symbols (AAPL, SPY)

Remember: This system is for covered calls only. You must own shares before selling calls against them.