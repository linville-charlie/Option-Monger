# Project Structure

```
OptionMonger/
│
├── 📁 core/                          # Core functionality
│   ├── __init__.py
│   ├── config.py                     # Configuration management
│   ├── ibkr_connection.py           # IB Gateway connection
│   ├── options_data.py              # Options data fetching
│   ├── covered_call_optimization.py # Optimization algorithms
│   ├── position_tracker.py          # Position management
│   ├── simulation.py                # Monte Carlo simulations
│   ├── models.py                    # Data models
│   └── simple_real_strikes.py       # Strike price handling
│
├── 📁 notebooks/                     # Jupyter notebooks
│   ├── live_options_trading.ipynb           # Standard trading notebook
│   └── live_options_trading_optimized.ipynb # Optimized (single fetch)
│
├── 📁 utilities/                     # Helper utilities
│   ├── check_sessions.py            # Check IB Gateway sessions
│   ├── debug_stock_price.py         # Debug market data issues
│   ├── kill_all_connections.py      # Clear stuck connections
│   └── use_next_client_id.py        # Auto-rotate client IDs
│
├── 📁 scripts/                       # Setup and utility scripts
│   ├── setup_jupyter.bat            # Windows Jupyter setup
│   ├── setup_jupyter.sh             # Linux/Mac Jupyter setup
│   ├── start_notebook.bat           # Quick notebook launcher
│   ├── fix_competing_session.bat    # Fix connection conflicts
│   ├── setup.sh                     # Initial setup script
│   └── run.sh                       # Run script
│
├── 📁 tests/                         # Unit tests
│   ├── test_simulation.py           # Test Monte Carlo
│   ├── test_position_vector.py      # Test position vectors
│   ├── test_covered_call_otm.py     # Test OTM scenarios
│   └── ...                          # Other unit tests
│
├── 📁 examples/                      # Example implementations
│   ├── your_strategy.py             # Example strategy
│   ├── trading_example.py           # Trading examples
│   └── analyze_strikes.py           # Strike analysis
│
├── 📁 docs/                          # Documentation
│   ├── INSTALLATION.md              # Installation guide
│   ├── IB_GATEWAY_SETUP.md         # IB Gateway configuration
│   ├── COVERED_CALLS_GUIDE.md      # Covered calls explanation
│   ├── CONNECTION_FIX.md           # Connection troubleshooting
│   └── ...                          # Other documentation
│
├── 📁 old_files/                     # Archive (can be deleted)
│   └── ...                          # Old versions
│
├── 📄 Core Files
│   ├── YOUR_MAIN_INTERFACE.py      # Main API interface
│   ├── test_live_options.py        # Main test script
│   ├── quick_test.py               # Quick verification
│   ├── test_ibkr_options.py        # Test IBKR connection
│   ├── test_market_data_verification.py  # Verify market data
│   └── test.py                     # Simple connection test
│
├── 📄 Configuration
│   ├── .env                         # Environment variables
│   ├── requirements.txt            # Python dependencies
│   ├── .gitignore                  # Git ignore rules
│   └── LICENSE                     # MIT License
│
└── 📄 Documentation
    ├── README.md                    # Main documentation
    ├── CLAUDE.md                    # Development notes
    └── PROJECT_STRUCTURE.md        # This file
```

## Key Components

### Core (`/core`)
The heart of the system - handles all IBKR connections, data fetching, and optimization logic.

### Notebooks (`/notebooks`)
Interactive Jupyter notebooks for live trading analysis. The optimized version fetches data only once for better performance.

### Utilities (`/utilities`)
Helper scripts for debugging connection issues, managing sessions, and troubleshooting.

### Scripts (`/scripts`)
Setup and configuration scripts for various platforms.

### Tests (`/tests`)
Comprehensive unit tests for core functionality.

### Examples (`/examples`)
Sample implementations and strategies.

## Main Entry Points

1. **YOUR_MAIN_INTERFACE.py** - Primary API for all functionality
2. **test_live_options.py** - Test with live IBKR data
3. **notebooks/live_options_trading_optimized.ipynb** - Interactive trading

## Data Flow

1. IB Gateway (port 8000) → 
2. `ibkr_connection.py` → 
3. `options_data.py` → 
4. `covered_call_optimization.py` → 
5. Results via `YOUR_MAIN_INTERFACE.py`