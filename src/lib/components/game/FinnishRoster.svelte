<script>
// @ts-nocheck
import { onMount } from 'svelte'
import { fetchLocalJSON } from '$lib/utils/apiHelpers.js'
import { correctFullName } from '$lib/utils/finnishNameUtils.js'
import teamMapping from '$lib/utils/teamMapping.js'

// State
/** @type {Array<Object>} */
let _players = []
/** @type {Map<string, Array<Object>>} */
let _teamsMap = new Map()
/** @type {Array<Object>} */
let _inactivePlayers = []
/** @type {boolean} */
let _loading = true
/** @type {string|null} */
let _error = null

// Extract team abbreviation from headshot URL
function extractTeamFromHeadshot(headshot) {
    if (!headshot || typeof headshot !== 'string') return ''
    const match = headshot.match(/\/mugs\/nhl\/\d+\/([A-Z]+)\/\d+\.png/)
    return match ? match[1] : ''
}

// Load and process Finnish players data
async function loadFinnishRoster() {
    _loading = true
    _error = null

    try {
        // Load from the cache JSON file directly
        const rawData = await fetchLocalJSON('/data/players/finnish-roster.json')

        if (!rawData) {
            throw new Error('Failed to load Finnish players data')
        }

        // Handle cache format (object keyed by player ID)
        let playerList
        if (Array.isArray(rawData)) {
            playerList = rawData.map((p) => ({
                ...p,
                name: correctFullName(p.name),
            }))
        } else {
            // Convert object to array and normalize
            playerList = Object.values(rawData).map((p) => {
                const teamFromHeadshot = extractTeamFromHeadshot(p.headshot)
                const originalName = p.name
                const correctedName = correctFullName(originalName)
                return {
                    id: p.playerId || p.id,
                    name: correctedName,
                    position: p.position,
                    team: p.teamAbbrev || p.team || teamFromHeadshot || '',
                    team_abbrev: p.teamAbbrev || p.team || teamFromHeadshot || '',
                    jersey_number: p.sweaterNumber || p.jersey_number,
                    birth_date: p.birthDate || p.birth_date || null,
                    is_active: p.isActive !== false,
                    games_played: p.gamesPlayed ?? null,
                    lastTeam: p.lastTeam || null,
                }
            })
        }

        // Group active players by team and move UNKNOWN/non-active into inactive list
        const teams = new Map()
        const inactive = []

        for (const player of playerList) {
            const teamAbbr = player.team_abbrev || player.team || 'UNKNOWN'
            const isInactive = !player.is_active || teamAbbr === 'UNKNOWN'

            if (isInactive) {
                inactive.push({ ...player, team_abbrev: teamAbbr })
                continue
            }

            if (!teams.has(teamAbbr)) {
                teams.set(teamAbbr, [])
            }
            teams.get(teamAbbr).push(player)
        }

        // Sort teams alphabetically by full name
        const sortedTeams = new Map(
            [...teams.entries()].sort((a, b) => {
                const aName = teamMapping[a[0]] || a[0]
                const bName = teamMapping[b[0]] || b[0]
                return aName.localeCompare(bName)
            })
        )

        _teamsMap = sortedTeams

        const inactiveWithLastTeam = await Promise.all(
            inactive.map((player) => {
                if (
                    player.team_abbrev &&
                    player.team_abbrev !== 'UNKNOWN' &&
                    player.team_abbrev !== ''
                ) {
                    return { ...player, last_team: player.team_abbrev }
                }
                return { ...player, last_team: player.lastTeam || null }
            })
        )

        _inactivePlayers = inactiveWithLastTeam.sort(
            (a, b) => (b.games_played ?? 0) - (a.games_played ?? 0)
        )
        _players = playerList
    } catch (err) {
        console.error('Error loading Finnish roster:', err)
        _error = 'Failed to load Finnish players roster'
    } finally {
        _loading = false
    }
}

onMount(() => {
    loadFinnishRoster()
})

// Get sorted players for a team (by position: C, LW, RW, D, G)
function _sortPlayersByPosition(teamPlayers) {
    const positionOrder = { C: 1, LW: 2, RW: 3, D: 4, G: 5 }
    return [...teamPlayers].sort((a, b) => {
        const aPos = (a.position || 'Z').toUpperCase()
        const bPos = (b.position || 'Z').toUpperCase()
        const aOrder = positionOrder[aPos] ?? 99
        const bOrder = positionOrder[bPos] ?? 99
        if (aOrder !== bOrder) return aOrder - bOrder
        return (a.name || '').localeCompare(b.name || '')
    })
}

// Get position display name
function _getPositionName(pos) {
    const positionNames = {
        C: 'Keskushyökkääjä',
        LW: 'Vasen laitahyökkääjä',
        RW: 'Oikea laitahyökkääjä',
        D: 'Puolustaja',
        G: 'Maalivahti',
    }
    return positionNames[pos?.toUpperCase()] || pos || ''
}

// Format birth date for display
function _formatBirthDate(dateStr) {
    if (!dateStr) return null
    const date = new Date(dateStr)
    return `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()}`
}
</script>

<div class="finnish-roster">
    {#if _loading}
        <div class="py-12 text-center">
            <LoadingSpinner message="Ladataan suomalaisten NHL-pelaajien luetteloa..." />
        </div>
    {:else if _error}
        <ErrorBoundary>
            <div class="py-12 text-center">
                <p class="text-red-600 mb-4">{_error}</p>
                <button
                    on:click={loadFinnishRoster}
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    Yritä uudelleen
                </button>
            </div>
        </ErrorBoundary>
    {:else}
        <div class="roster-header mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Suomalaiset NHL-pelaajat</h2>
            <p class="text-gray-600">
                Yhteensä {_players.length} suomalaista pelaajaa NHL:ssä (pelaamattomat ja loukkaantuneet
                eivät mukana)
            </p>
        </div>

        <div class="teams-grid">
            {#each Array.from(_teamsMap.entries()) as [teamAbbr, teamPlayers]}
                {@const teamName = teamMapping[teamAbbr] || teamAbbr}
                {@const sortedPlayers = _sortPlayersByPosition(teamPlayers)}
                <div class="team-card" style:--team-primary-color="#1e40af">
                    <!-- Team Header -->
                    <div class="team-header">
                        <div class="team-logo-wrapper">
                            <TeamLogo team={teamAbbr} size="64" />
                        </div>
                        <div class="team-info">
                            <h3 class="team-name">{teamName}</h3>
                            <p class="player-count">
                                {teamPlayers.length} pelaaj{teamPlayers.length === 1 ? "a" : "aa"}
                            </p>
                        </div>
                    </div>

                    <!-- Players List -->
                    <div class="players-list">
                        {#each sortedPlayers as player}
                            <div class="player-row">
                                <span class="player-number">{player.jersey_number ?? "-"}</span>
                                <span class="player-name">{player.name}</span>
                                <span class="player-position">{player.position || "-"}</span>
                                <span class="player-birthdate">
                                    {#if player.birth_date}
                                        {_formatBirthDate(player.birth_date)}
                                    {:else}
                                        -
                                    {/if}
                                </span>
                            </div>
                        {/each}
                    </div>
                </div>
            {/each}
        </div>

        {#if _inactivePlayers.length > 0}
            <div class="inactive-section mt-8">
                <h3 class="text-xl font-bold text-gray-700 mb-4">Ei joukkueessa / Vanhat pelaajat</h3>
                <div class="inactive-list">
                    <div class="player-row inactive-header">
                        <span class="player-number">#</span>
                        <span class="player-name">Pelaaja</span>
                        <span class="player-position">Pos</span>
                        <span class="player-gp">GP</span>
                        <span class="player-team">Viimeinen</span>
                    </div>
                    {#each _inactivePlayers as player}
                        <div class="player-row inactive">
                            <span class="player-number">{player.jersey_number ?? "-"}</span>
                            <span class="player-name">{player.name}</span>
                            <span class="player-position">{player.position || "-"}</span>
                            <span class="player-gp">{player.games_played ?? "-"}</span>
                            <span class="player-team">
                                {#if player.last_team && player.last_team !== 'UNKNOWN'}
                                    {teamMapping[player.last_team] || player.last_team}
                                {:else}
                                    Ei NHL:ssa
                                {/if}
                            </span>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}
    {/if}
</div>

<style>
    .finnish-roster {
        padding: 0;
    }

    .roster-header {
        text-align: center;
    }

    .teams-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 1.5rem;
        align-items: start;
    }

    .team-card {
        background: white;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        transition: box-shadow 0.2s ease;
        border: 1px solid #e5e7eb;
    }

    .team-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .team-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.25rem;
        background: linear-gradient(135deg, #f3f4f6 0%, #ffffff 100%);
        border-bottom: 1px solid #e5e7eb;
    }

    .team-logo-wrapper {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 56px;
        height: 56px;
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    .team-info {
        flex: 1;
        min-width: 0;
    }

    .team-name {
        font-size: 1.125rem;
        font-weight: 700;
        color: #111827;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .player-count {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0;
    }

    .players-list {
        padding: 0.5rem 0;
    }

    .player-row {
        display: grid;
        grid-template-columns: 2.5rem 1fr 2rem 5rem;
        gap: 0.5rem;
        padding: 0.5rem 1.25rem;
        border-bottom: 1px solid #f3f4f6;
        align-items: center;
        font-size: 0.875rem;
    }

    .player-row:last-child {
        border-bottom: none;
    }

    .player-row:hover {
        background: #f9fafb;
    }

    .player-number {
        font-weight: 600;
        color: #374151;
        text-align: center;
        font-variant-numeric: tabular-nums;
    }

    .player-name {
        font-weight: 500;
        color: #111827;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .player-position {
        font-weight: 600;
        color: #6b7280;
        text-align: center;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.025em;
    }

    .player-birthdate {
        color: #9ca3af;
        font-size: 0.75rem;
        text-align: right;
        white-space: nowrap;
    }

    .inactive-section {
        border-top: 2px solid #e5e7eb;
        padding-top: 1.5rem;
    }

    .inactive-list {
        background: #f9fafb;
        border-radius: 0.75rem;
        border: 1px solid #e5e7eb;
        overflow: hidden;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    }

    .player-row.inactive-header {
        font-size: 0.7rem;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: #f3f4f6;
        border-bottom: 1px solid #e5e7eb;
        grid-template-columns: 2.5rem 1fr 2rem 3rem 5rem;
    }

    .player-row.inactive {
        background: #f9fafb;
        grid-template-columns: 2.5rem 1fr 2rem 3rem 5rem;
    }

    .player-row.inactive:hover {
        background: #f3f4f6;
    }

    .player-gp {
        color: #6b7280;
        font-size: 0.75rem;
        text-align: center;
        font-variant-numeric: tabular-nums;
    }

    .player-team {
        color: #9ca3af;
        font-size: 0.75rem;
        text-align: right;
        white-space: nowrap;
    }

    /* Responsive adjustments */
    @media (max-width: 640px) {
        .teams-grid {
            grid-template-columns: 1fr;
        }

        .player-row {
            grid-template-columns: 2rem 1fr 1.5rem 4rem;
            gap: 0.25rem;
            padding: 0.5rem 0.75rem;
        }

        .player-row.inactive {
            grid-template-columns: 2rem 1fr 1.5rem 2.5rem 4rem;
        }

        .team-header {
            padding: 1rem;
        }
    }
</style>
