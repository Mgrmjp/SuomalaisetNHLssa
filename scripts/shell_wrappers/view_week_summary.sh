#!/bin/bash
# View this week's Finnish NHL players summary with color coding for wins/losses

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}🏒 THIS WEEK'S FINNISH NHL SUMMARY${NC}"
echo "=================================="
echo ""

# Calculate this week's range (last 7 days)
END_DATE=$(date -d "yesterday" +%Y-%m-%d)
START_DATE=$(date -d "$END_DATE - 6 days" +%Y-%m-%d)

for date in $(seq 0 6); do
    file_date=$(date -d "$START_DATE + $date days" +%Y-%m-%d)
    file="data/prepopulated/games/${file_date}.json"

    if [ -f "$file" ]; then
        players=$(jq -r '.total_players // 0' "$file")
        games=$(jq -r '.total_games // 0' "$file")
        display=$(date -d "$file_date" +"%a %b %d")

        printf "%s: %2s games, %2s Finnish players\n" "$display" "$games" "$players"

        # Show all players with color coding for wins/losses
        if [ "$players" -gt 0 ]; then
            # Get each player with their game result
            jq -r '.players[]? | "\(.game_result)|\(.name)|\(.team)|\(.opponent)|\(.game_score)|\(.goals)|\(.assists)"' "$file" 2>/dev/null | while IFS='|' read -r result name team opponent score goals assists; do
                # Set color based on game result
                case "$result" in
                    W|SOW)
                        color=$GREEN
                        status="✓"
                        ;;
                    L|SOL)
                        color=$RED
                        status="✗"
                        ;;
                    OTW|OTL)
                        color=$YELLOW
                        status="OT"
                        ;;
                    *)
                        color=$BLUE
                        status="-"
                        ;;
                esac

                # Format the line with color
                if [ "$goals" != "0" ] || [ "$assists" != "0" ]; then
                    printf "${color}   %s %s (%s) %s %s - %sg, %sa${NC}\n" "$status" "$name" "$team" "$score" "$opponent" "$goals" "$assists"
                else
                    printf "${color}   %s %s (%s) %s %s${NC}\n" "$status" "$name" "$team" "$score" "$opponent"
                fi
            done
        fi
        echo ""
    fi
done | grep -v "0 games,  0 Finnish" || echo "No Finnish players this week yet."

# Legend
echo -e "${NC}=================================="
echo -e "${GREEN}✓ = Win${NC}  ${RED}✗ = Loss${NC}  ${YELLOW}OT = Overtime${NC}  ${BLUE}- = No game${NC}"
echo "=================================="
