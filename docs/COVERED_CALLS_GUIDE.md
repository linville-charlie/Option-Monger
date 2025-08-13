# Covered Calls Guide

## Overview
The `find_best_options()` function now supports covered call strategies where:
1. Your capital is used to buy shares (100 shares per contract)
2. You sell call options against those shares to collect premium
3. If calls expire ITM, shares are called away at the strike price
4. If calls expire OTM, you keep shares and can sell them

## Key Difference from Long Calls
- **Long Calls**: Capital buys option contracts (premium × 100)
- **Covered Calls**: Capital buys shares (stock price × 100), then you sell calls

## Usage

```python
from YOUR_MAIN_INTERFACE import find_best_options

# Find optimal covered call positions
results = find_best_options(
    ticker='AAPL',
    expiration='20250117',
    capital=100000,  # This buys shares, not options
    strategy='covered_calls',  # Specify covered calls
    use_live_data=False  # Use True for real IBKR data
)

# Results tell you:
print(f"Buy {results['shares_needed']} shares at ${results['current_stock_price']:.2f}")
print(f"Sell calls at: {results['optimal_positions']}")
print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
print(f"Premium collected: ${results['premium_collected']:,.2f}")
```

## Capital Requirements

For covered calls, you need enough capital to buy 100 shares per contract:
- Minimum capital = Current Stock Price × 100
- Example: AAPL at $223 needs at least $22,300 for 1 contract

## Return Metrics

The function returns:
- `shares_needed`: Number of shares to buy
- `capital_for_shares`: Cost to buy the shares
- `premium_collected`: Premium from selling calls
- `net_capital_after_premium`: Net cost after collecting premium
- `expected_pnl`: Expected profit/loss including all outcomes
- `return_on_capital`: Percentage return on share investment
- `optimal_positions`: Which strikes and quantities to sell

## Example Scenarios

### Small Account ($25,000)
```python
results = find_best_options('AAPL', '20250117', 25000, strategy='covered_calls')
# Can afford 1 contract (100 shares)
# Sells 1 OTM call to collect premium
```

### Medium Account ($100,000)
```python
results = find_best_options('SPY', '20250117', 100000, strategy='covered_calls')
# Can afford 2-4 contracts depending on stock price
# May spread across multiple strikes
```

### Large Account ($500,000)
```python
results = find_best_options('AAPL', '20250117', 500000, 
                           strategy='covered_calls',
                           optimization_method='thorough')
# Can afford 20+ contracts
# Optimizes across multiple strikes for best risk/reward
```

## Optimization Methods

The function automatically chooses based on capital:
- **< 5 contracts worth**: Fast method (single strike focus)
- **5-20 contracts**: Balanced (tests multiple combinations)
- **> 20 contracts**: Thorough (extensive optimization)

Or specify manually:
- `optimization_method='fast'`: Quick results
- `optimization_method='thorough'`: Best results

## Strategy Comparison

```python
# Compare covered calls vs long calls
capital = 100000

# Covered calls
cc_results = find_best_options('AAPL', '20250117', capital, 
                              strategy='covered_calls')

# Long calls  
lc_results = find_best_options('AAPL', '20250117', capital,
                              strategy='long_calls')

print(f"Covered Calls Expected P&L: ${cc_results['expected_pnl']:,.2f}")
print(f"Long Calls Expected P&L: ${lc_results['expected_pnl']:,.2f}")
```

## Important Notes

1. **Share Ownership Required**: You must own shares before selling covered calls
2. **Limited Upside**: Profit is capped at strike price + premium
3. **Downside Protection**: Premium provides small buffer against stock decline
4. **Assignment Risk**: Shares may be called away if ITM at expiration

## P&L Calculation

For covered calls, the P&L includes:
1. Premium collected from selling calls
2. Gain/loss from shares if called away (ITM)
3. Value of shares if kept (OTM)
4. Minus initial share cost basis

Formula:
- ITM: Premium + (Strike - Purchase Price) × 100 × Contracts
- OTM: Premium + (Current Price - Purchase Price) × 100 × Contracts