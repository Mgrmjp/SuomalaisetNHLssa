#!/bin/bash

# suomalaisetnhlssa - Prospects & Draft Rankings Update Script
# This script updates:
# 1. Draft rankings from EliteProspects (multiple sources)
# 2. Unified draft rankings (NHL + EP)
# 3. Finnish prospects statistics

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
    VENV_PYTHON="python3"
fi

cd "$PROJECT_ROOT"

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}🏒 SUOMALAISET NHL:SSÄ - PROSPECTS UPDATE${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Step 1: Update EP Rankings
echo -e "${GREEN}[1/3] Fetching EliteProspects Rankings...${NC}"
$VENV_PYTHON scripts/data_collection/finnish/fetch_ep_rankings.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Warning: EP rankings fetch failed.${NC}"
fi
echo ""

# Step 2: Build Unified Rankings
echo -e "${GREEN}[2/3] Building Unified Draft Rankings...${NC}"
$VENV_PYTHON scripts/data_collection/finnish/build_draft_rankings.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Warning: Draft rankings build failed.${NC}"
fi
echo ""

# Step 3: Update Prospects Cache (Stats)
echo -e "${GREEN}[3/3] Updating Prospects Stats Cache...${NC}"
# Note: build_prospects_cache.py is the existing script for this
$VENV_PYTHON scripts/data_collection/finnish/build_prospects_cache.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Warning: Prospects cache build failed.${NC}"
fi

echo ""
echo -e "${BLUE}================================================================${NC}"
echo -e "${GREEN}✅ Prospects update completed!${NC}"
