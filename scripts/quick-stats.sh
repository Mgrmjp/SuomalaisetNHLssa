#!/bin/bash
# Quick summary - just wins and losses for this week

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}🏒 THIS WEEK'S QUICK STATS${NC}"
echo "=========================="
echo ""

# Counters
wins=0
losses=0
ot=0
scorers=0

# Calculate this week's range (last 7 days)
END_DATE=$(date -d "yesterday" +%Y-%m-%d)
START_DATE=$(date -d "$END_DATE - 6 days" +%Y-%m-%d)

for date in $(seq 0 6); do
    file_date=$(date -d "$START_DATE + $date days" +%Y-%m-%d)
    file="data/prepopulated/games/${file_date}.json"

    if [ -f "$file" ]; then
        players=$(jq -r '.total_players // 0' "$file")

        if [ "$players" -gt 0 ]; then
            # Count wins/losses/OT
            day_wins=$(jq -r '[.players[]? | select(.game_result == "W" or .game_result == "SOW")] | length' "$file" 2>/dev/null)
            day_losses=$(jq -r '[.players[]? | select(.game_result == "L" or .game_result == "SOL")] | length' "$file" 2>/dev/null)
            day_ot=$(jq -r '[.players[]? | select(.game_result == "OTW" or .game_result == "OTL")] | length' "$file" 2>/dev/null)
            day_scorers=$(jq -r '[.players[]? | select(.goals > 0 or .assists > 0)] | length' "$file" 2>/dev/null)

            wins=$((wins + day_wins))
            losses=$((losses + day_losses))
            ot=$((ot + day_ot))
            scorers=$((scorers + day_scorers))
        fi
    fi
done

# Display summary
echo -e "Wins:   ${GREEN}$wins${NC}"
echo -e "Losses: ${RED}$losses${NC}"
echo -e "OT:     ${YELLOW}$ot${NC}"
echo ""
echo "Players with points: $scorers"
echo "Win %: $(awk "BEGIN {printf \"%.1f\", ($wins/($wins+$losses+$ot))*100}")%"
echo ""
echo "=========================="
