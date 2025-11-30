# Team Assignment Bug Fix

## 🚨 Bug Summary

**Issue**: Finnish NHL players were being assigned to the wrong teams in the data output.

**Root Cause**: Logic error in `scripts/data_collection/finnish/fetch.py` at line 262.

## 🔍 The Bug

```python
# Line 234: team_side is set to either "awayTeam" or "homeTeam"
for team_side in ["awayTeam", "homeTeam"]:

# Line 262: Code checks for "away" (never matches!)
if team_side == "away":
    player_team = away_team
else:  # Always executes this branch!
    player_team = home_team
```

**Problem**: `team_side` is either `"awayTeam"` or `"homeTeam"`, but the condition checks for `"away"`. This condition NEVER matches, so ALL players were incorrectly assigned to the `home_team`.

## ✅ The Fix

Changed line 262 from:
```python
if team_side == "away":
```

To:
```python
if team_side == "awayTeam":
```

## 📊 Impact

**Affected Dates**: Nov 24-28, 2025 (all game days with Finnish players)

**Wrong Assignments** (Examples):
- Roope Hintz: Assigned to SEA (wrong) → Now: DAL ✓
- Mikko Rantanen: Assigned to SEA (wrong) → Now: DAL ✓
- Miro Heiskanen: Assigned to SEA (wrong) → Now: DAL ✓
- Esa Lindell: Assigned to SEA (wrong) → Now: DAL ✓
- All away team players were assigned to home team

**Correct Assignments** (Examples):
- Erik Haula: NSH (vs DET) ✓
- Sebastian Aho: CAR (vs NYR) ✓
- Anton Lundell: FLA (vs PHI) ✓
- All home team players were correct ✓

## 🔧 Resolution

1. **Fixed** the condition in `fetch.py` line 262
2. **Re-fetched** all affected dates (Nov 24-28)
3. **Verified** team assignments are now correct

## ✅ Verification Command

```bash
# Check team assignments
jq -r '.players[]? | "\(.name): team=\(.team) (vs \(.opponent))"' data/prepopulated/games/2025-11-28.json

# Should show correct teams matching opponents
```

## 📝 Lessons Learned

- **String matching bugs** are easy to miss in production
- **Unit tests** should include verification of team assignments
- **Data validation** should check for team vs opponent consistency
- Always test with both **home** and **away** team players

## 🕒 Timestamps

- **Bug discovered**: 2025-11-29
- **Fix applied**: 2025-11-29
- **Data re-fetched**: 2025-11-29
- **Status**: ✅ RESOLVED
