# Claude Development Notes - Root Directory

## Project Overview
OptionMonger is a **covered call optimization system** for Interactive Brokers that finds the optimal strikes to sell calls against owned shares.

## CRITICAL: This is ONLY for Covered Calls
- **NO long calls** - all buying logic has been removed
- **Capital buys shares** - not option premiums
- **We sell calls** - collecting premium against owned shares
- **Always exit at expiration** - sell all shares whether ITM or OTM

## Main Entry Point
`find_best_options()` in YOUR_MAIN_INTERFACE.py - The ONE function you need:
```python
results = find_best_options('AAPL', '20250117', 100000)
# Returns:
# - shares_needed: How many shares to buy
# - optimal_positions: Which call strikes to sell
# - expected_pnl: Expected profit/loss
# - premium_collected: Premium from selling calls
```

## Money Flow (Critical Understanding)
### Going In:
1. Buy shares with capital (e.g., $89,200 for 400 shares)
2. Sell calls, collect premium (e.g., $204)
3. Net cost: $88,996

### Coming Out (At Expiration):
1. **ITM strikes**: Shares called away at strike price
2. **OTM strikes**: We sell shares at market price
3. **Mixed outcomes handled**: Each contract evaluated independently

### P&L Formula:
`Total P&L = Premium Collected + (Exit Price - Entry Price) × Shares`

## Connection Configuration
- IB Gateway runs on Windows host
- WSL connects to: 172.21.112.1:4002
- Must add WSL IP to IB Gateway trusted IPs
- Paper trading account: DUE723251

## Key Implementation Details
1. **Real Stock Price**: Fetches actual current price from IBKR for accurate share calculations
2. **Accurate Share Costs**: `Shares = floor(Capital / Stock Price)`
3. **Mixed ITM/OTM**: Each position evaluated independently at expiration
4. **Vectorized Math**: All positions calculated simultaneously
5. **100 Share Multiplier**: All contracts represent 100 shares

## Testing Commands
```bash
# Test covered call optimization
python test_covered_calls_only.py

# Test production readiness
python test_production_ready.py

# Test with real IBKR data
python YOUR_MAIN_INTERFACE.py  # with use_live_data=True
```

## Common Issues and Solutions
1. **Connection timeout**: Restart IB Gateway, check trusted IPs
2. **Insufficient capital**: Need at least Stock Price × 100 for one contract
3. **No market data**: Normal - requires subscriptions (demo mode works without)
4. **Import errors**: Check core/ directory is in path

## File Organization
- Core functionality → `core/`
- Examples → `examples/`
- Tests → `tests/`
- Old versions → `old_files/` (can be deleted)