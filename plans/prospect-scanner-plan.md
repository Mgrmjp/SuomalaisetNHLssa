# Prospect Scanner - Data Sources Expansion Plan

## Current State

The project already has multiple data source implementations, but they may not all be working or integrated:

### Already Implemented:
| Source | Status | Notes |
|--------|--------|-------|
| EliteProspects scraper | ✅ Working | Supports 25+ leagues |
| AHL API (HockeyTech) | ✅ Working | Real AHL data |
| NHL API | ✅ Working | Used for current NHL players |
| Liiga API | ⚠️ May need fixing | Has adapter code |
| SHL API | ⚠️ May need fixing | Has adapter code |
| KHL API | ⚠️ May need fixing | Has adapter code |
| API-Hockey | ⚠️ Needs API key | 100 req/day free tier |
| HockeyDB scraper | ⚠️ Partial | Only Liiga, SHL |

### Missing / Needs Work:
- NCAA (College hockey) - needs integration
- US Juniors (USHL, NAHL) - limited coverage
- Canadian Juniors (WHL, OHL, QMJHL) - limited coverage
- Unified data collection system

---

## Proposed Implementation Plan

### Phase 1: Fix and Test Existing Collectors
- [ ] Test AHL API collector
- [ ] Test Liiga API collector  
- [ ] Test SHL API collector
- [ ] Test KHL API collector
- [ ] Fix any broken league adapters

### Phase 2: Add New Data Sources
- [ ] Add NCAA data collection (collegehockeynews.com API)
- [ ] Add Canadian Junior leagues (WHL, OHL, QMJHL)
- [ ] Add US Junior leagues (USHL, NAHL)
- [ ] Add KHL data collection (if not working)

### Phase 3: Create Unified Collection System
- [ ] Create multi-source collector that combines all sources
- [ ] Deduplicate players across sources
- [ ] Add data source tracking

### Phase 4: Run and Update Data
- [ ] Run collection for current season
- [ ] Update static/data/leagues/ with fresh data
- [ ] Verify data in frontend

---

## Data Sources to Add

### Priority 1 (High Value):
1. **NCAA** - Many Finnish prospects play college hockey
2. **Canadian Juniors (WHL, OHL, QMJHL)** - Major source of NHL prospects
3. **USHL** - Top US junior league

### Priority 2 (Medium Value):
4. **KHL** - Russian league with Finnish players
5. **DEL** - German league
6. **Swiss NL** - Swiss league

### Priority 3 (Nice to Have):
7. **Czech Extraliga**
8. **Slovak Extraliga**
9. **ICEHL** (Austria/Italy/Hungary/Slovenia)

---

## Technical Approach

### 1. Use EliteProspects as Primary (Already Working)
The EliteProspects scraper already covers most leagues. Focus on:
- Running it to get fresh data
- Fixing any broken league scraping

### 2. Add League-Specific APIs Where Available
- **NCAA**: Use collegehockeynews.com API
- **AHL**: Already working via HockeyTech API
- **Liiga/SHL/KHL**: Fix existing adapters

### 3. Create Unified Collector
```python
class UnifiedProspectCollector:
    """Collect from all sources and deduplicate"""
    
    def collect_all(self):
        # 1. EliteProspects (main source)
        # 2. AHL API (supplement)
        # 3. League APIs (where available)
        # 4. Deduplicate by name + birthdate
        # 5. Return unified list
```

---

## Next Steps

1. **Decide which leagues to prioritize** - Which are most important for Finnish prospects?
2. **Test existing collectors** - Run them to see what works
3. **Add missing sources** - Implement new collectors for missing leagues
4. **Run collection** - Get fresh data
5. **Update frontend** - Display new data

---

## Commands to Run

```bash
# Test existing EliteProspects scraper
npm run prospects:scrape

# Build prospects cache
npm run prospects:cache:build

# Update all league data
npm run prospects:leagues:update
```
