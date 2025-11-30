#!/bin/bash
# Fetch Finnish NHL players data for the current week (Monday-Sunday)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Calculate this week's date range (Monday to Sunday)
START_OF_WEEK=$(date -d "last monday" +%Y-%m-%d)
END_OF_WEEK=$(date -d "sunday" +%Y-%m-%d)

# If today is Monday, use today as start
if [ $(date +%u) -eq 1 ]; then
    START_OF_WEEK=$(date +%Y-%m-%d)
fi

echo -e "${BLUE}🏒 Fetching THIS WEEK'S Finnish NHL players data${NC}"
echo -e "${YELLOW}Week: $START_OF_WEEK to $END_OF_WEEK${NC}"
echo ""

# Create output directory
mkdir -p data/prepopulated/games

# Loop through dates in the week
current_date=$(date -d "$START_OF_WEEK" +%Y-%m-%d)
end_date=$(date -d "$END_OF_WEEK" +%Y-%m-%d)

while [ "$(date -d "$current_date" +%Y%m%d)" -le "$(date -d "$end_date" +%Y%m%d)" ]; do
    echo -e "${BLUE}Processing${NC} $current_date..."

    # Run the fetcher
    python3 scripts/data_collection/finnish/fetch.py "$current_date" 2>&1 | grep -E "(✅|Found|Error|No Finnish)" || true

    # Copy to correct location if needed
    src_file="scripts/data/prepopulated/games/${current_date}.json"
    dst_file="data/prepopulated/games/${current_date}.json"
    if [ -f "$src_file" ]; then
        cp "$src_file" "$dst_file"
        echo -e "  ${GREEN}✓${NC} Saved to data/prepopulated/games/"
    fi

    # Move to next day
    current_date=$(date -d "$current_date + 1 day" +%Y-%m-%d)

    # Rate limiting - increased to avoid 429 errors
    sleep 5
done

echo ""
echo -e "${GREEN}✅ Week complete!${NC}"
echo -e "${BLUE}📁 Data saved to: data/prepopulated/games/${NC}"

# Show summary
echo ""
echo "📊 This Week's Summary:"
echo "========================"
# Loop through each day in the week to show summary
current_date=$(date -d "$START_OF_WEEK" +%Y-%m-%d)
end_date=$(date -d "$END_OF_WEEK" +%Y-%m-%d)

while [ "$(date -d "$current_date" +%Y%m%d)" -le "$(date -d "$end_date" +%Y%m%d)" ]; do
    file="data/prepopulated/games/${current_date}.json"
    if [ -f "$file" ]; then
        date=$(basename "$file" .json | tr '-' '/')
        players=$(jq -r '.total_players // 0' "$file")
        games=$(jq -r '.games | length // 0' "$file")
        printf "%s: %2s games, %2s Finnish players\n" "$date" "$games" "$players"
    fi
    # Move to next day
    current_date=$(date -d "$current_date + 1 day" +%Y-%m-%d)
done | grep -v "games,  0 Finnish"
