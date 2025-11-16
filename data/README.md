# Data Directory Structure

This directory contains all data for the Finnish NHL Player Tracker.

## 📁 Directory Structure

```
data/
├── games/                    # 🎯 PRIMARY: Game data by date (SOURCE OF TRUTH)
│   ├── 2024-10-04.json      # Game data for 2024-10-04
│   ├── 2024-10-05.json      # Game data for 2024-10-05
│   └── ...
├── players/                  # 👥 Player-related data
│   ├── finnish-roster.json   # Master list of Finnish NHL players
│   └── player-changes.json   # Track player roster changes
├── reports/                  # 📊 Processing and maintenance reports
│   ├── cleaning-report.json # Data cleaning logs
│   └── refresh-report.json  # Data refresh logs
└── backups/                  # 💾 Version history and backups
    └── finnish-nhl-players-*.json
```

## 🎯 Single Source of Truth

- **`data/games/`** - The ONLY location for game data by date
- All other directories reference this data
- Build process copies from here to `static/data/`
- No duplicate data maintenance needed

## 📋 File Formats

### Game Data (`games/YYYY-MM-DD.json`)
```json
[
  {
    "name": "Mikael Granlund",
    "team": "ANA",
    "team_full": "Anaheim Ducks",
    "position": "C",
    "goals": 1,
    "assists": 1,
    "points": 2,
    "opponent": "EDM",
    "opponent_full": "Edmonton Oilers",
    "game_score": "4-3",
    "game_result": "W"
  }
]
```

### Player Roster (`players/finnish-roster.json`)
```json
[
  {
    "id": 8475798,
    "name": "Mikael Granlund",
    "firstName": "Mikael",
    "lastName": "Granlund",
    "position": "C",
    "team": "ANA",
    "teamName": "Anaheim Ducks",
    "sweaterNumber": 64,
    "birthDate": "1992-02-26",
    "birthCity": "Oulu",
    "birthCountry": "FIN",
    "nationality": "FIN",
    "shoots": "L",
    "height": "5'10\"",
    "weight": 179,
    "isActive": true
  }
]
```

## 🔄 Data Flow

1. **Source**: Raw NHL data → `data/games/`
2. **Processing**: Game data → Finnish player extraction → Game files
3. **Build**: `data/games/` → `static/data/` (for serving)
4. **Runtime**: `static/data/` → Browser cache → User

## 🛠️ Maintenance

- Add new game data to `data/games/`
- Update player roster in `data/players/finnish-roster.json`
- Run build to update `static/data/`
- Backup important data to `data/backups/`

## 📈 Benefits

✅ Single source of truth for game data
✅ No duplicate data maintenance
✅ Clear separation of concerns
✅ Easy backup and version control
✅ Simplified build process
✅ Better organization and findability