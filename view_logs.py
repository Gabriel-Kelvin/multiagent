#!/usr/bin/env python3
"""View application logs with error filtering"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8010"

print("=" * 70)
print("Application Logs")
print("=" * 70)

try:
    response = requests.get(f"{BASE_URL}/logs?limit=30")
    if response.status_code == 200:
        data = response.json()
        logs = data.get('logs', [])
        
        print(f"\nTotal logs: {len(logs)}")
        print("\nRecent Errors and Important Events:")
        print("-" * 70)
        
        for log in logs:
            level = log.get('level', '')
            event = log.get('event', '')
            node = log.get('node', '')
            timestamp = log.get('timestamp', '')
            run_id = log.get('run_id', '')[:8]
            
            # Show errors, exceptions, and important events
            if level in ['ERROR', 'EXCEPTION'] or 'error' in event.lower():
                print(f"\n[{level}] {timestamp}")
                print(f"  Node: {node}")
                print(f"  Event: {event}")
                print(f"  Run ID: {run_id}...")
                
                # Parse and display data
                data_str = log.get('data', '{}')
                try:
                    log_data = json.loads(data_str) if isinstance(data_str, str) else data_str
                    if 'error' in log_data:
                        print(f"  Error: {log_data['error']}")
                    if 'tried' in log_data:
                        print(f"  Tried queries: {log_data['tried']}")
                except:
                    print(f"  Data: {data_str[:200]}")
        
        print("\n" + "-" * 70)
        print("\nAll Recent Events (last 10):")
        print("-" * 70)
        
        for log in logs[-10:]:
            level = log.get('level', 'INFO')
            event = log.get('event', '')
            node = log.get('node', '')
            status = log.get('data', {})
            
            symbol = "X" if level in ['ERROR', 'EXCEPTION'] else "-"
            print(f"  [{symbol}] {node:12} | {event:30} | {level}")
            
    else:
        print(f"Error: Could not fetch logs (HTTP {response.status_code})")
        
except requests.exceptions.ConnectionError:
    print("\nError: Cannot connect to backend at http://localhost:8010")
    print("Make sure the backend server is running!")
    
except Exception as e:
    print(f"\nError: {e}")

print("\n" + "=" * 70)
print("\nTo see more logs:")
print("  - Open: http://localhost:8010/logs in browser")
print("  - Or run: curl http://localhost:8010/logs?limit=50")
print("=" * 70)

