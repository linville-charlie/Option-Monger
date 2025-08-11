# Claude Development Notes - Core Directory

## Purpose
Core functionality for options data fetching, position tracking, and IB Gateway communication.

## Key Files

### `simple_real_strikes.py`
**Main Function**: `get_all_strikes(ticker, expiration, use_live_data)`
- Fetches real strikes from IBKR or generates demo data
- Returns three aligned pandas Series: (bids, strikes, deltas)
- Handles both real IBKR strike increments and $0.50 demo increments
- Key insight: IBKR strikes vary by stock (AAPL uses $5, SPY uses $0.50-$5)

### `position_tracker.py`
**Key Functions**:
- `create_position_vector()` - Creates vector with quantities (0, 1, 2, ...)
- `create_itm_vector()` - Binary vector for ITM strikes
- `calculate_premium_paid_for_itm()` - Hadamard multiplication
- `calculate_net_pnl_vectors()` - Complete P&L calculation

**Important**: Position vectors now support quantities, not just binary!

### `ibkr_connection.py`
- Manages IB Gateway connection with retry logic
- Uses official `ibapi` package (not ib_insync)
- Handles threading for async message processing
- Connection: 172.21.112.1:4002 (WSL to Windows)

### `options_data.py`
- Fetches option chains and market data
- Gets available strikes for expiration dates
- Handles contract creation and data requests
- Implements caching to reduce API calls

### `models.py`
- Data models using dataclasses
- `OptionContract`, `OptionQuote`, `OptionGreeks`
- Type safety for option data structures

### `config.py`
- Configuration settings from .env
- Connection parameters
- Logging configuration

## Important Implementation Details

1. **Strike Detection**: 
   ```python
   # Automatically detects IBKR strike increments
   strikes = fetcher.get_option_strikes(ticker, expiration)
   ```

2. **Position Quantities**:
   ```python
   # Old: binary (0 or 1)
   # New: quantities (0, 1, 2, 3, ...)
   positions = create_position_vector(strikes, {220: 5, 225: 10})
   ```

3. **Hadamard Multiplication**:
   ```python
   # positions ⊙ itm ⊙ (bids × 100)
   premium = positions * itm * (bids * 100)
   ```

4. **Vector Alignment**:
   - All vectors share same index
   - `strikes[i]`, `bids[i]`, `deltas[i]`, `positions[i]` refer to same contract

## Connection Flow
1. Create IBKRConnection instance
2. Connect to IB Gateway at 172.21.112.1:4002
3. Fetch underlying price
4. Get available strikes
5. Fetch option data (or generate demo)
6. Return aligned vectors

## Error Handling
- Connection retry with timeout
- Fallback to demo data if no connection
- Closest strike matching if exact not found
- Market data warnings are normal (need subscriptions)

## Testing Without Market Data
Demo mode generates realistic data:
- Proper delta curves (0.01 to 0.99)
- Realistic bid prices with intrinsic + time value
- ITM/OTM spread behavior
- $0.50 strike increments as requested