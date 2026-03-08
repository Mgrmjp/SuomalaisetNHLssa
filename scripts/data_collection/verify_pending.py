#!/usr/bin/env python3
"""
Helper script to identify players pending nationality verification.
"""
import sys
import os

# Add parent dir to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from leagues.utils.nationality_validator import validator

def main():
    pending = [k for k, v in validator.cache.items() if v.get('status') == 'pending']
    
    if not pending:
        print("✓ No players pending verification.")
        return

    print(f"Found {len(pending)} players pending verification:")
    for key in pending:
        p = validator.cache[key]
        print(f"  - {p['player_name']} ({p['league']}, {p['team']})")
    
    print("\nAction Required:")
    print("1. Search each player on EliteProspects/Google.")
    print("2. Update scripts/static/data/checks/nationality_cache.json with 'confirmed' or 'rejected'.")

if __name__ == "__main__":
    main()
