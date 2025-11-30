#!/bin/bash
# Fetch Finnish NHL players data for the last 7 days (recent week)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Calculate date range (last 7 days)
END_DATE=$(date -d "yesterday" +%Y-%m-%d)  # Yesterday (today's games may not be done yet)
START_DATE=$(date -d "$END_DATE - 6 days" +%Y-%m-%d)  # 7 days back

echo -e "${BLUE}🏒 Fetching RECENT WEEK data (last 7 days)${NC}"
echo -e "${YELLOW}Range: $START_DATE to $END_DATE${NC}"
echo ""

# Create output directory
mkdir -p data/prepopulated/games

# Loop through dates
current_date="$START_DATE"

while [ "$(date -d "$current_date" +%Y%m%d)" -le "$(date -d "$END_DATE" +%Y%m%d)" ]; do
    echo -e "${BLUE}Processing${NC} $current_date..."

    # Run the fetcher
    python3 scripts/data_collection/finnish/fetch.py "$current_date" 2>&1 | grep -E "(✅|Found|Error|No Finnish)" || true

    # Copy to correct location if needed
    src_file="scripts/data/prepopulated/games/${current_date}.json"
    dst_file="data/prepopulated/games/${current_date}.json"
    if [ -f "$src_file" ]; then
        cp "$src_file" "$dst_file"
        echo -e "  ${GREEN}✓${NC} Saved"
    fi

    # Move to next day
    current_date=$(date -d "$current_date + 1 day" +%Y-%m-%d)

    # Rate limiting
    sleep 2
done

echo ""
echo -e "${GREEN}✅ Recent week fetched!${NC}"
echo ""
echo "📊 Week Summary:"
echo "=================="
total_players=0
total_days=0

for date in $(date -d "$START_DATE" +%Y-%m-%d); do
    file="data/prepopulated/games/${date}.json"
    if [ -f "$file" ]; then
        players=$(jq -r '.total_players // 0' "$file")
        games=$(jq -r '.total_games // 0' "$file")
        display_date=$(date -d "$date" +"%b %d")
        printf "%s: %2s games, %2s Finnish players\n" "$display_date" "$games" "$players"
        total_players=$((total_players + players))
        total_days=$((total_days + 1))
    fi
    [ "$date" = "$END_DATE" ] && break
    date=$(date -d "$date + 1 day" +%Y-%m-%d)
done

echo "=================="
echo "Total: $total_players Finnish players across $total_days days"
