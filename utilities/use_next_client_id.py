#!/usr/bin/env python3
"""
Automatically rotate to the next available client ID to avoid competing sessions
"""
import os
import time
from pathlib import Path

def get_current_client_id():
    """Read current client ID from .env"""
    env_path = Path('.env')
    if not env_path.exists():
        return 1
    
    with open(env_path) as f:
        for line in f:
            if line.startswith('TWS_CLIENT_ID='):
                try:
                    return int(line.split('=')[1].strip())
                except:
                    return 1
    return 1

def set_client_id(client_id):
    """Update client ID in .env"""
    env_path = Path('.env')
    if not env_path.exists():
        print(f"Error: .env file not found")
        return False
    
    lines = []
    with open(env_path) as f:
        for line in f:
            if line.startswith('TWS_CLIENT_ID='):
                lines.append(f'TWS_CLIENT_ID={client_id}\n')
            else:
                lines.append(line)
    
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Updated .env to use client ID {client_id}")
    return True

def test_client_id(client_id):
    """Test if a client ID can connect"""
    # Temporarily set the client ID
    original_id = os.environ.get('TWS_CLIENT_ID')
    os.environ['TWS_CLIENT_ID'] = str(client_id)
    
    try:
        from core.ibkr_connection import IBKRConnection
        from core.config import Config
        
        # Force reload config with new client ID
        Config.TWS_CLIENT_ID = client_id
        
        print(f"Testing client ID {client_id}...")
        conn = IBKRConnection()
        
        if conn.connect():
            print(f"✅ Client ID {client_id} connected successfully!")
            conn.disconnect()
            return True
        else:
            print(f"❌ Client ID {client_id} failed to connect")
            return False
            
    except Exception as e:
        print(f"❌ Client ID {client_id} error: {e}")
        return False
    finally:
        # Restore original
        if original_id:
            os.environ['TWS_CLIENT_ID'] = original_id

def main():
    print("="*60)
    print("FINDING AVAILABLE CLIENT ID")
    print("="*60)
    
    current_id = get_current_client_id()
    print(f"\nCurrent client ID: {current_id}")
    
    # Try client IDs 1-10
    available_ids = []
    for client_id in range(1, 11):
        if test_client_id(client_id):
            available_ids.append(client_id)
            break  # Stop at first working ID
        time.sleep(1)  # Brief pause between attempts
    
    if available_ids:
        new_id = available_ids[0]
        if new_id != current_id:
            print(f"\nSwitching from client ID {current_id} to {new_id}")
            set_client_id(new_id)
        else:
            print(f"\nClient ID {current_id} is already working")
        
        print("\n" + "="*60)
        print("SUCCESS - You can now run your scripts!")
        print(f"Using client ID: {new_id}")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("ERROR - No available client IDs found")
        print("="*60)
        print("Try these steps:")
        print("1. Close all Python scripts")
        print("2. Restart IB Gateway")
        print("3. Run: python kill_all_connections.py")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())