#!/bin/bash

# Fixed script to generate prepopulated data for all November 2025 dates

TOTAL_DAYS=30
CURRENT_DAY=0
COMPLETED_DATES=()

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting prepopulation for November 2025 (FIXED VERSION)...${NC}"
echo

# Function to draw progress bar
draw_progress_bar() {
    local progress=$1
    local total=$2
    local width=50
    local percentage=$((progress * 100 / total))
    local filled=$((progress * width / total))
    local empty=$((width - filled))

    printf "\r${GREEN}[${NC}"
    printf "%*s" $filled | tr ' ' '='
    printf "${RED}%*s${NC}" $empty | tr ' ' '-'
    printf "${GREEN}]${NC} %d%% (%d/%d)" $percentage $progress $total
}

# Function to process a single date with rate limiting
process_date() {
    local date_str=$1

    echo -e "\n${BLUE}🏒 Processing $date_str...${NC}"

    # Run the script and capture output with longer delays
    local output=$(python3 scripts/data/fetch-nhl-data.py "$date_str" 2>&1)
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        # Extract number of players found from output
        local players=$(echo "$output" | grep "Generated data for" | grep -o "[0-9]* players" | grep -o "[0-9]*")
        if [ -z "$players" ]; then
            players=0
        fi

        echo -e "${GREEN}✅${NC} $date_str: $players players found"

        # Show player details if any found
        if [ "$players" -gt 0 ]; then
            echo "$output" | grep "Players found:" -A 20 | tail -n +2 | head -10
        fi

        COMPLETED_DATES+=("$date_str ($players players)")
    else
        echo -e "${RED}❌${NC} $date_str: Error occurred"
        echo "$output" | head -3
        COMPLETED_DATES+=("$date_str (ERROR)")
    fi

    # Rate limiting: wait between dates to avoid 429 errors
    sleep 5
}

# Check which dates are already done
echo -e "${BLUE}🔍 Checking for existing files...${NC}"
for day in {1..30}; do
    # Use printf with explicit decimal to avoid octal issues
    date_str=$(printf "2025-11-%02d" $day)
    if [ -f "static/data/prepopulated/games/$date_str.json" ]; then
        echo -e "${GREEN}✓${NC} $date_str already exists"
        COMPLETED_DATES+=("$date_str (EXISTS)")
        CURRENT_DAY=$((CURRENT_DAY + 1))
    fi
done

if [ $CURRENT_DAY -gt 0 ]; then
    echo -e "${GREEN}Found $CURRENT_DAY existing files, will process remaining dates.${NC}"
    echo
fi

# Loop through all dates in November 2025, skipping existing ones
for day in {1..30}; do
    # Use printf with explicit decimal to avoid octal issues
    date_str=$(printf "2025-11-%02d" $day)

    # Skip if file already exists
    if [ -f "static/data/prepopulated/games/$date_str.json" ]; then
        continue
    fi

    CURRENT_DAY=$((CURRENT_DAY + 1))

    # Update progress bar
    draw_progress_bar $((CURRENT_DAY - 1)) $TOTAL_DAYS

    # Process the date
    process_date "$date_str"
done

# Final progress bar
draw_progress_bar $TOTAL_DAYS $TOTAL_DAYS
echo
echo

echo -e "${GREEN}✅ Prepopulation complete for November 2025!${NC}"

# Show summary
echo
echo -e "${BLUE}📊 Summary:${NC}"
echo "Total files: $(ls -1 static/data/prepopulated/games/2025-11-*.json 2>/dev/null | wc -l)"
echo "Output directory: static/data/prepopulated/games/"

echo
echo -e "${BLUE}📋 Processed dates:${NC}"
for date_info in "${COMPLETED_DATES[@]}"; do
    echo "  $date_info"
done

echo
echo -e "${GREEN}🎉 All done! The prepopulated data is ready for use.${NC}"