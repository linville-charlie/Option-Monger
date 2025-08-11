#!/usr/bin/env python3
"""
Test IBKR API connection according to official documentation
"""
import time
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class TestApp(EWrapper, EClient):
    """
    Minimal test app following IBKR documentation exactly
    """
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.nextOrderId = None
        
    def error(self, reqId, errorCode, errorString):
        """Error callback"""
        print(f"Error {errorCode}: {errorString}")
        # Error codes 2104-2108 are informational
        if errorCode in [2104, 2106, 2158]:
            print("  (This is informational, not an error)")
            
    def nextValidId(self, orderId):
        """Called when connection is established"""
        self.nextOrderId = orderId
        self.connected = True
        print(f"✅ Connected! Next order ID: {orderId}")
        
    def contractDetails(self, reqId, contractDetails):
        """Receive contract details"""
        print(f"Contract: {contractDetails.contract.symbol} at {contractDetails.contract.exchange}")
        
    def contractDetailsEnd(self, reqId):
        """End of contract details"""
        print("Contract details received")
        
    def connectAck(self):
        """Acknowledge connection"""
        print("Connection acknowledged")
        
    def connectionClosed(self):
        """Connection closed"""
        print("Connection closed")
        self.connected = False

def run_loop(app):
    """Run the client message loop"""
    app.run()

def test_connection():
    """Test IBKR API connection following official docs"""
    
    print("IBKR API CONNECTION TEST")
    print("="*60)
    
    # Connection parameters
    # According to docs: IB Gateway default ports are 4001 (live) and 4002 (paper)
    host = "127.0.0.1"  # Try localhost first
    port = 4002  # IB Gateway paper trading port
    clientId = 1  # Must be unique per connection
    
    # Check if we're in WSL
    import os
    if 'WSL_DISTRO_NAME' in os.environ:
        # In WSL, need to connect to Windows host
        import subprocess
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'default' in line:
                host = line.split()[2]
                break
        print(f"Detected WSL environment, using Windows host: {host}")
    
    print(f"Connecting to {host}:{port} with client ID {clientId}")
    print("-"*60)
    
    # Create app
    app = TestApp()
    
    # Connect
    app.connect(host, port, clientId)
    
    # Start message thread
    thread = threading.Thread(target=run_loop, args=(app,), daemon=True)
    thread.start()
    
    # Wait for connection
    timeout = 10
    start = time.time()
    while not app.connected and time.time() - start < timeout:
        time.sleep(0.1)
    
    if app.connected:
        print("\n✅ CONNECTION SUCCESSFUL!")
        print("-"*60)
        
        # Test requesting contract details
        print("\nTesting contract details request...")
        contract = Contract()
        contract.symbol = "AAPL"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        
        app.reqContractDetails(1, contract)
        
        # Wait a bit for response
        time.sleep(2)
        
        # Request server time
        print("\nRequesting server time...")
        app.reqCurrentTime()
        time.sleep(1)
        
        # Disconnect
        app.disconnect()
        
    else:
        print("\n❌ CONNECTION FAILED")
        print("\nPlease check:")
        print("1. IB Gateway is running")
        print("2. API connections are enabled in IB Gateway")
        print("3. Port 4002 is configured for paper trading")
        print("4. Your IP is in the trusted IP list")
        
        if 'WSL_DISTRO_NAME' in os.environ:
            print(f"\n5. For WSL, add this IP to IB Gateway trusted IPs:")
            import subprocess
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            wsl_ip = result.stdout.strip().split()[0]
            print(f"   {wsl_ip}")
    
    print("\n" + "="*60)
    print("According to IBKR documentation:")
    print("- IB Gateway paper port: 4002 (default)")
    print("- IB Gateway live port: 4001 (default)")
    print("- TWS paper port: 7497")
    print("- TWS live port: 7496")
    print("- Client ID must be unique (0 = master)")
    print("="*60)

if __name__ == "__main__":
    test_connection()