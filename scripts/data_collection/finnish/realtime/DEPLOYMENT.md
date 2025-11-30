# Real-Time NHL Monitor - Deployment Guide

## 🚀 Quick Start

### 1. Verify Installation

```bash
# Navigate to realtime directory
cd scripts/data_collection/finnish/realtime

# Run integration tests
./test_integration.py

# Run demonstration
./demo.py
```

### 2. Install Systemd Service

```bash
# Make management script executable
chmod +x manage.sh

# Install and start service
sudo ./manage.sh install
sudo ./manage.sh start

# Check status
sudo ./manage.sh status
```

### 3. Monitor Logs

```bash
# View real-time logs
sudo ./manage.sh logs

# Or use journalctl
sudo journalctl -u nhl-realtime -f
```

## 📋 Full Deployment Checklist

### Pre-Deployment
- [ ] Integration tests pass (7/7)
- [ ] NHL API connectivity verified
- [ ] Finnish player cache exists (34 players)
- [ ] Management script is executable
- [ ] Working directory is correct

### Service Installation
- [ ] Copy systemd service file
- [ ] Reload systemd daemon
- [ ] Enable service (auto-start on boot)
- [ ] Start service
- [ ] Verify service is running

### Post-Deployment Verification
- [ ] Service status shows "active (running)"
- [ ] Logs show "Real-time monitor started"
- [ ] State file created: `state/active_games.json`
- [ ] Log file created: `logs/realtime_monitor.log`
- [ ] No errors in logs

## 🔧 Manual Service Management

### Control Service

```bash
# Start service
sudo systemctl start nhl-realtime

# Stop service
sudo systemctl stop nhl-realtime

# Restart service
sudo systemctl restart nhl-realtime

# Check status
sudo systemctl status nhl-realtime

# Enable auto-start
sudo systemctl enable nhl-realtime

# Disable auto-start
sudo systemctl disable nhl-realtime
```

### View Logs

```bash
# Systemd journal (recommended)
sudo journalctl -u nhl-realtime -f
sudo journalctl -u nhl-realtime --since "1 hour ago"
sudo journalctl -u nhl-realtime -n 100

# Log file
tail -f scripts/data_collection/finnish/realtime/logs/realtime_monitor.log
grep "ERROR" scripts/data_collection/finnish/realtime/logs/realtime_monitor.log
```

## 📊 Monitoring & Debugging

### Check System Status

```bash
# View state manager stats
python3 -c "
from scripts.data_collection.finnish.realtime.state_manager import GameStateManager
mgr = GameStateManager()
print(mgr.get_stats())
"

# View live games
python3 -c "
from scripts.data_collection.finnish.realtime.state_manager import GameStateManager
mgr = GameStateManager()
for game in mgr.get_live_games():
    print(f\"Game {game['game_id']}: {game['away_team']} @ {game['home_team']} ({game['game_state']})\")
"
```

### Test NHL API

```bash
# Test schedule endpoint
curl "https://api-web.nhle.com/v1/schedule/$(date +%Y-%m-%d)"

# Test boxscore endpoint (replace with actual game ID)
curl "https://api-web.nhle.com/v1/gamecenter/2025020335/boxscore"
```

### Check Data Files

```bash
# Verify JSON files are being updated
ls -la data/prepopulated/games/

# Check if real-time fields are added
jq '.games[0].realtime' data/prepopulated/games/2025-11-22.json

# Count Finnish players
jq '.total_players' data/prepopulated/games/2025-11-22.json
```

## 🛠️ Configuration

### Modify Settings

Edit `realtime_config.json`:

```json
{
  "monitoring": {
    "state_check_interval": 60,        // Check for new games every 60s
    "live_game_update_interval": 30,    // Update live games every 30s
    "max_concurrent_updates": 5
  },
  "api": {
    "base_url": "https://api-web.nhle.com",
    "request_timeout": 10,
    "retry_attempts": 2,
    "rate_limit_delay": 0.5
  },
  "logging": {
    "level": "INFO",                    // DEBUG, INFO, WARNING, ERROR
    "console_output": true
  }
}
```

### Apply Changes

```bash
# Restart service to apply new configuration
sudo systemctl restart nhl-realtime
```

## 🔍 Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status nhl-realtime

# View error logs
sudo journalctl -u nhl-realtime -n 50

# Run manually to see errors
python3 scripts/data_collection/finnish/realtime/realtime_monitor.py

# Check file permissions
ls -la scripts/data_collection/finnish/realtime/
```

### No Live Games Detected

```bash
# Verify NHL API is accessible
curl "https://api-web.nhle.com/v1/schedule/$(date +%Y-%m-%d)"

# Check state manager
python3 -c "from state_manager import GameStateManager; print(GameStateManager().get_stats())"

# Check if games are actually scheduled today
curl "https://api-web.nhle.com/v1/schedule/$(date +%Y-%m-%d)" | jq '.gameWeek[].games | length'
```

### Data Not Updating

```bash
# Verify Finnish player cache exists
ls -la scripts/data_collection/finnish/cache/finnish-players.json

# Check data file permissions
ls -la data/prepopulated/games/

# Manually test data updater
python3 -c "
from data_updater import DataUpdater
updater = DataUpdater()
print(f'Data dir: {updater.DATA_DIR}')
print(f'Exists: {updater.DATA_DIR.exists()}')
"

# Check for errors in logs
grep "ERROR" scripts/data_collection/finnish/realtime/logs/realtime_monitor.log | tail -20
```

### High Resource Usage

```bash
# Check CPU and memory usage
top -p $(pgrep -f realtime_monitor)

# Check network activity
sudo netstat -p | grep realtime_monitor

# Count API requests
grep "API request" scripts/data_collection/finnish/realtime/logs/realtime_monitor.log | wc -l
```

### Logs Filling Up

```bash
# Check log file size
ls -lh scripts/data_collection/finnish/realtime/logs/

# Rotate logs manually
mv scripts/data_collection/finnish/realtime/logs/realtime_monitor.log scripts/data_collection/finnish/realtime/logs/realtime_monitor.log.1

# Restart service
sudo systemctl restart nhl-realtime
```

## 🔒 Security

### Service Security

The systemd service runs with security hardening:

```ini
[Service]
NoNewPrivileges=true    # Prevent privilege escalation
PrivateTmp=true         # Isolated temp directory
ProtectSystem=strict    # Read-only system directories
ProtectHome=true        # Protected home directories
ReadWritePaths=/home/miikka/dev/suomalaisetnhlssa/data/prepopulated/games
ReadWritePaths=/home/miikka/dev/suomalaisetnhlssa/scripts/data_collection/finnish/realtime
```

### Access Control

```bash
# Check service user
sudo systemctl show nhl-realtime | grep User

# Verify file permissions
ls -la scripts/data_collection/finnish/realtime/
```

## 📈 Performance Tuning

### Optimize Polling Intervals

For high-traffic game days:
```json
{
  "monitoring": {
    "state_check_interval": 30,        // Faster state checks
    "live_game_update_interval": 15    // More frequent updates
  }
}
```

For normal operation:
```json
{
  "monitoring": {
    "state_check_interval": 60,        // Default
    "live_game_update_interval": 30    // Default
  }
}
```

### Reduce API Load

```json
{
  "api": {
    "rate_limit_delay": 1.0  // Increase delay between requests
  }
}
```

## 🔄 Backup & Recovery

### Backup State

```bash
# Backup active games state
cp scripts/data_collection/finnish/realtime/state/active_games.json \
   backups/active_games_$(date +%Y%m%d).json

# Backup configuration
cp scripts/data_collection/finnish/realtime/realtime_config.json \
   backups/realtime_config_$(date +%Y%m%d).json
```

### Restore State

```bash
# Stop service
sudo systemctl stop nhl-realtime

# Restore state
cp backups/active_games_20251122.json \
   scripts/data_collection/finnish/realtime/state/active_games.json

# Start service
sudo systemctl start nhl-realtime
```

### Disaster Recovery

If system is completely down:

1. **Reinstall service**:
   ```bash
   sudo ./manage.sh install
   sudo ./manage.sh start
   ```

2. **Restore from backups**:
   ```bash
   # Restore configuration
   cp backups/realtime_config_*.json realtime_config.json
   sudo systemctl restart nhl-realtime
   ```

3. **Verify recovery**:
   ```bash
   sudo ./manage.sh status
   sudo ./manage.sh logs
   ```

## 📞 Support

### Getting Help

1. **Check logs first**:
   ```bash
   sudo journalctl -u nhl-realtime -n 100
   ```

2. **Run diagnostics**:
   ```bash
   ./test_integration.py
   ./manage.sh status
   ```

3. **Check NHL API status**:
   ```bash
   curl "https://api-web.nhle.com/v1/schedule/$(date +%Y-%m-%d)"
   ```

4. **Common issues**:
   - Service won't start: Check logs and permissions
   - No live games: Verify NHL API and game schedule
   - Data not updating: Check cache and file permissions
   - High resource usage: Adjust polling intervals

### Log Locations

- **Systemd journal**: `sudo journalctl -u nhl-realtime`
- **Log file**: `scripts/data_collection/finnish/realtime/logs/realtime_monitor.log`
- **State file**: `scripts/data_collection/finnish/realtime/state/active_games.json`
- **Error log**: `scripts/data_collection/finnish/realtime/logs/error.log`

### Quick Commands Reference

```bash
# Service management
sudo systemctl start nhl-realtime
sudo systemctl stop nhl-realtime
sudo systemctl restart nhl-realtime
sudo systemctl status nhl-realtime

# Logging
sudo journalctl -u nhl-realtime -f
tail -f scripts/data_collection/finnish/realtime/logs/realtime_monitor.log

# Testing
./test_integration.py
./demo.py
./manage.sh test

# Configuration
cat realtime_config.json
jq . realtime_config.json

# Data verification
jq '.total_players' data/prepopulated/games/$(date +%Y-%m-%d).json
```

## ✅ Success Criteria

Deployment is successful when:

- [ ] Service status: `active (running)`
- [ ] No errors in logs
- [ ] State file exists and is updated
- [ ] Log file is created and being written to
- [ ] Live games are detected
- [ ] Finnish player data is updating
- [ ] API requests are successful
- [ ] Resource usage is normal (< 10% CPU, < 50MB RAM)

## 📅 Maintenance Schedule

### Daily
- Check service status
- Review logs for errors

### Weekly
- Check disk usage (logs)
- Verify API connectivity
- Test backup procedure

### Monthly
- Review configuration
- Update documentation
- Performance optimization

### On Game Days
- Monitor logs closely
- Watch for live game detection
- Verify data updates

---

## 🎉 Deployment Complete!

Your real-time NHL Finnish player monitoring system is now live!

**Next Steps:**
1. Monitor the service during the next game day
2. Verify live game detection works
3. Confirm data updates are occurring
4. Set up monitoring alerts (optional)

**Quick Links:**
- Service management: `./manage.sh`
- View logs: `sudo journalctl -u nhl-realtime -f`
- Documentation: `README.md`
- Configuration: `realtime_config.json`
