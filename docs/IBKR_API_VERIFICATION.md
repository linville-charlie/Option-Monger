# IBKR API Connection Verification

## Official IBKR API Documentation Review

Based on the official Interactive Brokers API documentation, here are the correct connection parameters and requirements:

### 1. Default Port Numbers

According to IBKR documentation:

| Application | Paper Trading | Live Trading |
|------------|--------------|--------------|
| **IB Gateway** | 4002 | 4001 |
| **TWS** | 7497 | 7496 |

### 2. Connection Requirements

#### API Settings in IB Gateway:
1. **File → Global Configuration → API → Settings**
2. Required settings:
   - ✅ **Enable ActiveX and Socket Clients** - MUST be checked
   - **Socket port**: 4002 (for paper trading)
   - **Master API client ID**: 0 (leave as default)
   - **Trusted IP Addresses**: Must include your connecting IP
   - ❌ **Read-Only API** - Should be UNCHECKED for trading

#### Client Connection Parameters:
```python
# Correct connection parameters per IBKR docs
host = "127.0.0.1"  # localhost if on same machine
port = 4002         # IB Gateway paper trading
clientId = 1        # Must be unique, 0 is master
```

### 3. Connection Process (Per IBKR Docs)

The correct sequence is:
1. Create EClient instance
2. Call `connect(host, port, clientId)`
3. Start message processing thread with `run()`
4. Wait for `nextValidId()` callback
5. Connection is established when `nextValidId()` is received

### 4. Our Implementation Review

✅ **Correct implementations:**
- Inheriting from both `EWrapper` and `EClient`
- Starting message thread with `run()`
- Waiting for `nextValidId()` callback
- Using proper port numbers (4002 for paper)

⚠️ **Potential issues:**
- WSL requires Windows host IP, not localhost
- Firewall might block connection
- IB Gateway might not be running

### 5. WSL-Specific Configuration

For WSL connecting to Windows IB Gateway:

```python
# WSL must use Windows host IP
host = "172.21.112.1"  # From: ip route | grep default
port = 4002
clientId = 1
```

**Your WSL IP** (must be in IB Gateway trusted IPs):
```
172.21.116.114  # From: hostname -I
```

### 6. Common Connection Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port closed | IB Gateway not running or wrong port |
| Connection timeout | IP not in trusted list |
| "No security definition" | Market data subscription needed |
| Error 504 | Not connected to server |
| Error 502 | Cannot connect to TWS |

### 7. Verification Checklist

Before connecting, verify:

- [ ] IB Gateway is running (shows "Connected" status)
- [ ] Paper trading is selected in IB Gateway
- [ ] API Settings show:
  - [ ] Socket port: 4002
  - [ ] Enable ActiveX: ✅
  - [ ] Your WSL IP in trusted list: 172.21.116.114
- [ ] Windows Firewall allows IB Gateway
- [ ] No VPN interfering with connection

### 8. Testing Connection

Run these tests in order:

1. **Port test** (should show OPEN):
   ```bash
   nc -zv 172.21.112.1 4002
   ```

2. **Simple API test**:
   ```python
   python test_ibkr_api_correct.py
   ```

3. **Full connection test**:
   ```python
   python test_connection_now.py
   ```

### 9. API Methods for Options

Per IBKR documentation, for options data:

```python
# Correct way to request option chain
contract = Contract()
contract.symbol = "AAPL"
contract.secType = "OPT"
contract.exchange = "SMART"
contract.currency = "USD"
contract.lastTradeDateOrContractMonth = "20250919"

# Request contract details for all strikes
app.reqContractDetails(reqId, contract)
```

### 10. Rate Limits

IBKR API has rate limits:
- Max 50 messages per second
- Max 100 simultaneous market data lines
- Historical data: 60 requests per 10 minutes

Our implementation correctly handles this by:
- Fetching strikes first, then option data
- Using delays between requests
- Caching data to reduce API calls

## Conclusion

Our implementation follows IBKR API documentation correctly. The connection issues are likely due to:

1. **IB Gateway not running** on Windows
2. **Port 4002 not open** (verified by our tests)
3. **WSL IP not in trusted list**

## Next Steps

1. Start IB Gateway on Windows
2. Verify port 4002 in API settings
3. Add WSL IP (172.21.116.114) to trusted IPs
4. Run connection test again