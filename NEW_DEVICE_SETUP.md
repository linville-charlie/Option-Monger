# New Device Setup Guide

## Step-by-Step Setup on a New Device

### 1. Prerequisites to Install

#### On Windows:
- [ ] Install IB Gateway from [Interactive Brokers](https://www.interactivebrokers.com/en/trading/ibgateway-stable.php)
- [ ] Install WSL2 (if using Windows)
- [ ] Install Git
- [ ] Install Python 3.8+

#### On Mac/Linux:
- [ ] Install IB Gateway
- [ ] Install Git
- [ ] Install Python 3.8+

### 2. Clone the Repository

```bash
# Create projects directory
mkdir -p ~/projects/finance
cd ~/projects/finance

# Clone your private repo (you'll need to authenticate)
git clone https://github.com/linville-charlie/OptionMonger.git
cd OptionMonger
```

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac/WSL
# OR
venv\Scripts\activate     # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use any editor
```

**Key values to update in .env:**

```bash
# For WSL connecting to Windows:
TWS_HOST=<Windows_IP>  # Get with: ip route | grep default | awk '{print $3}'

# For Mac/Linux (IB Gateway on same machine):
TWS_HOST=127.0.0.1

# Port (IB Gateway default):
TWS_PAPER_PORT=4002
TWS_LIVE_PORT=4001
```

### 5. Find Your IP Addresses

#### On WSL:
```bash
# Your WSL IP (add to IB Gateway trusted IPs):
hostname -I | awk '{print $1}'

# Windows host IP (use in TWS_HOST):
ip route | grep default | awk '{print $3}'
```

#### On Mac/Linux:
```bash
# Your local IP:
hostname -I  # Linux
# OR
ipconfig getifaddr en0  # Mac
```

### 6. Configure IB Gateway

1. **Start IB Gateway**
2. **Log in to paper trading account**
3. **Configure API Settings:**
   - File → Global Configuration → API → Settings
   - Enable ActiveX and Socket Clients: ✅
   - Socket port: **4002**
   - Trusted IP Addresses: **Add your IP from step 5**
   - Read-Only API: ❌ (unchecked)

### 7. Configure Firewall

#### Windows:
- Windows Security → Firewall → Allow an app
- Add IB Gateway
- Allow both Private and Public networks

#### Mac:
- System Preferences → Security & Privacy → Firewall
- Add IB Gateway to allowed apps

#### Linux:
```bash
# If using ufw
sudo ufw allow 4002
```

### 8. Test the Connection

```bash
# Activate virtual environment if not already
source venv/bin/activate

# Test connection
python test_connection_now.py

# If connection fails, test port directly:
nc -zv <TWS_HOST_IP> 4002
```

### 9. Run Your First Strategy

```bash
# Test with demo data (always works)
python -c "
from YOUR_MAIN_INTERFACE import find_best_options
results = find_best_options('AAPL', '20250919', 100000, use_live_data=False)
print(results['recommendation'])
"
```

### 10. Enable Real Market Data (Optional)

1. **Get market data subscription** from IBKR ($6/month for options)
2. **Edit** `core/simple_real_strikes.py` line 112:
   ```python
   fetch_real_data = True  # Enable real data fetching
   ```
3. **Test with real data** (during market hours):
   ```bash
   python test_real_data_now.py
   ```

## Quick Checklist

- [ ] IB Gateway installed and running
- [ ] Python environment set up
- [ ] .env file configured with correct IPs
- [ ] Your IP added to IB Gateway trusted IPs
- [ ] Port 4002 configured in IB Gateway
- [ ] Firewall allows connection
- [ ] Connection test passes

## Common Issues & Solutions

### "Cannot connect to port 4002"
- Restart IB Gateway
- Check Windows/Mac firewall
- Verify IP addresses are correct
- Make sure IB Gateway shows "Connected"

### "No module named 'ibapi'"
- Make sure virtual environment is activated
- Run: `pip install ibapi`

### "Connection timeout"
- IB Gateway might need fresh login
- Check trusted IP list includes your IP
- Try both IPs if on WSL: 127.0.0.1 and Windows host IP

### Market data issues
- Demo mode works without subscriptions
- Real data needs market data subscription
- Market must be open (9:30 AM - 4:00 PM ET)

## Device-Specific Notes

### WSL on Windows
- Must use Windows host IP, not localhost
- Add WSL IP to IB Gateway trusted IPs
- May need to restart WSL after Windows updates

### Mac
- May need to allow IB Gateway in Security settings
- Use 127.0.0.1 as TWS_HOST

### Linux
- Use 127.0.0.1 as TWS_HOST
- May need to configure firewall (ufw/iptables)

## Support Files

- `IB_GATEWAY_SETUP.md` - Detailed IB Gateway configuration
- `COVERED_CALLS_GUIDE.md` - Understanding the strategy
- `INSTALLATION.md` - First-time installation
- `README.md` - Project overview

## Testing Everything Works

Run this comprehensive test:

```bash
# 1. Test imports
python -c "from YOUR_MAIN_INTERFACE import find_best_options; print('✓ Imports work')"

# 2. Test demo mode
python test_covered_calls_only.py

# 3. Test connection (if IB Gateway configured)
python test_connection_now.py

# 4. Run production test
python test_production_ready.py
```

If all tests pass, you're ready to optimize covered calls!