# Finnish Name Correction

## Overview

This feature automatically corrects Finnish letter patterns (ä, ö, å) in player names fetched from the NHL API. The NHL API often returns names with ASCII approximations (e.g., "Teravainen" instead of "Teräväinen"), which are corrected during server-side rendering.

## Problem

The NHL stats API (`api.nhle.com/stats/rest/`) returns Finnish names without proper Finnish characters:
- "Teravainen" → should be "Teräväinen"
- "Puljujarvi" → should be "Puljujärvi"
- "Raty" → should be "Räty"

## Solution

A server-side utility (`src/lib/utils/finnishNameUtils.js`) applies pattern-based corrections to Finnish names during the SvelteKit build process (static site generation).

## Implementation

### Files

1. **`src/lib/utils/finnishNameUtils.js`** - Core correction logic
   - `correctFinnishName(name)` - Corrects a single name
   - `correctFullName(fullName)` - Corrects full name (first + last)
   - `correctPlayerNames(players)` - Batch correction for player arrays

2. **`src/routes/pisteporssi/+page.server.js`** - Stats leaderboard page
   - Applies corrections to `skaterFullName` field

3. **`src/routes/pelaajat/+page.server.js`** - Player list page
   - Applies corrections to both `skaterFullName` and `goalieFullName` fields

### Correction Patterns

The utility uses two approaches:

1. **Lookup table** - Exact matches for known incorrect spellings
2. **Pattern matching** - Regex-based correction for common patterns

Example patterns:
- `Parssinen` → `Pärssinen` (aa + nen → ää)
- `Raty` → `Räty` (specific case)
- `Teravainen` → `Teräväinen` (known misspelling)

## Why Server-Side?

Since this project uses `adapter-static` for static site generation:
- Pages are pre-rendered at build time
- Corrections happen once during build, not on every request
- The corrected names are baked into the static HTML

## Future Improvements

- Integration with OpenAI API for more comprehensive corrections (see `scripts/data_collection/finnish/finnish_text_utils.py`)
- Expand correction patterns for more Finnish names
- Add support for city names and birthplaces

## Related Files

- `scripts/data_collection/finnish/finnish_text_utils.py` - Python OpenAI-based correction used in data collection scripts
