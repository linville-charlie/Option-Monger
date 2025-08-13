# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Interactive Brokers account
- IB Gateway or TWS installed
- Git

## Quick Setup

### 1. Clone the Repository

Since this is a private repository, you'll need to authenticate:

```bash
git clone https://github.com/linville-charlie/OptionMonger.git
cd OptionMonger
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- Set `TWS_HOST` to your Windows IP (from WSL: `ip route | grep default | awk '{print $3}'`)
- Set ports (default 4002 for IB Gateway)
- Keep `USE_PAPER_TRADING=true` for testing

### 5. Configure IB Gateway

1. Start IB Gateway on Windows
2. Go to File → Global Configuration → API → Settings
3. Configure:
   - Enable ActiveX and Socket Clients: ✓
   - Socket port: 4002
   - Add your WSL IP to Trusted IP Addresses (run `hostname -I` in WSL)

### 6. Test Connection

```bash
python test_connection_now.py
```

### 7. Run Your First Strategy

```bash
python -c "
from YOUR_MAIN_INTERFACE import find_best_options

results = find_best_options('AAPL', '20250919', 100000, use_live_data=False)
print(results['recommendation'])
"
```

## Troubleshooting

### Connection Issues
- Restart IB Gateway
- Check Windows Firewall
- Verify your WSL IP is in trusted IPs
- Make sure port 4002 is correct

### Import Errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Market Data
- Demo mode works without subscriptions
- For real data, you need IBKR market data subscriptions

## Next Steps

1. Read [COVERED_CALLS_GUIDE.md](COVERED_CALLS_GUIDE.md) to understand the strategy
2. Check [IB_GATEWAY_SETUP.md](IB_GATEWAY_SETUP.md) for detailed IB Gateway configuration
3. Run tests with `python test_production_ready.py`
4. Start optimizing your covered calls!