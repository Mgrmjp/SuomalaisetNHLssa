# Week Commands - Quick Reference

## 🚀 Easy Commands to Add

Add these aliases to your `~/.bashrc` or `~/.zshrc`:

```bash
# Fetch this week's games (Monday-Sunday)
alias nhl-week='cd /home/miikka/dev/suomalaisetnhlssa && bash scripts/fetch-this-week.sh'

# Fetch recent 7 days of games
alias nhl-recent='cd /home/miikka/dev/suomalaisetnhlssa && bash scripts/fetch-recent-week.sh'

# View this week's summary (with color coding!)
alias nhl-summary='cd /home/miikka/dev/suomalaisetnhlssa && bash scripts/view-week.sh'

# Quick wins/losses stats
alias nhl-stats='cd /home/miikka/dev/suomalaisetnhlssa && bash scripts/quick-stats.sh'

# Today's games
alias nhl-today='cd /home/miikka/dev/suomalaisetnhlssa && python3 scripts/data_collection/finnish/fetch.py $(date +%Y-%m-%d) && cp scripts/data/prepopulated/games/$(date +%Y-%m-%d).json data/prepopulated/games/'
```

# Daily full update (Finds new players + fetches latest games)
alias nhl-update='cd /home/miikka/dev/suomalaisetnhlssa && bash scripts/daily_update.sh'

Then reload your shell:
```bash
source ~/.bashrc
```

## 📖 Direct Usage

### Option 1: This Week (Calendar Week)
```bash
bash scripts/fetch-this-week.sh
```
- Fetches: Monday → Sunday of current calendar week
- Smart: If today is Monday, starts today
- Example (Nov 29, 2025): Fetches Nov 24-30

### Option 2: Recent Week (Last 7 Days)
```bash
bash scripts/fetch-recent-week.sh
```
- Fetches: Last 7 completed game days
- Practical: Gets recent games that have finished
- Example: Nov 23-29 (excludes today if games are ongoing)

## 📊 View Week Summary

Create a view script to see the data:

```bash
# Create scripts/view-week.sh
cat > scripts/view-week.sh << 'EOF'
#!/bin/bash
echo "🏒 THIS WEEK'S FINNISH NHL SUMMARY"
echo "=================================="
echo ""

START=$(date -d "last monday" +%Y-%m-%d)
END=$(date +%Y-%m-%d)

for file in data/prepopulated/games/{$START..$END}.json; do
    if [ -f "$file" ]; then
        date=$(basename "$file" .json)
        players=$(jq -r '.total_players // 0' "$file")
        games=$(jq -r '.total_games // 0' "$file")
        display=$(date -d "$date" +"%a %b %d")

        printf "%s: %2s games, %2s Finnish players\n" "$display" "$games" "$players"

        # Show top scorers if any
        if [ "$players" -gt 0 ]; then
            jq -r '.players[]? | select(.goals > 0 or .assists > 0) | "   → \(.name) (\(.team)) - \(.goals)g, \(.assists)a"' "$file" 2>/dev/null | sed 's/^/   /'
        fi
        echo ""
    fi
done | grep -v "0 games,  0 Finnish"
EOF

chmod +x scripts/view-week.sh
```

## 🔄 Daily Workflow

### After Games Finish Each Day:
```bash
# Fetch just today (or yesterday if today isn't done)
python3 scripts/data_collection/finnish/fetch.py 2025-11-30
cp scripts/data/prepopulated/games/2025-11-30.json data/prepopulated/games/
```

### Once a Week:
```bash
# Get all games from the week
nhl-week  # or bash scripts/fetch-this-week.sh
```

### Quick Check:
```bash
# See this week's summary (with color coding!)
nhl-summary  # or bash scripts/view-week.sh

# Quick wins/losses only
nhl-stats  # or bash scripts/quick-stats.sh
```

### Automatic Daily Update (Recommended)
```bash
# Updates player list AND fetches yesterday's games
nhl-update  # or bash scripts/daily_update.sh
```
- **Best simple command** to keep everything in sync.
- Finds new players (like Lenni Hameenaho).
- Fetches latest stats.

## 📁 Data Location

All data is saved to:
- **Primary**: `data/prepopulated/games/YYYY-MM-DD.json`
- **Cache**: `scripts/data/prepopulated/games/` (temporary, auto-copied)

## ⚡ Quick Commands Reference

| Command | Description |
|---------|-------------|
| `nhl-week` | Fetch this calendar week (Mon-Sun) |
| `nhl-recent` | Fetch last 7 days |
| `nhl-summary` | View week's Finnish players (COLOR CODED!) |
| `nhl-stats` | Quick wins/losses summary |
| `nhl-today` | Fetch today's games |
| `bash scripts/fetch-finnish-games.sh 2025-11-24 2025-11-30` | Custom date range |
| `python3 scripts/data_collection/finnish/fetch.py 2025-11-30` | Single date |

## 🌈 Color Coding

The `nhl-summary` command now includes **color coding** for wins and losses:

- **Green ✓** = Win
- **Red ✗** = Loss
- **Yellow OT** = Overtime win/loss
- **Blue -** = No game/didn't play

**Example output:**
```
   ✓ Roope Hintz (DAL) 4-3 UTA - 1g, 0a
   ✗ Anton Lundell (FLA) 3-5 CGY - 0g, 1a
   ✓ Erik Haula (NSH) 4-3 CHI
```

Shows:
- Win/loss indicator with color
- Team name
- Game score (team score - opponent score)
- Player stats if they scored

## 🎯 Tips

1. **Best Time to Fetch**: After all games finish (usually after 11 PM ET)
2. **Avoid**: Fetching during active games (data incomplete)
3. **Rate Limiting**: Scripts include 2-second delays (respects NHL API)
4. **Already Fetched**: Scripts skip dates with existing data
5. **Color Output**: Use `nhl-summary` to see wins/losses at a glance!
