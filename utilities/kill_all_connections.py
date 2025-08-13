#!/usr/bin/env python3
"""
Kill all IB API connections to resolve competing session errors
"""
import psutil
import sys
import time

def kill_python_processes():
    """Find and kill all Python processes that might be using IB API"""
    killed = []
    current_pid = psutil.Process().pid
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Skip current process
            if proc.info['pid'] == current_pid:
                continue
                
            # Check if it's a Python process
            if 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline:
                    # Check if it's running any IB-related scripts
                    cmd_str = ' '.join(cmdline).lower()
                    ib_keywords = ['ibkr', 'ib_gateway', 'test_', 'option', 'tws', 'ibapi']
                    
                    if any(keyword in cmd_str for keyword in ib_keywords):
                        print(f"Killing process {proc.info['pid']}: {' '.join(cmdline[:3])}")
                        proc.kill()
                        killed.append(proc.info['pid'])
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return killed

def test_connection():
    """Test if we can connect without competing session error"""
    try:
        from core.ibkr_connection import IBKRConnection
        
        print("\nTesting connection...")
        conn = IBKRConnection()
        if conn.connect():
            print("✅ Successfully connected without competing session!")
            conn.disconnect()
            return True
        else:
            print("❌ Connection failed")
            return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    print("="*60)
    print("KILLING COMPETING IB API SESSIONS")
    print("="*60)
    
    # Step 1: Kill Python processes
    print("\n1. Looking for Python processes using IB API...")
    killed = kill_python_processes()
    
    if killed:
        print(f"\n✅ Killed {len(killed)} processes")
        print("Waiting 3 seconds for cleanup...")
        time.sleep(3)
    else:
        print("No competing Python processes found")
    
    # Step 2: Test connection
    print("\n2. Testing IB Gateway connection...")
    if test_connection():
        print("\n" + "="*60)
        print("SUCCESS - You can now run your scripts!")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("Connection still failing. Try these steps:")
        print("="*60)
        print("1. Close and restart IB Gateway")
        print("2. Check Task Manager for lingering Python processes")
        print("3. Try using a different client ID (2, 3, or 4)")
        print("4. Restart your computer if nothing else works")
        return 1

if __name__ == "__main__":
    sys.exit(main())