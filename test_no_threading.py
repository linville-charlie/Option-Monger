#!/usr/bin/env python3
"""
Test our connection WITHOUT threading - like your working code
"""
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import time

class SimpleApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        
    def nextValidId(self, orderId):
        self.connected = True
        print(f"✅ Connected! Order ID: {orderId}")
        
    def error(self, reqId, errorCode, errorString):
        # Ignore info messages
        if errorCode >= 2000:
            print(f"Error {errorCode}: {errorString}")

def test_without_threading():
    """Test connection without threading - like your working code"""
    
    print("TEST 1: Without Threading (like your working code)")
    print("="*60)
    
    app = SimpleApp()
    app.connect("127.0.0.1", 8000, 0)
    
    # Give it a moment
    time.sleep(1)
    
    # Check if connected
    if app.isConnected():
        print("✅ app.isConnected() returns True")
    else:
        print("❌ app.isConnected() returns False")
    
    # Now run - this will block
    print("\nCalling app.run() - this will process messages...")
    print("Press Ctrl+C to stop")
    
    try:
        app.run()  # Blocks here
    except KeyboardInterrupt:
        print("\nStopped")
        app.disconnect()

def test_with_threading():
    """Test with threading - our current approach"""
    import threading
    
    print("\n\nTEST 2: With Threading (our current approach)")
    print("="*60)
    
    app = SimpleApp()
    app.connect("127.0.0.1", 8000, 0)
    
    # Start thread
    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()
    
    # Wait for connection
    time.sleep(2)
    
    if app.connected:
        print("✅ Connected via threading")
    else:
        print("❌ Not connected via threading")
        
    if app.isConnected():
        print("✅ app.isConnected() returns True")
    else:
        print("❌ app.isConnected() returns False")
    
    app.disconnect()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "thread":
        test_with_threading()
    else:
        test_without_threading()
        
    print("\nTo test threading: python test_no_threading.py thread")