# OptionMonger System Architecture

## Overview
OptionMonger is a sophisticated covered call optimization system designed to maximize returns from selling call options against owned shares. The system connects to Interactive Brokers (IB Gateway) to fetch real-time market data and uses advanced algorithms to find optimal strike prices.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                        │
├─────────────────────────────────────────────────────────────┤
│  • YOUR_MAIN_INTERFACE.py (Main API)                         │
│  • Jupyter Notebooks (Interactive Analysis)                  │
│  • Test Scripts (Verification)                               │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│                    Core Business Logic                      │
├─────────────────────────────────────────────────────────────┤
│  • covered_call_optimization.py (Optimization Algorithms)   │
│  • position_tracker.py (P&L Calculations)                  │
│  • simulation.py (Monte Carlo Simulations)                 │
│  • simple_real_strikes.py (Strike Management)              │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│                    Data Access Layer                        │
├─────────────────────────────────────────────────────────────┤
│  • options_data.py (Option Chain Fetching)                 │
│  • ibkr_connection.py (IB Gateway Connection)              │
│  • models.py (Data Models)                                 │
│  • config.py (Configuration Management)                     │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│              Interactive Brokers Gateway                    │
├─────────────────────────────────────────────────────────────┤
│  • Port: 8000                                              │
│  • Client ID: 1                                            │
│  • Protocol: TCP/IP                                        │
│  • API: Official ibapi                                     │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

#### YOUR_MAIN_INTERFACE.py
- **Purpose**: Primary API endpoint for all functionality
- **Key Function**: `find_best_options(ticker, expiration, capital)`
- **Returns**: Optimal positions, expected P&L, risk metrics

#### Jupyter Notebooks
- **Location**: `notebooks/`
- **Purpose**: Interactive analysis and visualization
- **Features**: 
  - Live data fetching (optimized for single fetch)
  - P&L visualization
  - Risk analysis charts
  - Trade execution checklists

### 2. Core Business Logic

#### covered_call_optimization.py
- **Purpose**: Implements optimization algorithms
- **Key Functions**:
  - `optimize_covered_calls()` - Random search optimization
  - `optimize_covered_calls_continuous()` - Enhanced optimization
- **Algorithm**: Monte Carlo simulation with delta-based probabilities

#### position_tracker.py
- **Purpose**: Tracks positions and calculates P&L
- **Key Functions**:
  - `create_position_vector()` - Creates position quantities
  - `calculate_covered_call_pnl()` - Computes profit/loss
- **Math**: Vectorized operations using pandas/numpy

#### simulation.py
- **Purpose**: Monte Carlo simulations for risk analysis
- **Features**:
  - Delta-based probability modeling
  - Multiple expiration scenarios
  - VaR and win rate calculations

### 3. Data Access Layer

#### options_data.py
- **Purpose**: Fetches option market data
- **Key Functions**:
  - `get_option_strikes()` - Available strikes for expiration
  - `get_option_data()` - Full option details (bid, ask, Greeks)
  - `get_underlying_price()` - Current stock price
- **Caching**: Reduces redundant API calls

#### ibkr_connection.py
- **Purpose**: Manages IB Gateway connection
- **Features**:
  - Async message handling with threading
  - Retry logic with timeout
  - Clean disconnect handling
- **Connection**: WSL → Windows (172.21.112.1:8000)

## Data Flow

### 1. Option Data Retrieval
```
User Request → find_best_options() → get_all_strikes() → 
→ IBKRConnection.connect() → OptionsDataFetcher.get_option_strikes() →
→ IB Gateway → Market Data → Parse & Return
```

### 2. Optimization Process
```
Option Data → optimize_covered_calls() → 
→ Generate Portfolio Candidates → Monte Carlo Simulation →
→ Calculate P&L for Each Scenario → Select Best Portfolio →
→ Return Optimal Positions
```

### 3. P&L Calculation
```
Positions + Market Data → calculate_covered_call_pnl() →
→ Premium Collection + Stock P&L → ITM/OTM Evaluation →
→ Net P&L Calculation → Risk Metrics
```

## Key Design Patterns

### 1. Vector Operations
All calculations use aligned pandas Series for efficiency:
```python
# All vectors share same index
strikes[i], bids[i], deltas[i], positions[i]  # Same contract
```

### 2. Hadamard Multiplication
Element-wise multiplication for calculations:
```python
premium = positions ⊙ bids ⊙ 100  # Per contract
```

### 3. Binary ITM Detection
```python
itm = (expiration_price > strikes).astype(int)
```

## Configuration

### Environment Variables (.env)
```
TWS_HOST=172.21.112.1
TWS_PORT=8000
TWS_CLIENT_ID=1
ACCOUNT_ID=DUE723251
```

### Key Parameters
- **Contract Multiplier**: 100 shares per option contract
- **Strike Filtering**: 80%-120% of current stock price
- **Liquid Strikes**: Minimum $0.50 premium
- **Max Contracts**: User-defined or capital-limited

## Security Considerations

1. **No Demo Data**: All test/demo data generation removed
2. **Real Data Only**: System requires live IBKR connection
3. **Client ID Management**: Avoids competing sessions
4. **No Sensitive Logging**: Greeks and prices logged safely

## Performance Optimizations

1. **Single Data Fetch**: Notebooks fetch data once and reuse
2. **Vectorized Math**: NumPy/Pandas for fast calculations
3. **Cached Connections**: Reuse IB Gateway connection
4. **Rate Limiting**: 0.1s delay between API calls

## Error Handling

### Connection Errors
- Retry with timeout
- Clear error messages
- Connection diagnostic tools

### Market Data Errors
- Check OPRA subscription
- Verify market hours
- Fallback to estimated prices

### Calculation Errors
- Input validation
- Capital sufficiency checks
- Position limit enforcement

## Testing Strategy

### Unit Tests (`tests/`)
- Position vector calculations
- P&L computation
- ITM/OTM detection
- Hadamard operations

### Integration Tests
- Live market data fetching
- End-to-end optimization
- Connection management

### Manual Testing
- `test_live_options.py` - Full system test
- `quick_test.py` - Connection verification
- Jupyter notebooks - Interactive testing

## Deployment Considerations

### Prerequisites
1. IB Gateway running on Windows
2. OPRA subscription for options data
3. Python 3.8+ with requirements.txt
4. WSL2 (if running from Linux subsystem)

### Network Requirements
- Port 8000 open between WSL and Windows
- Stable connection to IB servers
- Low latency for real-time data

### Monitoring
- Connection status checks
- Market data validation
- P&L tracking
- Error logging

## Future Enhancements

### Planned Features
1. Multi-expiration optimization
2. Rolling covered calls
3. Risk parity allocation
4. Greeks-based adjustments

### Performance Improvements
1. Parallel portfolio evaluation
2. GPU acceleration for Monte Carlo
3. Real-time position updates
4. WebSocket streaming data

### Risk Management
1. Dynamic position sizing
2. Correlation analysis
3. Stress testing scenarios
4. Portfolio hedging options