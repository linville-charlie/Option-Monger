# Claude Development Notes - Examples Directory

## Purpose
Example implementations showing how to use the options trading interface in real strategies.

## Key Files

### `your_strategy.py`
**Purpose**: Complete example of using all main functions
- Shows how to get option vectors
- Demonstrates position creation with quantities
- Calculates P&L at different expiration scenarios
- Includes spread calculations
- Has `--demo` flag for testing without IB Gateway

**Key Examples**:
```python
# Get vectors
bids, strikes, deltas = get_all_strikes('AAPL', '20250117')

# Create positions with quantities
positions = create_position_vector(strikes, {
    220.0: 10,  # Buy 10 contracts at 220
    225.0: 5,   # Buy 5 contracts at 225
})

# Calculate P&L
results = calculate_expiration_value(strikes, bids, positions, 227.50)
```

### `trading_example.py`
**Purpose**: Demonstrates real trading workflow
- Position entry based on delta targets
- Spread construction (vertical, iron condor)
- Risk management calculations
- Portfolio Greeks aggregation

**Key Patterns**:
- Finding strikes by delta
- Building multi-leg positions
- Calculating max profit/loss
- Position sizing

### `analyze_strikes.py`
**Purpose**: Analyzes strike increments from IBKR
- Fetches real strikes for different tickers
- Identifies strike increment zones
- Shows how increments vary by stock price

**Key Findings**:
- AAPL: $5.00 increments, $2.50 near ATM
- SPY: $0.50, $1.00, $5.00 in different zones
- Increments change based on moneyness

## Usage Examples

### Basic Strategy
```python
# 1. Get data
bids, strikes, deltas = get_all_strikes('AAPL', '20250117')

# 2. Find ATM
atm_idx = np.abs(deltas - 0.5).argmin()

# 3. Buy spread
positions = create_position_vector(strikes, {
    strikes.iloc[atm_idx]: 1,      # Buy ATM
    strikes.iloc[atm_idx + 5]: -1   # Sell 5 strikes higher
})
```

### Iron Condor
```python
# Find strikes by delta
d20_call = find_strike_by_delta(deltas, strikes, 0.20)
d20_put = find_strike_by_delta(deltas, strikes, -0.20)

# Create position
positions = create_position_vector(strikes, {
    d20_put - 5: 1,   # Buy put
    d20_put: -1,      # Sell put
    d20_call: -1,     # Sell call
    d20_call + 5: 1   # Buy call
})
```

### Multiple Expirations
```python
expirations = ['20250117', '20250221', '20250321']
all_data = {}

for exp in expirations:
    bids, strikes, deltas = get_all_strikes('AAPL', exp)
    all_data[exp] = {'bids': bids, 'strikes': strikes, 'deltas': deltas}
```

## Testing Tips

1. **Without IB Gateway**:
   ```bash
   python your_strategy.py --demo
   ```

2. **With Real Data**:
   ```bash
   python your_strategy.py  # Connects to IB Gateway
   ```

3. **Analyze Strikes**:
   ```bash
   python analyze_strikes.py AAPL 20250117
   ```

## Common Patterns

### Filter Liquid Options
```python
liquid = bids > 0.10  # Only options with bids > $0.10
liquid_strikes = strikes[liquid]
liquid_bids = bids[liquid]
liquid_deltas = deltas[liquid]
```

### Calculate Spread P&L
```python
# At expiration
intrinsic = np.maximum(hit_price - strikes, 0)
pnl = positions * (intrinsic - bids)
total_pnl = pnl.sum() * 100  # × 100 shares
```

### Position Sizing
```python
capital = 10000
max_contracts = capital // (bids.iloc[atm_idx] * 100)
positions = create_position_vector(strikes, {atm_strike: max_contracts})
```