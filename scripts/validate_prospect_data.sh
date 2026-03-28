#!/bin/bash
# Validate prospect data quality across all data files
# Usage: ./scripts/validate_prospect_data.sh [--fix]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

if [ "$1" = "--fix" ]; then
    echo "Running validation with auto-fix..."
    python scripts/data_collection/validate_prospect_data.py --file all --fix
else
    echo "Running validation..."
    python scripts/data_collection/validate_prospect_data.py --file all
fi
