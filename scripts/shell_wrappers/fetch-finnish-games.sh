#!/bin/bash

# Simple wrapper for fetching Finnish players data for a date range

START_DATE=${1:-2025-10-01}
END_DATE=${2:-$(date +%Y-%m-%d)}

echo "🏒 Fetching Finnish NHL players data"
echo "Date range: $START_DATE to $END_DATE"
echo ""

# Create output directory
mkdir -p data/prepopulated/games

# Loop through dates
current_date=$(date -d "$START_DATE" +%Y-%m-%d)
end_date=$(date -d "$END_DATE" +%Y-%m-%d)

while [ "$(date -d "$current_date" +%Y%m%d)" -le "$(date -d "$end_date" +%Y%m%d)" ]; do
    echo "Processing $current_date..."

    python3 scripts/data_collection/finnish/fetch.py "$current_date"

    # Move to next day
    current_date=$(date -d "$current_date + 1 day" +%Y-%m-%d)

    # Rate limiting
    sleep 2
done

echo ""
echo "✅ Done! Finnish players data saved to data/prepopulated/games/"
