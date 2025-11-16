#!/usr/bin/env node

/**
 * Simple NHL Game Data Fetcher Script
 *
 * This script fetches Finnish NHL player data from the NHL API and saves it to JSON files.
 * It can be used to populate data for specific dates or date ranges.
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

// Get current directory for ES modules
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.join(__dirname, '..')

// NHL API configuration
const NHL_API_BASE = 'https://api-web.nhle.com'
const FINNISH_NATIONALITY_CODES = ['FIN', 'FI']

// Output directory for JSON files (use the games directory to match existing structure)
const OUTPUT_DIR = path.join(projectRoot, 'data', 'games')

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true })
}

/**
 * Get command line arguments
 */
function getArguments() {
  const args = process.argv.slice(2)
  const options = {
    date: null,
    verbose: false,
    help: false
  }

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]
    const nextArg = args[i + 1]

    switch (arg) {
      case '--date':
      case '-d':
        options.date = nextArg
        i++
        break
      case '--verbose':
      case '-v':
        options.verbose = true
        break
      case '--help':
      case '-h':
        options.help = true
        break
    }
  }

  return options
}

/**
 * Display help information
 */
function showHelp() {
  console.log(`
Simple NHL Game Data Fetcher

USAGE:
  node simple-fetch-data.js [OPTIONS]

OPTIONS:
  -d, --date DATE         Fetch data for specific date (YYYY-MM-DD)
  -v, --verbose           Enable verbose logging
  -h, --help              Show this help message

EXAMPLES:
  node simple-fetch-data.js --date 2025-10-01
  node simple-fetch-data.js -d 2025-10-01 -v

OUTPUT:
  Files are saved to: data/games/
  File format: YYYY-MM-DD.json
`)
}

/**
 * Log message if verbose mode is enabled
 */
function log(message, options) {
  if (options.verbose) {
    console.log(`[${new Date().toISOString()}] ${message}`)
  }
}

/**
 * Check if a value is a placeholder
 */
function isPlaceholderValue(value) {
  if (typeof value !== 'string') return false
  
  const placeholderPatterns = [
    /^OPP$/i,
    /^Opponent Team$/i,
    /^TBD$/i,
    /^TBA$/i,
    /^UNK$/i,
    /^Unknown$/i,
    /^N\/A$/i,
    /^To Be Determined$/i,
    /^To Be Announced$/i,
    /^0-0$/,  // Generic score
    /^null$/i,
    /^undefined$/i
  ]
  
  return placeholderPatterns.some(pattern => pattern.test(value.trim()))
}

/**
 * Validate player data for placeholder values
 */
function validatePlayerData(playerData) {
  const requiredFields = ['name', 'team', 'opponent']
  const issues = []
  
  // Check required fields
  for (const field of requiredFields) {
    if (!playerData[field] || isPlaceholderValue(playerData[field])) {
      issues.push(`Missing or placeholder value for ${field}: ${playerData[field]}`)
    }
  }
  
  // Check for placeholder values in other fields
  if (isPlaceholderValue(playerData.team_full)) {
    issues.push(`Placeholder value for team_full: ${playerData.team_full}`)
  }
  
  if (isPlaceholderValue(playerData.opponent_full)) {
    issues.push(`Placeholder value for opponent_full: ${playerData.opponent_full}`)
  }
  
  // Check for generic scores
  if (isPlaceholderValue(playerData.game_score)) {
    issues.push(`Placeholder value for game_score: ${playerData.game_score}`)
  }
  
  // Check for impossible stats
  if (playerData.goals < 0 || playerData.assists < 0 || playerData.points < 0) {
    issues.push(`Invalid stats: goals=${playerData.goals}, assists=${playerData.assists}, points=${playerData.points}`)
  }
  
  return issues
}

/**
 * Fetch data from NHL API with improved error handling
 */
async function fetchFromAPI(url, options, critical = false) {
  try {
    log(`Fetching: ${url}`, options)
    const response = await fetch(url)

    if (!response.ok) {
      const errorMessage = `HTTP ${response.status}: ${response.statusText}`
      console.error(`API Error for ${url}: ${errorMessage}`)
      
      if (critical) {
        throw new Error(`Critical API call failed: ${errorMessage}`)
      }
      
      return null
    }

    const data = await response.json()
    
    // Check for empty or invalid responses
    if (!data) {
      const errorMessage = 'Empty response from API'
      console.error(`API Error for ${url}: ${errorMessage}`)
      
      if (critical) {
        throw new Error(`Critical API call failed: ${errorMessage}`)
      }
      
      return null
    }
    
    log(`Response received, size: ${JSON.stringify(data).length} chars`, options)
    return data
  } catch (error) {
    const errorMessage = `Failed to fetch ${url}: ${error.message}`
    console.error(errorMessage)
    
    if (critical) {
      throw new Error(`Critical API call failed: ${errorMessage}`)
    }
    
    return null
  }
}

/**
 * Get games scheduled for a specific date
 */
async function getGamesByDate(date, options) {
  const url = `${NHL_API_BASE}/v1/schedule/${date}`
  const data = await fetchFromAPI(url, options, true) // Mark as critical

  if (!data) {
    throw new Error(`Failed to fetch schedule data for ${date}. This is a critical failure.`)
  }

  // The API returns games in gameWeek array structure
  if (data?.gameWeek && data.gameWeek.length > 0) {
    // Find the games for the requested date
    const dayGames = data.gameWeek.find(week => week.date === date)
    return dayGames?.games || []
  }

  return []
}

/**
 * Get player information including nationality
 */
async function getPlayerInfo(playerId, options) {
  const url = `${NHL_API_BASE}/v1/player/${playerId}/landing`
  const data = await fetchFromAPI(url, options)
  return data
}

/**
 * Get player game log for a season
 */
async function getPlayerGameLog(playerId, season, options) {
  const url = `${NHL_API_BASE}/v1/player/${playerId}/game-log/${season}/2` // 2 = regular season
  const data = await fetchFromAPI(url, options)
  return data?.gameLog || []
}

/**
 * Check if player is Finnish
 */
function isFinnishPlayer(playerInfo) {
  if (!playerInfo?.nationality) return false
  const nationality = playerInfo.nationality.toUpperCase()
  return FINNISH_NATIONALITY_CODES.includes(nationality)
}

/**
 * Find player's stats for a specific game
 */
function findGameStatsForDate(gameLog, targetDate) {
  if (!Array.isArray(gameLog)) return null

  return gameLog.find(game => {
    const gameDate = new Date(game.gameDate).toISOString().split('T')[0]
    return gameDate === targetDate
  }) || null
}

/**
 * Get player's game result
 */
function getPlayerGameResult(game, teamAbbr) {
  if (!teamAbbr) return 'N/A'

  const homeScore = game.homeTeam?.score || 0
  const awayScore = game.awayTeam?.score || 0

  // Handle both old and new game data structures
  const homeTeamAbbr = game.homeTeam?.abbreviation || game.homeTeam?.abbrev || game.homeTeam?.triCode
  const awayTeamAbbr = game.awayTeam?.abbreviation || game.awayTeam?.abbrev || game.awayTeam?.triCode

  if (homeTeamAbbr === teamAbbr) {
    return homeScore > awayScore ? 'W' : homeScore < awayScore ? 'L' : 'OT'
  } else if (awayTeamAbbr === teamAbbr) {
    return awayScore > homeScore ? 'W' : awayScore < homeScore ? 'L' : 'OT'
  }

  return 'N/A'
}

/**
 * Get NHL season for a specific date in format YYYY(YYYY+1)
 */
function getSeasonForDate(date) {
  const year = parseInt(date.split('-')[0])
  const month = parseInt(date.split('-')[1])

  // NHL season typically starts in October
  // If date is before October, season started in previous year
  const seasonStartYear = month < 10 ? year - 1 : year

  return parseInt(`${seasonStartYear}${seasonStartYear + 1}`)
}

/**
 * Fetch Finnish players for a specific date
 */
async function getFinnishPlayersByDate(date, options) {
  log(`Fetching Finnish players for ${date}`, options)

  try {
    const games = await getGamesByDate(date, options)
    if (games.length === 0) {
      log(`No games found for ${date}`, options)
      return []
    }

    const finnishPlayers = []
    const seasonForDate = getSeasonForDate(date)
    const processedPlayerIds = new Set()
    let criticalErrors = 0

    for (const game of games) {
      log(`Processing game ${game.id}: ${game.awayTeam?.abbrev || game.awayTeam?.abbreviation || 'UNK'} @ ${game.homeTeam?.abbrev || game.homeTeam?.abbreviation || 'UNK'}`, options)

      // Get detailed game information to access player stats
      const gameDetails = await getGameDetails(game.id, options)
      if (!gameDetails) {
        console.error(`Critical error: Could not fetch details for game ${game.id}`)
        criticalErrors++
        continue
      }

      // Extract all players from both teams
      const allPlayers = []

      // Add away team players
      if (gameDetails.playerByGameStats?.awayTeam?.forwards || gameDetails.playerByGameStats?.awayTeam?.defensemen || gameDetails.playerByGameStats?.awayTeam?.goalies) {
        allPlayers.push(
          ...(gameDetails.playerByGameStats.awayTeam.forwards || []),
          ...(gameDetails.playerByGameStats.awayTeam.defensemen || []),
          ...(gameDetails.playerByGameStats.awayTeam.goalies || [])
        )
      }

      // Add home team players
      if (gameDetails.playerByGameStats?.homeTeam?.forwards || gameDetails.playerByGameStats?.homeTeam?.defensemen || gameDetails.playerByGameStats?.homeTeam?.goalies) {
        allPlayers.push(
          ...(gameDetails.playerByGameStats.homeTeam.forwards || []),
          ...(gameDetails.playerByGameStats.homeTeam.defensemen || []),
          ...(gameDetails.playerByGameStats.homeTeam.goalies || [])
        )
      }

      log(`Found ${allPlayers.length} players in game ${game.id}`, options)

      // Check each player for Finnish nationality
      for (const player of allPlayers) {
        if (processedPlayerIds.has(player.id)) continue

        // Get player info to check nationality
        const playerInfo = await getPlayerInfo(player.id, options)
        if (!playerInfo) {
          log(`Could not get info for player ${player.id}`, options)
          processedPlayerIds.add(player.id)
          continue
        }

        if (!isFinnishPlayer(playerInfo)) {
          processedPlayerIds.add(player.id)
          continue
        }

        log(`Found Finnish player: ${playerInfo.fullName || player.name}`, options)

        // Get player's game log
        const gameLog = await getPlayerGameLog(player.id, seasonForDate, options)

        // Validate game log data
        if (!gameLog || !Array.isArray(gameLog) || gameLog.length === 0) {
          log(`No game log data for ${playerInfo.fullName} in season ${seasonForDate}`, options)
          processedPlayerIds.add(player.id)
          continue
        }

        const gameStats = findGameStatsForDate(gameLog, date)

        if (gameStats && (gameStats.goals > 0 || gameStats.assists > 0)) {
          // Determine player's team and opponent
          const playerTeam = gameDetails.playerByGameStats?.awayTeam?.forwards?.some(p => p.id === player.id) ||
                          gameDetails.playerByGameStats?.awayTeam?.defensemen?.some(p => p.id === player.id) ||
                          gameDetails.playerByGameStats?.awayTeam?.goalies?.some(p => p.id === player.id)
                        ? gameDetails.awayTeam : gameDetails.homeTeam

          const opponentTeam = playerTeam === gameDetails.awayTeam ? gameDetails.homeTeam : gameDetails.awayTeam
          const opponentName = opponentTeam?.name?.default || opponentTeam?.placeName?.default + ' ' + opponentTeam?.commonName?.default

          const playerData = {
            name: playerInfo.fullName || player.name || '',
            team: playerTeam?.abbrev || playerTeam?.triCode || 'UNK',
            team_full: playerTeam?.name?.default || playerTeam?.placeName?.default || 'Unknown',
            position: playerInfo.primaryPosition?.abbreviation || 'N/A',
            goals: gameStats.goals || 0,
            assists: gameStats.assists || 0,
            points: (gameStats.goals || 0) + (gameStats.assists || 0),
            opponent: opponentTeam?.abbrev || opponentTeam?.triCode || 'UNK',
            opponent_full: opponentName || 'Unknown',
            game_score: `${gameDetails.homeTeam?.score || 0}-${gameDetails.awayTeam?.score || 0}`,
            game_result: getPlayerGameResult(gameDetails, playerTeam?.abbrev || playerTeam?.triCode),
            player_id: player.id,
            game_id: game.id
          }

          // Validate player data before adding
          const validationIssues = validatePlayerData(playerData)
          if (validationIssues.length > 0) {
            console.error(`Skipping player ${playerData.name} due to validation issues: ${validationIssues.join(', ')}`)
            continue
          }

          finnishPlayers.push(playerData)
          log(`Found Finnish player with points: ${playerData.name} (${playerData.points} pts)`, options)
        } else {
          log(`   ${playerInfo.fullName} - no points in this game`, options)
        }

        processedPlayerIds.add(player.id)
      }

      // Add delay to be respectful to the API
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    // Fail if too many critical errors occurred
    if (criticalErrors > 0 && criticalErrors >= games.length) {
      throw new Error(`All game detail fetches failed for ${date}. This indicates a critical API issue.`)
    }

    log(`Found ${finnishPlayers.length} Finnish players with points for ${date}`, options)
    return finnishPlayers

  } catch (error) {
    console.error(`Error fetching Finnish players for ${date}:`, error)
    throw error // Re-throw to let the main function handle the failure
  }
}

/**
 * Get detailed game information
 */
async function getGameDetails(gameId, options) {
  const url = `${NHL_API_BASE}/v1/gamecenter/${gameId}/boxscore`
  const data = await fetchFromAPI(url, options, true) // Mark as critical
  return data
}

/**
 * Save data to JSON file with validation
 */
function saveDataToFile(data, filename, options) {
  const filePath = path.join(OUTPUT_DIR, filename)

  try {
    // Validate data before saving
    if (Array.isArray(data)) {
      for (const player of data) {
        const issues = validatePlayerData(player)
        if (issues.length > 0) {
          throw new Error(`Invalid player data detected: ${issues.join(', ')}`)
        }
      }
    }

    const jsonData = JSON.stringify(data, null, 2)
    fs.writeFileSync(filePath, jsonData, 'utf8')
    log(`Data saved to: ${filePath}`, options)
    return filePath
  } catch (error) {
    console.error(`Error saving file ${filePath}:`, error)
    // Remove the file if it was partially written
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath)
      log(`Removed incomplete file: ${filePath}`, options)
    }
    return null
  }
}

/**
 * Main execution function
 */
async function main() {
  const options = getArguments()

  if (options.help) {
    showHelp()
    return
  }

  if (!options.date) {
    console.error('Error: --date is required')
    showHelp()
    process.exit(1)
  }

  console.log(`🏒 NHL Game Data Fetcher`)
  console.log(`📅 Fetching data for: ${options.date}`)

  try {
    const players = await getFinnishPlayersByDate(options.date, options)

    if (players.length > 0) {
      const savedFile = saveDataToFile(players, `${options.date}.json`, options)
      if (!savedFile) {
        console.error('❌ Failed to save data due to validation errors')
        process.exit(1)
      }
      
      console.log(`✅ Found ${players.length} Finnish players with points`)
      players.forEach(player => {
        console.log(`   ${player.name}: ${player.points} pts (${player.goals}G + ${player.assists}A)`)
      })
    } else {
      console.log(`ℹ️  No Finnish players with points found for ${options.date}`)
      // Still save an empty array to indicate the date was processed successfully
      const savedFile = saveDataToFile([], `${options.date}.json`, options)
      if (!savedFile) {
        console.error('❌ Failed to save empty data file')
        process.exit(1)
      }
    }

    console.log('📁 File saved to:', path.join(OUTPUT_DIR, `${options.date}.json`))
  } catch (error) {
    console.error('❌ Critical error during data fetching:', error.message)
    console.error('Script terminated to prevent creation of placeholder data.')
    process.exit(1)
  }
}

// Run the script
main().catch(error => {
  console.error('❌ Script failed:', error)
  process.exit(1)
})