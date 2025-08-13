# Changelog

## [2.0.0] - 2025-08-08
### BREAKING CHANGES
- **Removed all long call functionality** - System now ONLY does covered calls
- Removed `strategy` parameter from `find_best_options()` - always covered calls now
- Capital now buys shares, not option premiums

### Added
- Real stock price fetching from IBKR for accurate share calculations
- Covered call optimization with `find_best_options()`
- `core/covered_call_optimization.py` - Dedicated covered call optimization
- Proper handling of mixed ITM/OTM outcomes at expiration
- Return stock price as 4th element in `get_all_strikes()` when requested
- Production readiness tests

### Changed
- `find_best_options()` now exclusively for covered calls
- Capital calculations based on buying shares (Stock Price × 100)
- Optimization methods adapted for covered call positions
- Updated all documentation to reflect covered call focus

### Fixed
- Accurate stock price for share purchase calculations
- Proper P&L calculation for mixed ITM/OTM positions
- Math verification for share costs

### Removed
- All long call buying logic
- `optimize_portfolio()` and related functions for buying calls
- `strategy` parameter - no longer needed
- Unnecessary optimization imports

## [1.5.0] - 2025-08-07
### Added
- Simplified one-step optimization with `find_best_options()`
- Continuous position optimization using scipy
- Monte Carlo simulation with delta-based probabilities
- Target P&L optimization

### Changed
- Switched from `ib_insync` to official `ibapi` for stability
- Position vectors now support quantities (0, 1, 2, ...) not just binary

## [1.0.0] - 2025-08-06
### Initial Release
- Three vector interface (bids, strikes, deltas)
- Position tracking with quantities
- ITM detection vectors
- Hadamard multiplication for calculations
- IBKR connection via IB Gateway
- Demo mode with /usr/bin/zsh.50 strike increments
