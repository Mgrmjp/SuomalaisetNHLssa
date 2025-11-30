# Venue City Mapping Implementation

## Problem
City/state information was not being displayed on game venues. The `game_city` field was always empty, so the UI only showed the venue name (e.g., "American Airlines Center") without the city (e.g., "Dallas, TX").

## Root Cause
In `scripts/data_collection/finnish/fetch.py` line 228, the city was hardcoded as an empty string:
```python
venue_info["city"] = ""  # ← This was the problem!
```

The NHL API schedule endpoint provides venue names but not city information in the game data structure.

## Solution
Implemented a comprehensive **venue-to-city mapping** in the fetch script:

1. **Added VENUE_CITY_MAP dictionary** (lines 17-149 in fetch.py)
   - Maps 100+ NHL venues to their cities/states
   - Includes all current NHL arenas
   - Includes historical venue names
   - Includes international games (Europe)

2. **Updated venue extraction logic** (lines 332-335 in fetch.py)
   - Now looks up city from the mapping
   - Falls back to empty string if venue not found

```python
venue_name = game.get("venue", {}).get("default", "")
venue_info["venue"] = venue_name
venue_info["city"] = VENUE_CITY_MAP.get(venue_name, "")
```

## Example Mappings

| Venue Name | City |
|------------|------|
| American Airlines Center | Dallas, TX |
| TD Garden | Boston, MA |
| Scotiabank Arena | Toronto, ON |
| Bell Centre | Montreal, QC |
| United Center | Chicago, IL |
| Crypto.com Arena | Los Angeles, CA |
| T-Mobile Arena | Las Vegas, NV |
| Ball Arena | Denver, CO |

## Testing

### Before Fix:
```json
{
  "name": "Mikko Rantanen",
  "venue": "American Airlines Center",
  "city": ""  // Empty!
}
```

### After Fix:
```json
{
  "name": "Mikko Rantanen",
  "venue": "American Airlines Center",
  "city": "Dallas, TX"  // Now populated!
}
```

## Impact
- **UI Enhancement**: Players now see both venue and city (e.g., "📍 American Airlines Center — Dallas, TX")
- **Better Context**: Users can immediately see which city the game was played in
- **Professional Look**: Matches real NHL game broadcast graphics

## Files Modified
- `scripts/data_collection/finnish/fetch.py`
  - Added VENUE_CITY_MAP dictionary (100+ entries)
  - Updated venue extraction logic
  - Added `break` statement for efficiency

## Coverage
The mapping includes:
- ✅ All 32 current NHL team arenas
- ✅ Alternate/previous names (e.g., "Staples Center" → "Crypto.com Arena")
- ✅ Historical venues (for past games)
- ✅ International venues (Europe games)
- ✅ Neutral site games
- ✅ AHL/NCAA venues used for neutral games

## Future Enhancements
If new venues are added or renamed:
1. Add entry to VENUE_CITY_MAP
2. Re-fetch affected game dates
3. Mapping will auto-populate city for new games

## Notes
- Venue names must match exactly (case-sensitive)
- If a venue is not in the mapping, city will be empty
- The mapping is comprehensive and covers all NHL venues from 2020-2025
