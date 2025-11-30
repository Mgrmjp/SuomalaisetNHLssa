# Player Headshots

Downloads and creates thumbnail images for NHL players.

## 📁 Files

### `fetch_thumbnails.py`
Fetches Finnish NHL player headshots and creates thumbnails.

**Usage:**
```bash
# Download all Finnish player headshots
python3 scripts/data_collection/headshots/fetch_thumbnails.py

# Creates 40x40px JPEGs
# Saves to: static/headshots/thumbs/{playerId}.jpg
```

**Features:**
- ✅ Downloads Finnish players only (from roster data)
- ✅ Resizes to 40x40px thumbnails
- ✅ JPEG format (65% quality)
- ✅ Saves to `static/headshots/thumbs/`

**Requirements:**
```bash
pip install Pillow
```
If Pillow not installed, saves original PNGs (not resized).

## 📊 Process

1. **Fetch Rosters:** Gets all 32 team rosters
2. **Filter Finnish:** Identifies Finnish players
3. **Download Images:** Fetches headshot from NHL CDN
4. **Resize:** Creates 40x40px thumbnails
5. **Save:** Stores in `static/headshots/thumbs/`

## 📁 Output Structure

```
static/
└── headshots/
    └── thumbs/
        ├── 8478427.jpg  # Sebastian Aho
        ├── 8475287.jpg  # Erik Haula
        ├── 8478420.jpg  # Mikko Rantanen
        └── ... (34 players)
```

## 📝 Image Details

**Format:** JPEG (if Pillow installed)
**Size:** 40x40 pixels
**Quality:** 65%
**Source:** NHL CDN (https://assets.nhle.com/mugs/nhl)

**Without Pillow:**
- Format: PNG (original)
- Size: Original (not resized)
- Quality: 100%

## 🏆 Current Status (2025-11-22)

- **Finnish Players:** 34 active
- **Expected Images:** 34 thumbnails
- **Source:** Current team rosters
- **Cache:** Based on current Finnish cache

## ⚙️ How It Works

**Step 1: Get Rosters**
```python
for team in TEAM_ABBREVS:
    roster = fetch_json(f"{NHL_API}/v1/roster/{team}/current")
    players = forwards + defensemen + goalies
```

**Step 2: Filter Finnish**
```python
if is_finnish(player):
    finnish_players.append({
        "team": team,
        "id": player["id"],
        "name": player["fullName"]
    })
```

**Step 3: Download & Resize**
```python
image = Image.open(io.BytesIO(data))
image = image.resize((40, 40), Image.LANCZOS)
image.save(out_path, format="JPEG", quality=65)
```

## 📊 Example Output

```
Finnish players found: 34
Thumbs saved: 34 -> /home/miikka/dev/suomalaisetnhlssa/static/headshots/thumbs
```

## 🔧 Troubleshooting

### "Pillow not installed"
```bash
pip install Pillow
```
Then re-run to get resized thumbnails.

### "thumb failed for player"
- Player may not have headshot
- Network timeout
- Player changed teams

### "roster failed for team"
- API error for specific team
- Script continues with other teams

## 📈 Performance

- **Time:** ~2-3 minutes (34 players)
- **Rate Limit:** 0.5s between downloads
- **Success Rate:** ~95% (32-34 of 34)
- **File Size:** ~2KB per thumbnail

## 🎯 Use Cases

### Web Applications
```html
<img src="/static/headshots/thumbs/8478427.jpg"
     alt="Sebastian Aho"
     width="40" height="40">
```

### Player Cards
- Avatar images
- Team rosters
- Player profiles

## 🔄 Update Frequency

Run when:
- ✅ New Finnish players join NHL
- ✅ Player changes teams
- ✅ Start of new season

**Note:** Uses current roster data, not cached player list

## 📝 Dependencies

- Python 3.9+
- `requests` (for downloading images)
- `Pillow` (optional, for resizing)

Install:
```bash
pip install requests Pillow
```

---

**Status:** ✅ Working (2025-11-22)
**Finnish Players:** 34
**Expected Output:** 34 thumbnails
**Path:** `static/headshots/thumbs/`
