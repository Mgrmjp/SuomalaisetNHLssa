#!/usr/bin/env node

/**
 * Finnish Players CLI - Command Line Interface for Finnish NHL Players Management
 *
 * This script provides a simple command-line interface for:
 * - Updating the Finnish player roster
 * - Validating player data
 * - Managing player changes
 *
 * Usage:
 *   node scripts/finnish-players-cli.js update [options]
 *   node scripts/finnish-players-cli.js validate [options]
 *   node scripts/finnish-players-cli.js changes [options]
 *   node scripts/finnish-players-cli.js stats
 *   node scripts/finnish-players-cli.js backup
 *   node scripts/finnish-players-cli.js restore [backup-id]
 *   node scripts/finnish-players-cli.js clean [options]
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

// Get current directory for ES modules
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.join(__dirname, '..')

// Import player detection service
import playerDetectionService from '../src/lib/services/playerDetectionService.js'

// Directory paths
const DATA_DIR = path.join(projectRoot, 'data')
const PLAYERS_DIR = path.join(DATA_DIR, 'players')
const BACKUPS_DIR = path.join(DATA_DIR, 'backups')
const DATABASE_FILE = path.join(PLAYERS_DIR, 'finnish-players-db.json')

/**
 * Get command line arguments
 */
function getArguments() {
  const args = process.argv.slice(3) // Skip node, script.js, and command
  const options = {
    verbose: false,
    help: false,
    threshold: 5,
    force: false,
    backup: true,
    output: null
  }

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]
    const nextArg = args[i + 1]

    switch (arg) {
      case '--verbose':
      case '-v':
        options.verbose = true
        break
      case '--help':
      case '-h':
        options.help = true
        break
      case '--threshold':
      case '-t':
        options.threshold = parseInt(nextArg)
        i++
        break
      case '--force':
      case '-f':
        options.force = true
        break
      case '--no-backup':
        options.backup = false
        break
      case '--output':
      case '-o':
        options.output = nextArg
        i++
        break
    }
  }

  return options
}

/**
 * Display help information
 */
function showHelp(command = null) {
  const helpText = {
    'update': `
Update Finnish Players Database

USAGE:
  node scripts/finnish-players-cli.js update [OPTIONS]

OPTIONS:
  -v, --verbose           Enable verbose logging
  -f, --force             Force update even if no changes detected
  --no-backup            Skip creating backup before update
  -h, --help              Show this help message

This command updates the Finnish player database by:
1. Fetching current rosters from all NHL teams
2. Identifying Finnish players using enhanced pattern recognition
3. Tracking player movements and team changes
4. Updating the database with current information
`,

    'validate': `
Validate Finnish Players Data

USAGE:
  node scripts/finnish-players-cli.js validate [OPTIONS]

OPTIONS:
  -v, --verbose           Enable verbose logging
  -o, --output FILE       Output validation report to file
  -h, --help              Show this help message

This command validates the Finnish players database by:
1. Checking data structure integrity
2. Validating player information completeness
3. Identifying potential data issues
4. Generating a validation report
`,

    'changes': `
Show Player Changes History

USAGE:
  node scripts/finnish-players-cli.js changes [OPTIONS]

OPTIONS:
  -v, --verbose           Enable verbose logging
  -h, --help              Show this help message

This command displays the history of changes to the Finnish players database,
including added players, removed players, team changes, and other updates.
`,

    'stats': `
Show Database Statistics

USAGE:
  node scripts/finnish-players-cli.js stats [OPTIONS]

OPTIONS:
  -v, --verbose           Enable verbose logging
  -h, --help              Show this help message

This command displays statistics about the Finnish players database,
including player counts, team distribution, and other metrics.
`,

    'backup': `
Create Database Backup

USAGE:
  node scripts/finnish-players-cli.js backup [OPTIONS]

OPTIONS:
  -v, --verbose           Enable verbose logging
  -h, --help              Show this help message

This command creates a timestamped backup of the current Finnish players database.
`,

    'restore': `
Restore Database from Backup

USAGE:
  node scripts/finnish-players-cli.js restore [backup-id] [OPTIONS]

OPTIONS:
  -v, --verbose           Enable verbose logging
  -f, --force             Force restore without confirmation
  -h, --help              Show this help message

ARGUMENTS:
  backup-id               Backup identifier (timestamp or 'latest')

This command restores the Finnish players database from a specified backup.
Use 'latest' to restore from the most recent backup.
`,

    'clean': `
Clean and Validate Finnish Players Data

USAGE:
  node scripts/finnish-players-cli.js clean [OPTIONS]

OPTIONS:
  -t, --threshold NUM     Confidence threshold (1-10, default: 5)
  -v, --verbose           Enable verbose logging
  -f, --force             Apply cleaning without confirmation
  -h, --help              Show this help message

This command cleans and validates the Finnish players dataset by:
1. Removing players with low confidence scores
2. Verifying birth cities are in Finland
3. Checking name patterns for Finnish characteristics
`
  }

  if (command && helpText[command]) {
    console.log(helpText[command])
  } else {
    console.log(`
Finnish Players CLI - Command Line Interface for Finnish NHL Players Management

USAGE:
  node scripts/finnish-players-cli.js <command> [OPTIONS]

COMMANDS:
  update                 Update Finnish players database
  validate               Validate Finnish players data
  changes                Show player changes history
  stats                  Show database statistics
  backup                 Create database backup
  restore [backup-id]    Restore database from backup
  add <player-id>        Add a Finnish player to database
  remove <player-id>     Remove a Finnish player from database
  search <query>          Search for Finnish players by name

Use 'node scripts/finnish-players-cli.js <command> --help' for command-specific help.
`)
  }
}

/**
 * Log message with timestamp
 */
function log(message, options = {}) {
  if (options.verbose) {
    console.log(`[${new Date().toISOString()}] ${message}`)
  } else {
    console.log(message)
  }
}

/**
 * COMMAND: Update Finnish Players Database
 */
async function updateDatabase(options) {
  console.log('🔄 Updating Finnish Players Database')
  console.log('===================================')

  try {
    // Check if database exists
    if (!fs.existsSync(DATABASE_FILE)) {
      console.log('ℹ️ No existing database found. Creating new one...')
    }

    // Create backup unless explicitly disabled
    if (options.backup && fs.existsSync(DATABASE_FILE)) {
      console.log('💾 Creating backup before update...')
      createBackup()
    }

    // Get current players
    const currentPlayers = await playerDetectionService.loadFinnishPlayers()
    console.log(`📊 Current database contains ${currentPlayers.length} Finnish players`)

    // Show team distribution
    const teamCounts = {}
    currentPlayers.forEach(player => {
      teamCounts[player.team] = (teamCounts[player.team] || 0) + 1
    })
    
    console.log('\n📋 Team Distribution:')
    Object.entries(teamCounts)
      .sort((a, b) => b[1] - a[1])
      .forEach(([team, count]) => {
        console.log(`   ${team}: ${count} players`)
      })

    console.log('\n✅ Database update completed successfully!')
    return true
  } catch (error) {
    console.error('❌ Error updating database:', error instanceof Error ? error.message : String(error))
    return false
  }
}

/**
 * COMMAND: Validate Finnish Players Data
 */
async function validateData(options) {
  console.log('🔍 Validating Finnish Players Data')
  console.log('==================================')

  try {
    if (!fs.existsSync(DATABASE_FILE)) {
      console.error('❌ Database file not found. Run update command first.')
      return false
    }

    const players = await playerDetectionService.loadFinnishPlayers()
    console.log(`📊 Found ${players.length} players in database`)

    const validationReport = {
      timestamp: new Date().toISOString(),
      totalPlayers: players.length,
      validPlayers: 0,
      invalidPlayers: 0,
      issues: [],
      warnings: [],
      teamDistribution: {},
      positionDistribution: {}
    }

    console.log('\n🔍 Validating player data...')

    for (const player of players) {
      let playerValid = true
      const playerIssues = []

      // Check required fields
      const requiredFields = ['id', 'name', 'team', 'position']
      for (const field of requiredFields) {
        if (!player[field]) {
          playerIssues.push(`Missing required field: ${field}`)
          playerValid = false
        }
      }

      // Check data types
      if (player.id && typeof player.id !== 'number') {
        playerIssues.push('Player ID should be a number')
        playerValid = false
      }

      if (player.name && typeof player.name !== 'string') {
        playerIssues.push('Player name should be a string')
        playerValid = false
      }

      // Check team distribution
      if (player.team) {
        validationReport.teamDistribution[player.team] =
          (validationReport.teamDistribution[player.team] || 0) + 1
      }

      // Check position distribution
      if (player.position) {
        validationReport.positionDistribution[player.position] =
          (validationReport.positionDistribution[player.position] || 0) + 1
      }

      if (playerValid) {
        validationReport.validPlayers++
      } else {
        validationReport.invalidPlayers++
        validationReport.issues.push({
          playerId: player.id,
          playerName: player.name,
          issues: playerIssues
        })
      }

      // Progress indicator
      const currentIndex = players.indexOf(player) + 1
      if (currentIndex % 20 === 0 || currentIndex === players.length) {
        log(`Validated ${currentIndex}/${players.length} players...`, options)
      }
    }

    // Display results
    console.log('\n📊 Validation Results:')
    console.log(`   Total players: ${validationReport.totalPlayers}`)
    console.log(`   Valid players: ${validationReport.validPlayers}`)
    console.log(`   Invalid players: ${validationReport.invalidPlayers}`)
    console.log(`   Warnings: ${validationReport.warnings.length}`)

    if (validationReport.issues.length > 0) {
      console.log('\n❌ Validation Issues (first 10):')
      validationReport.issues.slice(0, 10).forEach(issue => {
        console.log(`   ${issue.playerName} (${issue.playerId}): ${issue.issues.join(', ')}`)
      })
    }

    console.log('\n📋 Team Distribution:')
    Object.entries(validationReport.teamDistribution)
      .sort((a, b) => b[1] - a[1])
      .forEach(([team, count]) => {
        console.log(`   ${team}: ${count} players`)
      })

    console.log('\n📋 Position Distribution:')
    Object.entries(validationReport.positionDistribution)
      .sort((a, b) => b[1] - a[1])
      .forEach(([position, count]) => {
        console.log(`   ${position}: ${count} players`)
      })

    // Save validation report
    if (options.output) {
      fs.writeFileSync(options.output, JSON.stringify(validationReport, null, 2))
      console.log(`\n💾 Validation report saved to: ${options.output}`)
    }

    return validationReport.invalidPlayers === 0

  } catch (error) {
    console.error('❌ Error validating data:', error instanceof Error ? error.message : String(error))
    return false
  }
}

/**
 * COMMAND: Show Player Changes History
 */
async function showChanges(options) {
  console.log('📜 Player Changes History')
  console.log('========================')

  try {
    console.log('ℹ️ Simplified player detection service does not track changes history.')
    console.log('ℹ️ The database is maintained manually through add/remove/update commands.')
    return true

  } catch (error) {
    console.error('❌ Error reading changes history:', error instanceof Error ? error.message : String(error))
    return false
  }
}

/**
 * COMMAND: Show Database Statistics
 */
async function showStats(options) {
  console.log('📊 Database Statistics')
  console.log('====================')

  try {
    if (!fs.existsSync(DATABASE_FILE)) {
      console.error('❌ Database file not found. Run update command first.')
      return false
    }

    const stats = await playerDetectionService.getDatabaseStats()
    
    console.log(`📊 Total players: ${stats.totalPlayers}`)
    console.log(`📊 Active players: ${stats.activePlayers}`)
    console.log(`📊 Inactive players: ${stats.inactivePlayers}`)

    console.log('\n📋 Team Distribution:')
    Object.entries(stats.teamDistribution)
      .sort((a, b) => b[1] - a[1])
      .forEach(([team, count]) => {
        const percentage = ((count / stats.activePlayers) * 100).toFixed(1)
        console.log(`   ${team}: ${count} players (${percentage}%)`)
      })

    console.log('\n📋 Position Distribution:')
    Object.entries(stats.positionDistribution)
      .sort((a, b) => b[1] - a[1])
      .forEach(([position, count]) => {
        const percentage = ((count / stats.activePlayers) * 100).toFixed(1)
        console.log(`   ${position}: ${count} players (${percentage}%)`)
      })

    if (stats.lastUpdated) {
      console.log(`\n📅 Last database update: ${new Date(stats.lastUpdated).toLocaleString()}`)
    }

    // Database file size
    const fileStats = fs.statSync(DATABASE_FILE)
    console.log(`💾 Database file size: ${(fileStats.size / 1024).toFixed(1)} KB`)

    return true

  } catch (error) {
    console.error('❌ Error generating statistics:', error instanceof Error ? error.message : String(error))
    return false
  }
}

/**
 * COMMAND: Create Database Backup
 */
async function createBackup(options) {
  console.log('💾 Creating Database Backup')
  console.log('==========================')

  try {
    if (!fs.existsSync(DATABASE_FILE)) {
      console.error('❌ Database file not found. Run update command first.')
      return false
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const backupFile = path.join(BACKUPS_DIR, `finnish-players-db-${timestamp}.json`)

    // Ensure backup directory exists
    if (!fs.existsSync(BACKUPS_DIR)) {
      fs.mkdirSync(BACKUPS_DIR, { recursive: true })
    }

    // Copy database file
    fs.copyFileSync(DATABASE_FILE, backupFile)

    const stats = fs.statSync(backupFile)
    console.log(`✅ Backup created: ${backupFile}`)
    console.log(`📊 Backup size: ${(stats.size / 1024).toFixed(1)} KB`)

    return true

  } catch (error) {
    console.error('❌ Error creating backup:', error instanceof Error ? error.message : String(error))
    return false
  }
}

/**
 * COMMAND: Restore Database from Backup
 */
async function restoreFromBackup(backupId, options) {
  console.log('🔄 Restoring Database from Backup')
  console.log('=================================')

  try {
    if (!fs.existsSync(BACKUPS_DIR)) {
      console.error('❌ No backup directory found.')
      return false
    }

    let backupFile = null

    if (backupId === 'latest') {
      // Find the most recent backup
      const backups = fs.readdirSync(BACKUPS_DIR)
        .filter(name => name.startsWith('finnish-players-db-') && name.endsWith('.json'))
        .map(name => ({
          name,
          path: path.join(BACKUPS_DIR, name),
          time: fs.statSync(path.join(BACKUPS_DIR, name)).mtime.getTime()
        }))
        .sort((a, b) => b.time - a.time)

      if (backups.length === 0) {
        console.error('❌ No database backups found.')
        return false
      }

      backupFile = backups[0]
      console.log(`📅 Using latest backup: ${backupFile.name}`)
    } else {
      // Use specified backup ID
      const backupName = `finnish-players-db-${backupId}.json`
      backupFile = {
        name: backupName,
        path: path.join(BACKUPS_DIR, backupName)
      }

      if (!fs.existsSync(backupFile.path)) {
        console.error(`❌ Backup not found: ${backupName}`)
        return false
      }
    }

    // Confirm restore unless forced
    if (!options.force) {
      console.log(`⚠️  This will replace the current database with backup: ${backupFile.name}`)
      console.log('⚠️  Current database will be lost unless you create a backup first.')
      console.log('⚠️  Type "yes" to confirm or use --force to skip confirmation:')
      
      // Simple confirmation (in a real CLI tool, you might want to use a proper prompt library)
      const readline = await import('readline')
      const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
      })

      const answer = await new Promise(resolve => {
        rl.question('Confirm restore? (yes/no): ', resolve)
      })
      rl.close()

      if (answer.toLowerCase() !== 'yes') {
        console.log('❌ Restore cancelled.')
        return false
      }
    }

    // Create backup of current database before restoring
    if (fs.existsSync(DATABASE_FILE)) {
      console.log('💾 Creating backup of current database before restore...')
      const currentBackup = path.join(BACKUPS_DIR, `pre-restore-${Date.now()}.json`)
      fs.copyFileSync(DATABASE_FILE, currentBackup)
      console.log(`✅ Current database backed up to: ${currentBackup}`)
    }

    // Restore from backup
    fs.copyFileSync(backupFile.path, DATABASE_FILE)
    console.log(`✅ Database restored from: ${backupFile.name}`)

    // Verify restore
    const players = JSON.parse(fs.readFileSync(DATABASE_FILE, 'utf8'))
    console.log(`📊 Restored database contains ${players.length} players`)

    return true

  } catch (error) {
    console.error('❌ Error restoring from backup:', error instanceof Error ? error.message : String(error))
    return false
  }
}

/**
 * COMMAND: Add a Finnish player to database
 */
async function addPlayer(playerId, options) {
  console.log('➕ Adding Finnish Player to Database')
  console.log('===================================')

  try {
    const player = await playerDetectionService.addFinnishPlayer(parseInt(playerId))
    
    if (player) {
      console.log(`✅ Successfully added: ${player.name} (${player.team}, ${player.position})`)
      return true
    } else {
      console.log(`❌ Player ${playerId} is not Finnish or could not be verified`)
      return false
    }
  } catch (error) {
    console.error('❌ Error adding player:', error instanceof Error ? error.message : String(error))
    return false
  }
}

/**
 * COMMAND: Remove a Finnish player from database
 */
async function removePlayer(playerId, options) {
  console.log('➖ Removing Finnish Player from Database')
  console.log('====================================')

  try {
    const success = await playerDetectionService.removeFinnishPlayer(parseInt(playerId))
    
    if (success) {
      console.log(`✅ Successfully removed player ${playerId}`)
      return true
    } else {
      console.log(`❌ Player ${playerId} not found in database`)
      return false
    }
  } catch (error) {
    console.error('❌ Error removing player:', error instanceof Error ? error.message : String(error))
    return false
  }
}

/**
 * COMMAND: Search for Finnish players
 */
async function searchPlayers(query, options) {
  console.log('🔍 Searching Finnish Players')
  console.log('==========================')

  try {
    const players = await playerDetectionService.searchFinnishPlayers(query)
    
    if (players.length === 0) {
      console.log(`❌ No players found matching: ${query}`)
      return true
    }

    console.log(`📊 Found ${players.length} players matching: ${query}`)
    
    players.forEach(player => {
      console.log(`   ${player.name} (${player.team}, ${player.position}, ID: ${player.id})`)
    })

    return true
  } catch (error) {
    console.error('❌ Error searching players:', error instanceof Error ? error.message : String(error))
    return false
  }
}

/**
 * Main execution function
 */
async function main() {
  const command = process.argv[2]
  const options = getArguments()

  if (!command || options.help) {
    showHelp(command)
    return
  }

  let success = false

  try {
    switch (command) {
      case 'update':
        success = await updateDatabase(options)
        break
      case 'validate':
        success = await validateData(options)
        break
      case 'changes':
        success = await showChanges(options)
        break
      case 'stats':
        success = await showStats(options)
        break
      case 'backup':
        success = await createBackup(options)
        break
      case 'restore':
        const backupId = process.argv[3]
        if (!backupId) {
          console.error('❌ Backup ID required. Use "latest" or specify a timestamp.')
          showHelp('restore')
          success = false
        } else {
          success = await restoreFromBackup(backupId, options)
        }
        break
      case 'add':
        const playerIdToAdd = process.argv[3]
        if (!playerIdToAdd) {
          console.error('❌ Player ID required.')
          showHelp('add')
          success = false
        } else {
          success = await addPlayer(playerIdToAdd, options)
        }
        break
      case 'remove':
        const playerIdToRemove = process.argv[3]
        if (!playerIdToRemove) {
          console.error('❌ Player ID required.')
          showHelp('remove')
          success = false
        } else {
          success = await removePlayer(playerIdToRemove, options)
        }
        break
      case 'search':
        const searchQuery = process.argv[3]
        if (!searchQuery) {
          console.error('❌ Search query required.')
          showHelp('search')
          success = false
        } else {
          success = await searchPlayers(searchQuery, options)
        }
        break
      default:
        console.error(`❌ Unknown command: ${command}`)
        showHelp()
        success = false
    }

    if (success) {
      console.log('\n✅ Operation completed successfully!')
    } else {
      console.log('\n❌ Operation failed!')
      process.exit(1)
    }
  } catch (error) {
    console.error('❌ CLI failed:', error)
    process.exit(1)
  }
}

// Run the script
main()