/**
 * Simplified Player Detection Service
 *
 * This service identifies Finnish NHL players purely through NHL API calls
 * without relying on a static database. Each player is verified in real-time.
 */

// Configuration
const CONFIG = {
  NHL_API_BASE: '/api', // Use proxy instead of direct API
  REQUEST_TIMEOUT: 8000,
  MAX_RETRIES: 2,
  RETRY_DELAY: 500,
}

// Cache for recently verified Finnish players (simple in-memory cache)
const finnishPlayerCache = new Map()
const CACHE_EXPIRY_MS = 5 * 60 * 1000 // 5 minutes

/**
 * Fetch data from NHL API with retry logic
 * @param {string} url - URL to fetch
 * @returns {Promise<any|null>} API response or null on error
 */
async function fetchFromAPI(url) {
  for (let attempt = 1; attempt <= CONFIG.MAX_RETRIES; attempt++) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT)

      const response = await fetch(url, {
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      if (attempt === CONFIG.MAX_RETRIES) {
        console.error(`Error fetching ${url}:`, error instanceof Error ? error.message : String(error))
        return null
      }

      console.warn(`Attempt ${attempt} failed for ${url}, retrying...`)
      await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY))
    }
  }
}

/**
 * Verify if a player is Finnish using the NHL API
 * @param {number} playerId - Player ID to verify
 * @returns {Promise<Object|null>} Player info if Finnish, null otherwise
 */
async function verifyFinnishPlayer(playerId) {
  // Check cache first
  const cached = finnishPlayerCache.get(playerId)
  if (cached && (Date.now() - cached.timestamp) < CACHE_EXPIRY_MS) {
    return cached.player
  }

  try {
    const playerData = await fetchFromAPI(`${CONFIG.NHL_API_BASE}/v1/player/${playerId}/landing`)

    if (!playerData) {
      return null
    }

    // Check if nationality is Finnish (try multiple fields)
    let isFinnish = false

    // Primary check: nationality field
    const nationality = playerData.nationality?.toUpperCase()
    if (nationality === 'FIN' || nationality === 'FI') {
      isFinnish = true
    }

    // Fallback: check birthCountry if nationality is null/undefined
    if (!isFinnish && playerData.birthCountry) {
      const birthCountry = playerData.birthCountry.toUpperCase()
      isFinnish = (birthCountry === 'FIN' || birthCountry === 'FINLAND')
    }

    if (!isFinnish) {
      return null
    }

    const playerInfo = {
      id: playerData.id,
      name: `${playerData.firstName?.default || ''} ${playerData.lastName?.default || ''}`.trim(),
      team: playerData.currentTeamAbbrev || 'UNKNOWN',
      position: playerData.primaryPosition?.abbreviation || 'N/A',
      active: playerData.active || false,
      lastUpdated: new Date().toISOString()
    }

    // Cache the result
    finnishPlayerCache.set(playerId, {
      player: playerInfo,
      timestamp: Date.now()
    })

    return playerInfo
  } catch (error) {
    console.error(`Error verifying player ${playerId}:`, error)
    return null
  }
}

/**
 * Check if a player ID is Finnish
 * @param {number} playerId - Player ID to check
 * @returns {Promise<boolean>} True if player is Finnish
 */
async function isFinnishPlayer(playerId) {
  const player = await verifyFinnishPlayer(playerId)
  return player !== null
}

/**
 * Get Finnish player by ID
 * @param {number} playerId - Player ID
 * @returns {Promise<Object|null>} Finnish player info or null
 */
async function getFinnishPlayerById(playerId) {
  return await verifyFinnishPlayer(playerId)
}

/**
 * Get all Finnish player IDs currently in cache
 * @returns {Promise<Set<number>>} Set of Finnish player IDs
 */
async function getFinnishPlayerIds() {
  const ids = new Set()
  for (const [playerId, cached] of finnishPlayerCache.entries()) {
    if ((Date.now() - cached.timestamp) < CACHE_EXPIRY_MS && cached.player.active) {
      ids.add(playerId)
    }
  }
  return ids
}

/**
 * Fetch Finnish players directly from Python API
 * @returns {Promise<any[]>} Array of Finnish players
 */
async function fetchFinnishPlayersFromPython() {
  try {
    const response = await fetch('/api/finnish-players')
    if (!response.ok) {
      throw new Error(`Failed to fetch Finnish players: ${response.status} ${response.statusText}`)
    }
    const players = await response.json()
    return players
  } catch (error) {
    console.error('Error fetching Finnish players from Python API:', error)
    return []
  }
}

/**
 * Get all Finnish players currently in cache
 * @param {boolean} activeOnly - Return only active players
 * @returns {Promise<any[]>} Array of Finnish players
 */
async function getAllFinnishPlayers(activeOnly = true) {
  // Try to fetch fresh data from Python API
  const freshPlayers = await fetchFinnishPlayersFromPython()

  if (freshPlayers.length > 0) {
    // Update cache with fresh data
    for (const player of freshPlayers) {
      if (player.id) {  // Only cache players with IDs
        finnishPlayerCache.set(player.id, {
          player: {
            id: player.id,
            name: player.name,
            team: player.team_abbrev || player.team,
            position: player.position,
            active: player.is_active !== false,
            lastUpdated: new Date().toISOString()
          },
          timestamp: Date.now()
        })
      }
    }

    if (activeOnly) {
      return freshPlayers.filter(p => p.is_active !== false)
    }
    return freshPlayers
  }

  // Fallback to cache if API fails
  const players = []
  for (const [playerId, cached] of finnishPlayerCache.entries()) {
    if ((Date.now() - cached.timestamp) < CACHE_EXPIRY_MS) {
      if (!activeOnly || cached.player.active) {
        players.push(cached.player)
      }
    }
  }
  return players
}

/**
 * Get all NHL team abbreviations from standings
 * @returns {Promise<string[]>} Array of team abbreviations
 */
async function getAllTeamAbbreviations() {
  try {
    // Use current date to avoid redirect
    const today = new Date().toISOString().split('T')[0]
    const standingsData = await fetchFromAPI(`${CONFIG.NHL_API_BASE}/v1/standings/${today}`)
    if (!standingsData || !standingsData.standings) {
      return []
    }

    return standingsData.standings.map(team => team.teamAbbrev.default)
  } catch (error) {
    console.error('Error fetching team list:', error)
    return []
  }
}

/**
 * Scan all NHL teams to find Finnish players
 * @returns {Promise<Object[]>} Array of Finnish players from all teams
 */
async function scanAllTeamsForFinnishPlayers() {
  const finnishPlayers = []
  const teamAbbreviations = await getAllTeamAbbreviations()

  if (teamAbbreviations.length === 0) {
    console.warn('No teams found, falling back to known team list')
    // Fallback to known team abbreviations
    const knownTeams = [
      'ANA', 'ARI', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL',
      'DET', 'EDM', 'FLA', 'LAK', 'MIN', 'MTL', 'NJD', 'NSH', 'NYI', 'NYR',
      'OTT', 'PHI', 'PIT', 'SEA', 'SJS', 'STL', 'TBL', 'TOR', 'UTA', 'VAN',
      'VGK', 'WPG', 'WSH'
    ]
    teamAbbreviations.push(...knownTeams)
  }

  console.log(`Scanning ${teamAbbreviations.length} teams for Finnish players...`)

  // Get current season ID (format: YYYYYY+YY, e.g., 20252026)
  const currentYear = new Date().getFullYear()
  const nextYear = currentYear + 1
  const seasonId = `${currentYear}${nextYear}`

  for (const teamAbbrev of teamAbbreviations) {
    try {
      const rosterUrl = `${CONFIG.NHL_API_BASE}/v1/roster/${teamAbbrev}/${seasonId}`
      const rosterData = await fetchFromAPI(rosterUrl)

      if (!rosterData || !rosterData.forwards || !rosterData.defensemen || !rosterData.goalies) {
        console.warn(`Invalid roster data for ${teamAbbrev}`)
        continue
      }

      // Check all player positions
      const allPlayers = [
        ...rosterData.forwards || [],
        ...rosterData.defensemen || [],
        ...rosterData.goalies || []
      ]

      for (const player of allPlayers) {
        if (player.id) {
          const finnishPlayer = await verifyFinnishPlayer(player.id)
          if (finnishPlayer) {
            finnishPlayers.push({
              ...finnishPlayer,
              team: teamAbbrev
            })
          }
        }
      }

      // Small delay to avoid overwhelming the API
      await new Promise(resolve => setTimeout(resolve, 100))

    } catch (error) {
      console.warn(`Error scanning team ${teamAbbrev}:`, error)
    }
  }

  console.log(`Found ${finnishPlayers.length} Finnish players across all teams`)
  return finnishPlayers
}


/**
 * Clear expired cache entries
 */
function clearExpiredCache() {
  const now = Date.now()
  for (const [playerId, cached] of finnishPlayerCache.entries()) {
    if ((now - cached.timestamp) > CACHE_EXPIRY_MS) {
      finnishPlayerCache.delete(playerId)
    }
  }
}

// Clean up expired cache entries periodically
setInterval(clearExpiredCache, CACHE_EXPIRY_MS)

export default {
  getFinnishPlayerIds,
  isFinnishPlayer,
  getFinnishPlayerById,
  getAllFinnishPlayers,
  verifyFinnishPlayer,
  scanAllTeamsForFinnishPlayers
}