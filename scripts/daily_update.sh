#!/bin/bash

# suomalaisetnhlssa - Daily Update Script
# This script runs the full data collection pipeline:
# 1. Updates player cache (scans rosters for new players)
# 2. Fetches latest game data

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Determine project root and virtual environment
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"

# Check if .venv python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${YELLOW}Warning: Virtual environment python not found at $VENV_PYTHON${NC}"
    echo "Using system python3 instead..."
    VENV_PYTHON="python3"
fi

cd "$PROJECT_ROOT"

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}🏒 SUOMALAISET NHL:SSÄ - DAILY UPDATE${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Step 1: Update Player Cache
echo -e "${GREEN}[1/3] Updating Player Cache...${NC}"
echo "Scanning rosters for new Finnish players..."
$VENV_PYTHON scripts/data_collection/finnish/build_cache.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Warning: Cache build failed or completed with warnings.${NC}"
fi
echo ""

# Step 2: Determine Date
# Usage: ./daily_update.sh [YYYY-MM-DD]
# Default: Yesterday (to get completed games if run in the morning)
if [ -n "$1" ]; then
    TARGET_DATE="$1"
    echo -e "${GREEN}[2/3] Using specified date: $TARGET_DATE${NC}"
else
    # Check if requests is available for checking schedule logic, otherwise just use yesterday
    # For simplicity, we default to yesterday as that's the extensive use case (checking last night's games)
    TARGET_DATE=$(date -d "yesterday" +%Y-%m-%d)
    echo -e "${GREEN}[2/3] Using default date (yesterday): $TARGET_DATE${NC}"
    echo "Tip: You can provide a specific date: ./scripts/daily_update.sh 2026-01-23"
fi
echo ""

# Step 3: Fetch Game Data
echo -e "${GREEN}[3/3] Fetching Game Data for $TARGET_DATE...${NC}"
$VENV_PYTHON scripts/data_collection/finnish/fetch.py "$TARGET_DATE"

EXIT_CODE=$?
echo ""
echo -e "${BLUE}================================================================${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Update completed successfully!${NC}"
else
    echo -e "${YELLOW}⚠️ Update completed with issues.${NC}"
fi

# Step 4: Optional Git Commit (uncomment if running on server)
# git add static/data/prepopulated/games/
# git commit -m "Auto-update data for $TARGET_DATE"
# git push
