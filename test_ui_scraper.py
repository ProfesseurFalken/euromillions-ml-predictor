#!/usr/bin/env python3
"""
Test script to verify the UI scraper functions work correctly.
"""

from streamlit_adapters import init_full_history, update_incremental, get_system_status

print('='*60)
print('Testing Streamlit UI Adapter Functions')
print('='*60)

# Test 1: System Status
print('\n1. Testing get_system_status()...')
status = get_system_status()
print(f'   Total draws: {status.get("total_draws", "N/A")}')
print(f'   Latest draw: {status.get("latest_draw", "N/A")}')
print(f'   Models trained: {status.get("models_trained", "N/A")}')

# Test 2: Update Incremental (the main update button in UI)
print('\n2. Testing update_incremental() [UI Update Button]...')
result = update_incremental()
print(f'   Success: {result.get("success")}')
print(f'   Message: {result.get("message")}')
print(f'   Inserted: {result.get("inserted", 0)}')
print(f'   Missing found: {result.get("missing_found", 0)}')

print('\n' + '='*60)
print('UI Scraper Test Complete!')
print('='*60)
