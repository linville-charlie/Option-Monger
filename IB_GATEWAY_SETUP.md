# IB Gateway Setup Instructions

## Current Configuration
- **Windows Host IP**: 172.21.112.1
- **Port**: 4002
- **Your WSL IP**: 172.21.116.114

## Steps to Configure IB Gateway:

### 1. Start IB Gateway on Windows
- Launch IB Gateway
- Log in to your paper trading account

### 2. Configure API Settings
1. Click **File → Global Configuration**
2. Select **API → Settings**
3. Configure as follows:
   - **Enable ActiveX and Socket Clients**: ✅ CHECKED
   - **Socket port**: 4002
   - **Master API client ID**: 0
   - **Trusted IP Addresses**: Add `172.21.116.114` (your WSL IP)
   - **Allow connections from localhost only**: ✅ CHECKED
   - **Read-Only API**: ❌ UNCHECKED

### 3. Windows Firewall
1. Open Windows Security
2. Go to Firewall & network protection
3. Click "Allow an app through firewall"
4. Add IB Gateway if not listed
5. Allow both Private and Public networks

### 4. Test Connection
Run this command in WSL:
```bash
nc -zv 172.21.112.1 4002
```

If it says "succeeded", the connection is working.

## Troubleshooting

### Port Not Reachable
1. **Check IB Gateway is running**: Look for the green "Connected" status
2. **Verify port number**: Should show "Socket port 4002" in API settings
3. **Check Windows Defender**: May be blocking the connection
4. **Try restarting IB Gateway**: Sometimes needed after config changes

### Alternative Ports
If 4002 doesn't work, try:
- 7497 (TWS paper trading default)
- 7496 (TWS live trading default)
- 4001 (IB Gateway live default)

### Finding Your IPs
```bash
# Your WSL IP (add to trusted IPs):
hostname -I

# Windows host IP (use in TWS_HOST):
ip route | grep default | awk '{print $3}'
```

## Testing Your Strategy

Once connected, you can:
1. Get real stock prices
2. Fetch actual bid/ask spreads
3. Get real-time Greeks
4. Optimize covered calls with live data

Run: `python test_connection_now.py` to verify everything works.