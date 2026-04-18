<script>
// @ts-nocheck - Svelte 5 runes not recognized by svelte-check

import { onMount } from 'svelte'
import { get } from 'svelte/store'
import { base } from '$app/paths'
import { draftRankings, loadProspects } from '$lib/stores/gameData'
import { correctFullName } from '$lib/utils/finnishNameUtils.js'
import { normalizeTeamAbbreviation } from '$lib/utils/teamMapping.js'

// biome-ignore lint/style/useConst: bind:value requires let
let activeFilter = $state('all') // 'all' | 'prospects' | 'draft2026'

// Sort options for prospects
// biome-ignore lint/style/useConst: bind:value requires let
let sortBy = $state('points') // 'points', 'goals', 'assists', 'league'
// biome-ignore lint/style/useConst: Svelte 5 $state
let sortDirection = $state('desc')

// Draft ranking source selection
// biome-ignore lint/style/useConst: bind:value requires let
let selectedRankingSlug = $state('nhl-central')
// Use get() from svelte/store for one-time read; reactivity handled via store subscription
/** @type {any} */
let _draftRankingsValue = get(draftRankings)
// Subscribe to store updates
$effect(() => {
    const unsub = draftRankings.subscribe((v) => {
        _draftRankingsValue = v
    })
    return unsub
})
const selectedRankingSource = $derived(
    _draftRankingsValue?.sources?.find(
        /** @param {any} s */ (s) => s.slug === selectedRankingSlug
    ) || _draftRankingsValue?.sources?.[0]
)
/** @type {Map} */
let _officialSeasonStatsByName = globalThis.$state(new Map())
/** @type {Map} */
const _epSeasonStatsByName = globalThis.$state(new Map())
/** @type {Map} */
let _nhlSeasonStatsById = globalThis.$state(new Map())
/** @type {Record<string, number>} */
let _selectedSeasonIndexByPlayer = globalThis.$state({})
/** @type {Map} */
const _unifiedGoalieStats = globalThis.$state(new Map())

onMount(() => {
    loadProspects()
    _loadDraftSeasonStats()
})

function _normalizeName(name) {
    return (name || '')
        .toString()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-zA-Z0-9\s-]/g, '')
        .replace(/\s+/g, ' ')
        .trim()
        .toLowerCase()
}

async function _loadDraftSeasonStats() {
    try {
        const [officialResponse, skatersResponse, goaliesResponse, unifiedGoaliesResponse] =
            await Promise.all([
                fetch(`${base}/data/leagues/league_prospects_official.json`),
                fetch(`${base}/data/player-stats/skaters-20252026.json`),
                fetch(`${base}/data/player-stats/goalies-20252026.json`),
                fetch(`${base}/data/player-stats/all-goalies.json`),
            ])

        const officialLookup = new Map()
        const nhlLookup = new Map()

        const appendEntry = (map, key, value) => {
            const existing = map.get(key) || []
            existing.push(value)
            map.set(key, existing)
        }

        if (officialResponse.ok) {
            const officialData = await officialResponse.json()
            const officialPlayers = Array.isArray(officialData?.players) ? officialData.players : []

            for (const player of officialPlayers) {
                appendEntry(officialLookup, _normalizeName(player.name), player)
            }
        }

        if (skatersResponse.ok) {
            const skaters = await skatersResponse.json()
            for (const skater of skaters) {
                nhlLookup.set(String(skater.playerId), {
                    league: 'NHL',
                    team: skater.teamAbbrev || '',
                    gp: Number(skater.gamesPlayed) || 0,
                    goals: Number(skater.goals) || 0,
                    assists: Number(skater.assists) || 0,
                    points: Number(skater.points) || 0,
                    savePct: 0,
                    gaa: 0,
                    shutouts: 0,
                    headshotUrl: skater.headshot || skater.headshotUrl || null,
                })
            }
        }

        if (goaliesResponse.ok) {
            const goalies = await goaliesResponse.json()
            for (const goalie of goalies) {
                nhlLookup.set(String(goalie.playerId), {
                    league: 'NHL',
                    team: goalie.teamAbbrev || '',
                    gp: Number(goalie.gamesPlayed) || 0,
                    goals: 0,
                    assists: 0,
                    points: 0,
                    savePct: Number(goalie.savePercentage) || 0,
                    gaa: Number(goalie.goalsAgainstAverage) || 0,
                    shutouts: Number(goalie.shutouts) || 0,
                    headshotUrl: goalie.headshot || goalie.headshotUrl || null,
                })
            }
        }

        _officialSeasonStatsByName = officialLookup
        _nhlSeasonStatsById = nhlLookup

        // Load unified goalie stats from all-goalies.json
        if (unifiedGoaliesResponse.ok) {
            const unifiedData = await unifiedGoaliesResponse.json()
            const goalies = unifiedData?.goalies || []
            for (const g of goalies) {
                const key = _normalizeName(g.name)
                _unifiedGoalieStats.set(key, {
                    gp: g.gp || 0,
                    savePct: g.savePct,
                    gaa: g.gaa,
                    shutouts: g.shutouts || 0,
                    league: g.league || '',
                    source: g.source || '',
                })
            }
        }
    } catch (_error) {
        // Leave prospects without enrichment if league files are unavailable.
    }
}

function _normalizeSeasonEntry(entry) {
    if (!entry) return null

    return {
        league: entry.league || '',
        team: entry.team || '',
        gp: Number(entry.gp ?? entry.games_played) || 0,
        goals: Number(entry.goals) || 0,
        assists: Number(entry.assists) || 0,
        points: Number(entry.points) || 0,
        savePct: Number(entry.savePct ?? entry.save_percentage) || 0,
        gaa: Number(entry.gaa ?? entry.goals_against_average) || 0,
        shutouts: Number(entry.shutouts) || 0,
        headshotUrl:
            entry.headshotUrl ||
            entry.headshot_url ||
            entry.headshot ||
            entry.photo_url ||
            entry.photoUrl ||
            null,
        headshotCrop: entry.headshotCrop || entry.headshot_crop || null,
    }
}

function _formatGoalieStat(value, decimals) {
    if (value === null || value === undefined || value === 0) {
        return 'Ei dataa'
    }
    return value.toFixed(decimals)
}

function _getUnifiedGoalieStats(playerName) {
    const key = _normalizeName(playerName)
    return _unifiedGoalieStats.get(key) || null
}

function _normalizeSeasonTeamKey(team) {
    return (team || '')
        .toString()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/\b(hockey|hc|hk)\b/g, '')
        .replace(/[^a-z0-9]/g, '')
        .trim()
}

function _getSeasonEntryKey(entry) {
    const normalizedLeague = _normalizeLeagueForPhoto(entry?.league)
    const normalizedTeam = _normalizeSeasonTeamKey(entry?.team)
    const statSignature = `${entry?.gp || 0}:${entry?.goals || 0}:${entry?.assists || 0}:${entry?.points || 0}:${entry?.savePct || 0}:${entry?.gaa || 0}:${entry?.shutouts || 0}`
    return `${normalizedLeague}::${normalizedTeam}::${statSignature}`
}

function _mergeSeasonEntries(officialEntries, epEntries) {
    const merged = new Map()

    const mergeIntoMap = (rawEntries, isOfficial) => {
        for (const rawEntry of rawEntries) {
            const entry = _normalizeSeasonEntry(rawEntry)
            const key = _getSeasonEntryKey(entry)
            const existing = merged.get(key)

            if (!existing) {
                merged.set(key, entry)
                continue
            }

            merged.set(key, {
                ...existing,
                ...entry,
                team: existing.team || entry.team,
                league: existing.league || entry.league,
                headshotUrl: isOfficial
                    ? entry.headshotUrl || existing.headshotUrl
                    : existing.headshotUrl || entry.headshotUrl,
                headshotCrop: isOfficial
                    ? entry.headshotCrop || existing.headshotCrop
                    : existing.headshotCrop || entry.headshotCrop,
                gp: existing.gp || entry.gp,
                goals: existing.goals || entry.goals,
                assists: existing.assists || entry.assists,
                points: existing.points || entry.points,
                savePct: existing.savePct || entry.savePct,
                gaa: existing.gaa || entry.gaa,
                shutouts: existing.shutouts || entry.shutouts,
            })
        }
    }

    mergeIntoMap(officialEntries, true)
    mergeIntoMap(epEntries, false)

    return Array.from(merged.values())
}

function _sortSeasonEntries(entries) {
    return [...entries].sort((a, b) => {
        if ((b.gp || 0) !== (a.gp || 0)) return (b.gp || 0) - (a.gp || 0)
        if ((b.points || 0) !== (a.points || 0)) return (b.points || 0) - (a.points || 0)
        return (b.savePct || 0) - (a.savePct || 0)
    })
}

function _buildSeasonData(player, fallbackStats = null) {
    const normalizedName = _normalizeName(
        player.name || `${player.firstName || ''} ${player.lastName || ''}`
    )
    const officialEntries = _officialSeasonStatsByName.get(normalizedName) || []
    const epEntries = _epSeasonStatsByName.get(normalizedName) || []
    const seasonEntries = _mergeSeasonEntries(officialEntries, epEntries)
    const playerId = player?.id || player?.playerId
    const nhlEntry = playerId ? _nhlSeasonStatsById.get(String(playerId)) : null

    if (nhlEntry) {
        seasonEntries.push(_normalizeSeasonEntry(nhlEntry))
    }

    const fallbackEntry = fallbackStats
        ? _normalizeSeasonEntry({
              ...fallbackStats,
              league: player?.league,
              team: player?.currentTeam || player?.team || '',
          })
        : null

    if (fallbackEntry) {
        const hasMatch = seasonEntries.some(
            (entry) => _getSeasonEntryKey(entry) === _getSeasonEntryKey(fallbackEntry)
        )
        if (!hasMatch) {
            seasonEntries.push(fallbackEntry)
        }
    }

    const sortedEntries = _sortSeasonEntries(seasonEntries.filter(Boolean))
    const primaryEntry = sortedEntries[0] ||
        _normalizeSeasonEntry(fallbackStats) || {
            league: player?.league || '',
            team: player?.currentTeam || player?.team || '',
            gp: 0,
            goals: 0,
            assists: 0,
            points: 0,
            savePct: 0,
            gaa: 0,
            shutouts: 0,
            headshotUrl: null,
        }

    return {
        entries: sortedEntries,
        primaryEntry,
    }
}

// Filter active prospects based on season data and age
// A prospect is considered active if they:
// 1. Are 26 or younger
// 2. Are NOT established NHL regulars (20+ NHL games this season)
const ACTIVE_AGE_CUTOFF = 24
const NHL_REGULAR_GP_THRESHOLD = 20 // Players with 20+ NHL games are considered regulars, not prospects

// Track NHL regulars (loaded from stats)
let _nhlRegularIds = globalThis.$state(new Set())

// Load NHL stats to identify regulars
globalThis.$effect(() => {
    if (globalThis.$prospects.length > 0) {
        fetch(`${base}/data/player-stats/skaters-20252026.json`)
            .then((r) => (r.ok ? r.json() : []))
            .then((skaters) => {
                const regulars = new Set()
                for (const s of skaters) {
                    if (s.gamesPlayed >= NHL_REGULAR_GP_THRESHOLD) {
                        regulars.add(s.playerId)
                    }
                }
                // Also check goalies (lower threshold)
                return fetch(`${base}/data/player-stats/goalies-20252026.json`)
                    .then((r) => (r.ok ? r.json() : []))
                    .then((goalies) => {
                        for (const g of goalies) {
                            if (g.gamesPlayed >= 10) {
                                // Goalies: 10+ games = regular
                                regulars.add(g.playerId)
                            }
                        }
                        _nhlRegularIds = regulars
                    })
            })
            .catch(() => {
                // Silently ignore - will just show all prospects
            })
    }
})

const activeProspects = globalThis.$derived(
    _dedupeProspects(globalThis.$prospects).filter((p) => {
        if (_isDraftRankingOnlyProspect(p)) {
            return false
        }

        // Check age
        let age = null
        if (p.birthDate) {
            age = new Date().getFullYear() - new Date(p.birthDate).getFullYear()
        }
        const ageOk = age === null || age < ACTIVE_AGE_CUTOFF

        // Skip if NHL regular (established player, not a prospect)
        const playerId = parseInt(p.id, 10)
        if (_nhlRegularIds.has(playerId)) {
            return false
        }

        return ageOk
    })
)

// Derived prospects
// Combine all prospects: drafted prospects + draft rankings
const allPlayers = globalThis.$derived(() => {
    const players = []

    // Add drafted prospects with stats
    for (const p of activeProspects) {
        const seasonData = _buildSeasonData(p, p.stats)
        const primarySeason = seasonData.primaryEntry
        players.push({
            ...p,
            playerId: p.id || null,
            name: correctFullName(p.name),
            currentTeam: primarySeason.team || p.currentTeam,
            league: primarySeason.league || p.league,
            stats: primarySeason,
            seasonEntries: seasonData.entries,
            headshotCrop: p.headshotCrop || p.headshot_crop || null,
            displayHeadshot: _getPreferredProspectHeadshot(
                { ...p, league: primarySeason.league },
                primarySeason
            ),
            displayHeadshotCrop:
                primarySeason.headshotCrop || p.headshotCrop || p.headshot_crop || null,
            photoFallbackPlayerId: _getPhotoFallbackPlayerId(
                primarySeason.league,
                p.id || null,
                _getPreferredProspectHeadshot({ ...p, league: primarySeason.league }, primarySeason)
            ),
            type: 'prospect',
            sortKey: primarySeason.points || 0,
        })
    }

    // Add 2026 draft rankings from selected source
    if (selectedRankingSource) {
        let draftPlayers = []
        if (selectedRankingSource.slug === 'nhl-central') {
            draftPlayers = [
                ...(selectedRankingSource.categories?.north_american || []),
                ...(selectedRankingSource.categories?.international || []),
            ]
        } else {
            draftPlayers = selectedRankingSource.players || []
        }

        for (const p of draftPlayers) {
            const firstName = p.firstName || p.name?.split(' ')[0] || ''
            const lastName =
                p.lastName ||
                (p.name?.includes(' ') ? p.name.split(' ').slice(1).join(' ') : p.name) ||
                ''
            const rank = p.midtermRank || p.rank
            const draftName = p.name || `${firstName} ${lastName}`
            const draftLeague =
                p.lastAmateurLeague?.replace('FINLAND-', '')?.replace('H-EAST', 'NCAA') ||
                p.league?.replace('FINLAND-', '') ||
                'Jr'
            const seasonData = _buildSeasonData(
                { ...p, name: draftName, playerId: p.playerId || null },
                null
            )
            const primarySeason = seasonData.primaryEntry

            players.push({
                id: `draft2026-${selectedRankingSource.slug}-${rank}`,
                name: correctFullName(draftName),
                position: p.positionCode || p.position,
                birthDate: p.birthDate,
                birthCity: p.birthCity,
                nhlRights: '2026',
                league: primarySeason.league || draftLeague,
                currentTeam: primarySeason.team || p.lastAmateurClub || p.team,
                draftRank: rank,
                height: p.heightInInches
                    ? Math.round(p.heightInInches * 2.54)
                    : typeof p.height === 'number'
                      ? p.height
                      : null,
                weight: p.weightInPounds
                    ? Math.round(p.weightInPounds * 0.453592)
                    : typeof p.weight === 'number'
                      ? p.weight
                      : null,
                playerId: p.playerId || null,
                headshot: p.playerId
                    ? `https://assets.nhle.com/mugs/nhl/20262027/2026/${p.playerId}.png`
                    : `https://assets.nhle.com/mugs/nhl/20262027/2026/${rank}.png`,
                seasonEntries: seasonData.entries,
                headshotCrop: p.headshotCrop || p.headshot_crop || null,
                displayHeadshot: _getPreferredDraftHeadshot(
                    primarySeason.league || draftLeague,
                    p.playerId || null,
                    primarySeason
                ),
                displayHeadshotCrop:
                    primarySeason.headshotCrop || p.headshotCrop || p.headshot_crop || null,
                photoFallbackPlayerId: _getPhotoFallbackPlayerId(
                    primarySeason.league || draftLeague,
                    p.playerId || null,
                    _getPreferredDraftHeadshot(
                        primarySeason.league || draftLeague,
                        p.playerId || null,
                        primarySeason
                    )
                ),
                stats: primarySeason,
                type: 'draft2026',
                sortKey: primarySeason.points || 0,
            })
        }
    }

    return _dedupeDisplayPlayers(players)
})

// Filter players
const filteredPlayers = globalThis.$derived(() => {
    const all = allPlayers()
    if (activeFilter === 'prospects') return all.filter((p) => p.type === 'prospect')
    if (activeFilter === 'draft2026') return all.filter((p) => p.type === 'draft2026')
    return all
})

// Separate goalies and skaters
const goalies = globalThis.$derived(filteredPlayers().filter((p) => p.position === 'G'))
const skaters = globalThis.$derived(filteredPlayers().filter((p) => p.position !== 'G'))

// Sort options for goalies
let goalieSortBy = globalThis.$state('savePct') // 'savePct', 'gaa', 'gp'
let goalieSortDirection = globalThis.$state('desc')

// Sorted skaters (existing sort logic)
const _sortedProspects = globalThis.$derived(
    [...skaters].sort((a, b) => {
        if (sortBy === 'league') {
            return sortDirection === 'asc'
                ? a.league.localeCompare(b.league)
                : b.league.localeCompare(a.league)
        }
        if (sortBy === 'age') {
            if (sortDirection === 'asc') {
                return b.birthDate.localeCompare(a.birthDate)
            }
            return a.birthDate.localeCompare(b.birthDate)
        }

        const valA = a.stats?.[sortBy] || 0
        const valB = b.stats?.[sortBy] || 0
        return sortDirection === 'asc' ? valA - valB : valB - valA
    })
)

// Sorted goalies (goalie-specific sort logic)
const _sortedGoalies = globalThis.$derived(
    [...goalies].sort((a, b) => {
        if (goalieSortBy === 'savePct') {
            const valA = a.stats?.savePct || 0
            const valB = b.stats?.savePct || 0
            return goalieSortDirection === 'asc' ? valA - valB : valB - valA
        }
        if (goalieSortBy === 'gaa') {
            // GAA: lower is better, so reverse the sort
            const valA = a.stats?.gaa || 99
            const valB = b.stats?.gaa || 99
            return goalieSortDirection === 'asc' ? valA - valB : valB - valA
        }
        const valA = a.stats?.[goalieSortBy] || 0
        const valB = b.stats?.[goalieSortBy] || 0
        return goalieSortDirection === 'asc' ? valA - valB : valB - valA
    })
)

function _setSort(field) {
    if (sortBy === field) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc'
    } else {
        sortBy = field
        sortDirection = field === 'age' ? 'asc' : 'desc'
    }
}

function _setGoalieSort(field) {
    if (goalieSortBy === field) {
        goalieSortDirection = goalieSortDirection === 'asc' ? 'desc' : 'asc'
    } else {
        goalieSortBy = field
        // For GAA, lower is better, so start with asc (best first)
        goalieSortDirection = field === 'gaa' ? 'asc' : 'desc'
    }
}

function _getSortIcon(field) {
    if (sortBy !== field) return ''
    return sortDirection === 'asc' ? '↑' : '↓'
}

function _getGoalieSortIcon(field) {
    if (goalieSortBy !== field) return ''
    return goalieSortDirection === 'asc' ? '↑' : '↓'
}

function _getDisplayNhlRights(teamAbbrev) {
    if (!teamAbbrev || teamAbbrev === 'N/A') return ''
    return normalizeTeamAbbreviation(teamAbbrev)
}

function _hasKnownNhlRights(player) {
    return Boolean(_getDisplayNhlRights(player?.nhlRights))
}

function _normalizeLeagueForPhoto(league) {
    return (league || '').toString().trim().toUpperCase()
}

function _shouldUseNhlMugshot(league) {
    const normalizedLeague = _normalizeLeagueForPhoto(league)
    return ['NHL', 'AHL', 'ECHL'].includes(normalizedLeague)
}

function _getProspectHeadshotZoom(league) {
    return _shouldUseNhlMugshot(league) ? 1.08 : 1.26
}

function _getProspectHeadshotPosition(league) {
    return _shouldUseNhlMugshot(league) ? '50% 18%' : '50% 10%'
}

function _getProspectHeadshotSettings(player, league) {
    const selectedSeason = _getSelectedSeasonEntry(player)
    const crop =
        selectedSeason?.headshotCrop || player?.headshotCrop || player?.displayHeadshotCrop || null
    return {
        zoom: crop?.zoom || _getProspectHeadshotZoom(league),
        objectPosition: crop?.objectPosition || _getProspectHeadshotPosition(league),
    }
}

function _isNhlMugshotUrl(url) {
    return typeof url === 'string' && url.includes('assets.nhle.com/mugs/')
}

function _getPreferredProspectHeadshot(player, seasonStats = null) {
    const currentLeaguePhoto = seasonStats?.headshotUrl || null
    if (currentLeaguePhoto) return currentLeaguePhoto

    const playerHeadshot = player?.headshot || null
    if (playerHeadshot && !_isNhlMugshotUrl(playerHeadshot)) {
        return playerHeadshot
    }

    if (
        _isNhlMugshotUrl(playerHeadshot) &&
        _shouldUseNhlMugshot(player?.league) &&
        _hasKnownNhlRights(player)
    ) {
        return playerHeadshot
    }

    return null
}

function _getPreferredDraftHeadshot(playerLeague, playerId, seasonStats) {
    if (seasonStats?.headshotUrl) return seasonStats.headshotUrl

    if (_shouldUseNhlMugshot(playerLeague) && playerId) {
        return `https://assets.nhle.com/mugs/nhl/20262027/2026/${playerId}.png`
    }

    return null
}

function _getSeasonSelectionKey(player) {
    return String(player?.id || player?.playerId || player?.name || '')
}

function _getSelectedSeasonIndex(player) {
    const key = _getSeasonSelectionKey(player)
    const selectedIndex = _selectedSeasonIndexByPlayer[key]
    return Number.isInteger(selectedIndex) ? selectedIndex : 0
}

function _getSelectedSeasonEntry(player) {
    const entries = Array.isArray(player?.seasonEntries) ? player.seasonEntries : []
    return entries[_getSelectedSeasonIndex(player)] || player?.stats || null
}

function _getSeasonSelectorEntries(player) {
    const entries = Array.isArray(player?.seasonEntries) ? player.seasonEntries : []
    const deduped = new Map()

    entries.forEach((entry, index) => {
        const key = `${_normalizeLeagueForPhoto(entry?.league)}::${_normalizeSeasonTeamKey(entry?.team)}`
        const existing = deduped.get(key)

        if (!existing || (entry?.gp || 0) > (existing.entry?.gp || 0)) {
            deduped.set(key, { entry, index })
        }
    })

    return Array.from(deduped.values())
}

function _getBestAvailableSeasonHeadshot(player) {
    const selectedSeason = _getSelectedSeasonEntry(player)
    if (selectedSeason?.headshotUrl) return selectedSeason.headshotUrl

    const entries = Array.isArray(player?.seasonEntries) ? player.seasonEntries : []
    const selectedLeague = _normalizeLeagueForPhoto(selectedSeason?.league || player?.league)

    if (!_shouldUseNhlMugshot(selectedLeague)) {
        const preferredLeagueEntry = entries.find(
            (entry) =>
                entry?.headshotUrl &&
                _normalizeLeagueForPhoto(entry?.league) === selectedLeague &&
                !_isNhlMugshotUrl(entry.headshotUrl)
        )
        if (preferredLeagueEntry?.headshotUrl) return preferredLeagueEntry.headshotUrl

        const anyNonNhlEntry = entries.find(
            (entry) => entry?.headshotUrl && !_isNhlMugshotUrl(entry.headshotUrl)
        )
        if (anyNonNhlEntry?.headshotUrl) return anyNonNhlEntry.headshotUrl
    }

    for (const entry of entries) {
        if (entry?.headshotUrl) return entry.headshotUrl
    }

    if (
        !_shouldUseNhlMugshot(selectedLeague) &&
        player?.displayHeadshot &&
        !_isNhlMugshotUrl(player.displayHeadshot)
    ) {
        return player.displayHeadshot
    }

    return player?.displayHeadshot || null
}

function _getBestFallbackPlayerId(player) {
    const selectedSeason = _getSelectedSeasonEntry(player)
    const playerId = player?.playerId || player?.id || null
    if (!playerId) return null

    const selectedLeague = selectedSeason?.league || player?.league
    if (_shouldUseNhlMugshot(selectedLeague) && _hasKnownNhlRights(player)) return playerId

    const explicitUrl = _getBestAvailableSeasonHeadshot(player) || ''

    // Return playerId if there's an explicit NHL headshot URL (handles Mestis and other leagues)
    if (typeof explicitUrl === 'string' && explicitUrl.includes('assets.nhle.com/mugs/')) {
        return playerId
    }

    if (typeof explicitUrl === 'string' && explicitUrl.includes('www.shl.se/imageproxy/')) {
        return playerId
    }

    const entries = Array.isArray(player?.seasonEntries) ? player.seasonEntries : []
    const fallbackLeagueEntry = entries.find((entry) => _shouldUseNhlMugshot(entry?.league))
    return fallbackLeagueEntry ? playerId : null
}

function _selectSeasonEntry(player, index) {
    const key = _getSeasonSelectionKey(player)
    _selectedSeasonIndexByPlayer = {
        ..._selectedSeasonIndexByPlayer,
        [key]: index,
    }
}

function _getPhotoFallbackPlayerId(playerLeague, playerId, explicitPhotoUrl) {
    if (explicitPhotoUrl) return null
    return _shouldUseNhlMugshot(playerLeague) ? playerId || null : null
}

function _getProspectIdentityKey(player) {
    if (player?.id !== undefined && player?.id !== null) return `id:${String(player.id)}`
    if (player?.name && player?.birthDate) return `name:${player.name}:${player.birthDate}`
    return `fallback:${player?.name || ''}:${player?.currentTeam || ''}:${player?.league || ''}`
}

function _getProspectPriority(player) {
    const sources = Array.isArray(player?.sources) ? player.sources : []

    if (sources.some((source) => source.startsWith('team_prospects:'))) return 3
    if (player?.league === 'NHL') return 2
    if (sources.some((source) => source.startsWith('draft_picks:'))) return 1
    return 0
}

function _getDisplayPlayerIdentityKey(player) {
    if (player?.name && player?.birthDate) {
        return `name:${_normalizeName(player.name)}:${player.birthDate}`
    }
    if (player?.playerId) return `playerId:${String(player.playerId)}`
    return _getProspectIdentityKey(player)
}

function _getDisplayPlayerPriority(player) {
    if (player?.type === 'prospect') return 2
    if (player?.type === 'draft2026') return 1
    return 0
}

function _dedupeDisplayPlayers(players) {
    const deduped = new Map()

    for (const player of players) {
        const key = _getDisplayPlayerIdentityKey(player)
        const existing = deduped.get(key)

        if (!existing || _getDisplayPlayerPriority(player) > _getDisplayPlayerPriority(existing)) {
            deduped.set(key, player)
        }
    }

    return Array.from(deduped.values())
}

function _isDraftRankingOnlyProspect(player) {
    const sources = Array.isArray(player?.sources) ? player.sources : []
    if (sources.length === 0) return false

    const hasDraftRankingSource = sources.some((source) => source.startsWith('draft_rankings:'))
    const hasNonDraftSource = sources.some((source) => !source.startsWith('draft_rankings:'))

    return hasDraftRankingSource && !hasNonDraftSource && !_hasKnownNhlRights(player)
}

function _dedupeProspects(players) {
    const deduped = new Map()

    for (const player of players) {
        const key = _getProspectIdentityKey(player)
        const existing = deduped.get(key)

        if (!existing || _getProspectPriority(player) > _getProspectPriority(existing)) {
            deduped.set(key, player)
        }
    }

    return Array.from(deduped.values())
}
</script>

<svelte:head>
    <title>Suomalaiset NHL-lupaukset - Varausprospectit ja tulevat tähdet</title>
    <meta name="description" content="Seuraa suomalaisten NHL-varausten ja tulevien huippujen otteita maailmalla." />
    <meta property="og:title" content="Suomalaiset NHL-lupaukset" />
    <meta property="og:description" content="Seuraa suomalaisten NHL-varausten ja tulevien huippujen otteita maailmalla." />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/lupaukset" />
</svelte:head>

<div class="min-h-screen bg-slate-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <!-- Header -->
        <div class="text-center mb-12">
            <a href="{base}/" class="inline-block mb-6 hover:opacity-80 transition-opacity">
                <img
                    src={base + "/logo.svg"}
                    alt="Suomalaiset NHL-pelaajat"
                    class="w-16 h-16 mx-auto"
                />
            </a>
            <h1 class="text-4xl font-bold text-slate-900 mb-4">
                Suomalaiset Lupaukset
            </h1>
            <p class="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
                Seuraa suomalaisten NHL-varausten ja tulevien huippujen otteita maailmalla.
            </p>

            <!-- Filter Buttons -->
            <div class="flex justify-center gap-2 flex-wrap">
                <button 
                    class="px-4 py-2 rounded-lg text-sm font-semibold transition-all {activeFilter === 'all' ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200'}"
                    onclick={() => activeFilter = 'all'}
                >
                    Kaikki ({allPlayers().length})
                </button>
                <button 
                    class="px-4 py-2 rounded-lg text-sm font-semibold transition-all {activeFilter === 'prospects' ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200'}"
                    onclick={() => activeFilter = 'prospects'}
                >
                    NHL-varaukset
                </button>
                <button 
                    class="px-4 py-2 rounded-lg text-sm font-semibold transition-all {activeFilter === 'draft2026' ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200'}"
                    onclick={() => activeFilter = 'draft2026'}
                >
                    Draft 2026
                </button>
            </div>

            <!-- Ranking Source Selector (only visible when Draft 2026 is active) -->
            {#if activeFilter === 'draft2026'}
                <div class="mt-8 max-w-xs mx-auto">
                    <label for="ranking-source" class="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Rankings-lähde</label>
                    <select 
                        id="ranking-source"
                        bind:value={selectedRankingSlug}
                        class="block w-full bg-white border border-slate-200 text-slate-700 py-2 px-3 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm"
                    >
                        {#each globalThis.$draftRankings.sources || [] as source}
                            <option value={source.slug}>{source.name}</option>
                        {/each}
                    </select>
                </div>
            {/if}
        </div>

        {#if globalThis.$prospectsLoading}
            <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        {:else}
            <div in:fade={{ duration: 300 }}>
                    <!-- Controls -->
                    <div class="flex justify-center gap-3 mb-8 flex-wrap">
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'points' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            onclick={() => _setSort('points')}
                        >
                            Pisteet {getSortIcon('points')}
                        </button>
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'goals' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            onclick={() => _setSort('goals')}
                        >
                            Maalit {getSortIcon('goals')}
                        </button>
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'league' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            onclick={() => _setSort('league')}
                        >
                            Liiga {getSortIcon('league')}
                        </button>
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'age' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            onclick={() => {
                                sortBy = 'age';
                                sortDirection = 'asc';
                            }}
                        >
                            Ikä {getSortIcon('age')}
                        </button>
                    </div>

                    <!-- Active prospects count -->
                    <div class="text-center mb-6">
                        <span class="text-sm text-slate-500">
                            Näytetään {sortedProspects.length} kenttäpelaajaa ja {sortedGoalies.length} maalivahtia
                        </span>
                    </div>

                    <!-- Skaters Grid -->
                    {#if sortedProspects.length === 0}
                        <div class="text-center text-slate-400 mt-12">
                            <p>Ei löytynyt lupauksia.</p>
                        </div>
                    {:else}
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {#each sortedProspects as player, index (`${player.id}-${index}`)}
                                {@const selectedSeason = _getSelectedSeasonEntry(player)}
                                {@const headshotUrl = _getBestAvailableSeasonHeadshot(player)}
                                {@const headshotSettings = _getProspectHeadshotSettings(player, selectedSeason?.league || player.league)}
                                <div 
                                    class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md hover:border-blue-200 transition-all group p-4"
                                >
                                    <div class="flex items-center gap-4 mb-4">
                                        <div class="relative w-20 h-20 flex-shrink-0">
                                            <div class="w-full h-full rounded-full border-2 border-slate-100 overflow-hidden bg-slate-50 relative z-10">
                                                <PlayerHeadshot
                                                    playerId={_getBestFallbackPlayerId(player)}
                                                    explicitUrl={headshotUrl}
                                                    teamAbbrev={player.nhlRights}
                                                    alt={player.name}
                                                    imageClass="w-full h-full object-cover object-top"
                                                    zoom={headshotSettings.zoom}
                                                    objectPosition={headshotSettings.objectPosition}
                                                    autoFocusFace={false}
                                                    fallbackClass="w-full h-full flex items-center justify-center text-2xl font-bold text-slate-400"
                                                    initials={player.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                                                    loading="lazy"
                                                />
                                            </div>
                                            {#if player.type === 'draft2026' || _hasKnownNhlRights(player)}
                                                <div class="absolute -bottom-1 -right-1 z-20 bg-white rounded-full p-1 shadow-sm border border-slate-100">
                                                    <div class="w-7 h-7 flex items-center justify-center">
                                                        {#if player.type === 'draft2026'}
                                                            <span class="text-[10px] font-black text-amber-600">#{player.draftRank}</span>
                                                        {:else if _getDisplayNhlRights(player.nhlRights)}
                                                            <TeamLogo team={_getDisplayNhlRights(player.nhlRights)} size="24" />
                                                        {/if}
                                                    </div>
                                                </div>
                                            {/if}
                                        </div>
                                        
                                        <div class="min-w-0">
                                            <div class="flex items-center gap-2 mb-1">
                                                <div class="inline-block bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                                                    {selectedSeason?.league || player.league}
                                                </div>
                                                {#if player.type === 'draft2026'}
                                                    <div class="inline-block bg-amber-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                                                        Draft 2026
                                                    </div>
                                                {/if}
                                            </div>
                                            <h3 class="text-base font-bold text-slate-900 truncate">{player.name}</h3>
                                            <div class="space-y-1 text-xs text-slate-500">
                                                <div class="truncate">{selectedSeason?.team || player.currentTeam}</div>
                                                <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
                                                    {#if player.birthDate}
                                                        <span>{new Date().getFullYear() - new Date(player.birthDate).getFullYear()} vuotta</span>
                                                    {/if}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {#if _getSeasonSelectorEntries(player).length > 1}
                                        <div class="mb-3 flex flex-wrap gap-2">
                                            {#each _getSeasonSelectorEntries(player) as { entry, index }}
                                                <button
                                                    class={`rounded-full border px-2.5 py-1 text-[10px] font-semibold transition-colors ${
                                                        _getSelectedSeasonIndex(player) === index
                                                            ? 'border-blue-200 bg-blue-50 text-blue-700'
                                                            : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300 hover:text-slate-700'
                                                    }`}
                                                    onclick={() => _selectSeasonEntry(player, index)}
                                                    type="button"
                                                >
                                                    {entry.league} {entry.gp || 0} GP
                                                </button>
                                            {/each}
                                        </div>
                                    {/if}

                                    {#if player.type === 'draft2026'}
                                        <!-- Draft prospect stats -->
                                        <div class="grid grid-cols-4 gap-2 bg-amber-50/50 rounded-lg p-3 text-center border border-amber-100/50">
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">GP</div>
                                                <div class="font-mono font-bold text-slate-700">{selectedSeason?.gp || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">G</div>
                                                <div class="font-mono font-bold text-emerald-600">{selectedSeason?.goals || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">A</div>
                                                <div class="font-mono font-bold text-amber-600">{selectedSeason?.assists || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">P</div>
                                                <div class="font-mono font-bold text-slate-900">{selectedSeason?.points || 0}</div>
                                            </div>
                                        </div>
                                    {:else}
                                        <!-- Regular prospect stats -->
                                        <div class="grid grid-cols-4 gap-2 bg-slate-50/50 rounded-lg p-3 text-center border border-slate-100/50">
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">GP</div>
                                                <div class="font-mono font-bold text-slate-700">{selectedSeason?.gp || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">G</div>
                                                <div class="font-mono font-bold text-emerald-600">{selectedSeason?.goals || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">A</div>
                                                <div class="font-mono font-bold text-amber-600">{selectedSeason?.assists || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">P</div>
                                                <div class="font-mono font-bold text-slate-900">{selectedSeason?.points || 0}</div>
                                            </div>
                                        </div>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    {/if}

                    <!-- Goalies Section -->
                    {#if sortedGoalies.length > 0}
                        <div class="mt-12">
                            <h2 class="text-2xl font-bold text-slate-900 mb-6 text-center">Maalivahdit</h2>
                            
                            <!-- Goalie Sort Controls -->
                            <div class="flex justify-center gap-3 mb-6 flex-wrap">
                                <button 
                                    class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                                    {goalieSortBy === 'savePct' ? 'bg-emerald-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-emerald-300 hover:bg-slate-50'}"
                                    onclick={() => _setGoalieSort('savePct')}
                                >
                                    Torjunta-% {getGoalieSortIcon('savePct')}
                                </button>
                                <button 
                                    class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                                    {goalieSortBy === 'gaa' ? 'bg-emerald-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-emerald-300 hover:bg-slate-50'}"
                                    onclick={() => _setGoalieSort('gaa')}
                                >
                                    Päästettyjen keskiarvo {getGoalieSortIcon('gaa')}
                                </button>
                                <button 
                                    class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                                    {goalieSortBy === 'gp' ? 'bg-emerald-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-emerald-300 hover:bg-slate-50'}"
                                    onclick={() => _setGoalieSort('gp')}
                                >
                                    Ottelut {getGoalieSortIcon('gp')}
                                </button>
                            </div>

                            <!-- Goalies Grid -->
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {#each sortedGoalies as goalie, index (`${goalie.id}-${index}`)}
                                    {@const selectedSeason = _getSelectedSeasonEntry(goalie)}
                                    {@const unifiedStats = _getUnifiedGoalieStats(goalie.name)}
                                    {@const headshotUrl = _getBestAvailableSeasonHeadshot(goalie)}
                                    {@const headshotSettings = _getProspectHeadshotSettings(goalie, selectedSeason?.league || goalie.league)}
                                    <div 
                                        class="bg-white rounded-xl shadow-sm border border-emerald-200 overflow-hidden hover:shadow-md hover:border-emerald-300 transition-all group p-4"
                                    >
                                        <div class="flex items-center gap-4 mb-4">
                                            <div class="relative w-20 h-20 flex-shrink-0">
                                                <div class="w-full h-full rounded-full border-2 border-emerald-100 overflow-hidden bg-slate-50 relative z-10">
                                                    <PlayerHeadshot
                                                        playerId={_getBestFallbackPlayerId(goalie)}
                                                        explicitUrl={headshotUrl}
                                                        teamAbbrev={goalie.nhlRights}
                                                        alt={goalie.name}
                                                        imageClass="w-full h-full object-cover object-top"
                                                        zoom={headshotSettings.zoom}
                                                        objectPosition={headshotSettings.objectPosition}
                                                        autoFocusFace={false}
                                                        fallbackClass="w-full h-full flex items-center justify-center text-2xl font-bold text-slate-400"
                                                        initials={goalie.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                                                        loading="lazy"
                                                    />
                                                </div>
                                                {#if goalie.type === 'draft2026' || _hasKnownNhlRights(goalie)}
                                                    <div class="absolute -bottom-1 -right-1 z-20 bg-white rounded-full p-1 shadow-sm border border-emerald-100">
                                                        <div class="w-7 h-7 flex items-center justify-center">
                                                            {#if goalie.type === 'draft2026'}
                                                                <span class="text-[10px] font-black text-amber-600">#{goalie.draftRank}</span>
                                                            {:else if _getDisplayNhlRights(goalie.nhlRights)}
                                                                <TeamLogo team={_getDisplayNhlRights(goalie.nhlRights)} size="24" />
                                                            {/if}
                                                        </div>
                                                    </div>
                                                {/if}
                                            </div>
                                            
                                            <div class="min-w-0">
                                                <div class="flex items-center gap-2 mb-1">
                                                    <div class="inline-block bg-emerald-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                                                        {selectedSeason?.league || goalie.league}
                                                    </div>
                                                    {#if goalie.type === 'draft2026'}
                                                        <div class="inline-block bg-amber-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                                                            Draft 2026
                                                        </div>
                                                    {/if}
                                                </div>
                                                <h3 class="text-base font-bold text-slate-900 truncate">{goalie.name}</h3>
                                                <div class="space-y-1 text-xs text-slate-500">
                                                    <div class="truncate">{selectedSeason?.team || goalie.currentTeam}</div>
                                                    <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
                                                        {#if goalie.birthDate}
                                                            <span>{new Date().getFullYear() - new Date(goalie.birthDate).getFullYear()} vuotta</span>
                                                        {/if}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {#if _getSeasonSelectorEntries(goalie).length > 1}
                                            <div class="mb-3 flex flex-wrap gap-2">
                                                {#each _getSeasonSelectorEntries(goalie) as { entry, index }}
                                                    <button
                                                        class={`rounded-full border px-2.5 py-1 text-[10px] font-semibold transition-colors ${
                                                            _getSelectedSeasonIndex(goalie) === index
                                                                ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                                                                : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300 hover:text-slate-700'
                                                        }`}
                                                        onclick={() => _selectSeasonEntry(goalie, index)}
                                                        type="button"
                                                    >
                                                        {entry.league} {entry.gp || 0} GP
                                                    </button>
                                                {/each}
                                            </div>
                                        {/if}

                                        {#if goalie.type === 'draft2026'}
                                            <!-- Draft prospect stats -->
                                            <div class="grid grid-cols-4 gap-2 bg-amber-50/50 rounded-lg p-3 text-center border border-amber-100/50">
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">GP</div>
                                                    <div class="font-mono font-bold text-slate-700">{selectedSeason?.gp || 0}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">SV%</div>
                                                    <div class="font-mono font-bold text-emerald-600">{selectedSeason?.savePct ? selectedSeason.savePct.toFixed(3) : '-'}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">GAA</div>
                                                    <div class="font-mono font-bold text-amber-600">{selectedSeason?.gaa ? selectedSeason.gaa.toFixed(2) : '-'}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">SO</div>
                                                    <div class="font-mono font-bold text-slate-900">{selectedSeason?.shutouts || 0}</div>
                                                </div>
                                            </div>
                                        {:else}
                                            <!-- Regular goalie stats -->
                                            <div class="grid grid-cols-4 gap-2 bg-emerald-50/50 rounded-lg p-3 text-center border border-emerald-100/50">
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">GP</div>
                                                    <div class="font-mono font-bold text-slate-700">{unifiedStats?.gp || selectedSeason?.gp || 0}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">SV%</div>
                                                    <div class="font-mono font-bold text-emerald-600">{_formatGoalieStat(unifiedStats?.savePct ?? selectedSeason?.savePct, 3)}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">GAA</div>
                                                    <div class="font-mono font-bold text-amber-600">{_formatGoalieStat(unifiedStats?.gaa ?? selectedSeason?.gaa, 2)}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">SO</div>
                                                    <div class="font-mono font-bold text-slate-900">{unifiedStats?.shutouts ?? selectedSeason?.shutouts ?? 0}</div>
                                                </div>
                                            </div>
                                        {/if}
                                    </div>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            {/if}

            <!-- Related Links -->
            <div class="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4">
                <a 
                    href="{base}/scouting"
                    class="flex items-center gap-4 bg-white rounded-xl border border-slate-200 p-6 hover:shadow-md hover:border-blue-200 transition-all group"
                >
                    <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <h3 class="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">Scouting Reports</h3>
                        <p class="text-sm text-slate-500">Yksityiskohtaiset analyysit lupaavimmista pelaajista</p>
                    </div>
                    <svg class="w-5 h-5 text-slate-400 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                </a>
                
                <a 
                    href="{base}/drafts"
                    class="flex items-center gap-4 bg-white rounded-xl border border-slate-200 p-6 hover:shadow-md hover:border-blue-200 transition-all group"
                >
                    <div class="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                        <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z"/>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <h3 class="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">Draft-historia</h3>
                        <p class="text-sm text-slate-500">Suomalaisten varausten historia ja tilastot</p>
                    </div>
                    <svg class="w-5 h-5 text-slate-400 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                </a>
            </div>

            <!-- Data Sources -->
            <div class="mt-12 pt-8 border-t border-slate-200">
                <div class="text-center">
                    <h3 class="text-sm font-semibold text-slate-900 mb-3">Tietolähteet</h3>
                    <div class="flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-slate-500">
                        <span>• NHL API: Pelaajatiedot & tilastot</span>
                        <span>• NHL Central Scouting: Draft 2026 ranking</span>
                        <span>• EliteProspects: Nuorten sarjatiedot</span>
                        <span>• Liiga, SHL, AHL: Kausitilastot</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-4">
                        Päivitetty: {new Date().toLocaleDateString('fi-FI')} • 
                        Näytetään {activeProspects.length + (activeFilter === 'all' ? (globalThis.$draftRankings.north_american_skaters?.length || 0) + (globalThis.$draftRankings.international_skaters?.length || 0) : 0)} lupausta
                    </p>
                </div>
            </div>
        </div>
    </div>
