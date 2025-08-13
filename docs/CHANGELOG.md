# Changelog

## [2.1.0] - 2025-08-13
### Fixed
- **Stock price threshold** - Now accepts all stocks > $0 (previously required > $50)
  - Fixes issue where lower-priced stocks like SONY ($27.92) were rejected
- **Notebook imports** - Fixed import errors in Jupyter notebooks
  - Added proper path handling to find YOUR_MAIN_INTERFACE.py
- **Notebook launcher** - Fixed path in start_notebook.bat to find notebooks/ directory
- **Calculation bugs** - Fixed win rate showing 8196% and return showing 136%
  - Corrected operator precedence in return_on_capital calculation

### Security
- **Removed ALL demo/test data capabilities** - Per user request for safety
  - Deleted `_generate_demo_strikes()` function
  - Removed all fallback to simulated data
  - System now ONLY uses real IBKR market data

### Changed
- **Project structure** - Reorganized for clarity:
  - Core functionality → `core/`
  - Notebooks → `notebooks/`
  - Utilities → `utilities/`
  - Scripts → `scripts/`
  - Old files → `old_files/` (can be deleted)
- **Client ID** - Changed default from 0 to 1 to avoid competing sessions
- **Error handling** - Improved connection error messages and debugging

### Added
- **Jupyter notebooks** - Created optimized notebook that fetches data only once
- **Utility scripts** - Added tools for connection management:
  - `check_sessions.py` - Check for competing sessions
  - `kill_all_connections.py` - Clear stuck connections
  - `use_next_client_id.py` - Auto-rotate client IDs
- **Setup scripts** - Added Jupyter setup and notebook launchers
- **Documentation** - Enhanced CLAUDE.md and PROJECT_STRUCTURE.md

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
- Demo mode with $0.50 strike increments