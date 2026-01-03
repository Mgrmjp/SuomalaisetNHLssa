<script>
import ComprehensivePlayerDetails from '$lib/components/game/ComprehensivePlayerDetails.svelte'
import { onMount } from 'svelte'
import { base } from '$app/paths'
import { games } from '$lib/stores/gameData.js'
import { formatGameMatchup, formatGameVenue } from '$lib/utils/gameFormatHelpers.mjs'
import { getTeamColorVariables } from '$lib/utils/teamColors.js'
import { isPlayerGameLive, shouldShowGameResult } from '$lib/utils/gameStateHelpers.mjs'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import './PlayerCard.css'

export let player

// Reactive variables for player photo
let playerPhotoUrl = null
let _photoError = false
let _imageLoading = true
let _lqipUrl = null

// Get player headshot URL
function getPlayerHeadshotUrl(playerId) {
    if (!playerId) return null
    return `${base}/headshots/thumbs/${playerId}.jpg`
}

// Generate LQIP (Low Quality Image Placeholder)
function _generateLQIP(playerId) {
    if (!playerId) return null
    // Create a simple colored rectangle as LQIP based on player ID
    const canvas = document.createElement('canvas')
    canvas.width = 64
    canvas.height = 64
    const ctx = canvas.getContext('2d')

    // Generate color based on player ID
    const hue = (parseInt(playerId, 10) * 137.508) % 360
    ctx.fillStyle = `hsl(${hue}, 30%, 85%)`
    ctx.fillRect(0, 0, 64, 64)

    return canvas.toDataURL()
}

// Preload player image
function preloadPlayerImage(playerId) {
    if (!playerId) return

    _imageLoading = true
    playerPhotoUrl = null // Reset full image

    // Set LQIP immediately
    _lqipUrl = getPlayerHeadshotUrl(playerId)

    // Load full image after delay
    setTimeout(() => {
        const img = new Image()
        const url = player.headshot_url

        img.onload = () => {
            playerPhotoUrl = url
            _photoError = false
            _imageLoading = false
        }

        img.onerror = () => {
            _photoError = true
            playerPhotoUrl = null
            _imageLoading = false
        }

        img.src = url
    }, 500)
}

// Preload image when player changes
$: if (player?.playerId) {
    preloadPlayerImage(player.playerId)
}
let _photoLoading = true

// Load player photo when component mounts or player changes
$: if (player?.playerId) {
    loadPlayerPhoto(player.playerId, player.headshot_url)
}

/**
 * Load player photo from our API, falling back to precomputed headshot_url if available
 */
async function loadPlayerPhoto(_playerId, precomputedUrl) {
    // If we already have a precomputed URL from data, use it first
    if (precomputedUrl) {
        playerPhotoUrl = precomputedUrl
        _photoLoading = false
        _photoError = false
        return
    }

    // If no precomputed URL is available, skip network fetch to avoid 404 spam in dev/offline
    _photoLoading = false
    _photoError = true
    playerPhotoUrl = null
}

let showSeasonStats = false
let showComprehensiveDetails = false
let _isLogoHovered = false
let isFlipped = false

// Convert hex to rgba with opacity for subtle borders
function _hexToRgba(hex, opacity = 0.7) {
    if (!hex || !hex.startsWith('#')) return `rgba(0, 0, 0, ${opacity})`

    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    if (!result) return `rgba(0, 0, 0, ${opacity})`

    const r = parseInt(result[1], 16)
    const g = parseInt(result[2], 16)
    const b = parseInt(result[3], 16)

    return `rgba(${r}, ${g}, ${b}, ${opacity})`
}

// Team names are now fetched from API and stored in team_full field
function getTeamWithCity(teamAbbrev) {
    if (!teamAbbrev) return 'Unknown Team'
    // Use team_full from API data if available, otherwise fallback to abbreviation
    const fullTeamName = player?.team_full || player?.opponent_full
    if (fullTeamName && fullTeamName !== teamAbbrev) {
        return fullTeamName
    }
    return teamAbbrev
}

function _toggleSeasonStats(event) {
    if (event) {
        event.preventDefault()
        event.stopPropagation()
    }
    showSeasonStats = !showSeasonStats
}

function _closeSeasonStats(event) {
    event.preventDefault()
    event.stopPropagation()
    showSeasonStats = false
}

function _toggleComprehensiveDetails(event) {
    if (event) {
        event.preventDefault()
        event.stopPropagation()
    }
    showComprehensiveDetails = !showComprehensiveDetails
}

function _handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
        showSeasonStats = false
        showComprehensiveDetails = false
    }
}

function toggleFlip() {
    isFlipped = !isFlipped
}

function _handleCardClick(event) {
    // Only flip if clicking on the card itself, not on buttons or interactive elements
    if (event.target.closest('button') || event.target.closest('a')) {
        return
    }
    toggleFlip()
}

$: displayName = player.name?.default || player.name || 'Unknown Player'
$: isLive = isPlayerGameLive(player, gamesData)
$: showResult = shouldShowGameResult(player, gamesData)
$: teamWithCity = getTeamWithCity(player.team || 'NHL')
$: opponentWithCity = getTeamWithCity(player.opponent || 'NHL')
$: playerHeadshot = playerPhotoUrl
$: gamesData = $games

// Team color variables
let _teamColorVars = {
    '--team-primary-color': '#000000',
    '--team-secondary-color': '#FFFFFF',
    '--team-accent-color': '#000000',
}

// Animation control
const _enableAnimatedBorders = true

// Load team colors when component mounts or player changes
onMount(async () => {
    if (player?.team) {
        try {
            _teamColorVars = await getTeamColorVariables(player.team)
        } catch (error) {
            console.warn(`Failed to load team colors for ${player.team}:`, error)
        }
    }
})

// Update colors when player changes
$: if (player?.team) {
    loadTeamColors()
}

async function loadTeamColors() {
    if (player?.team) {
        try {
            _teamColorVars = await getTeamColorVariables(player.team)
        } catch (error) {
            console.warn(`Failed to load team colors for ${player.team}:`, error)
        }
    }
}
$: playerInitials = displayName
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase())
    .join('')
    .slice(0, 2)

// Calculate number of stats for responsive grid (skaters)
$: statCount = [
    player.goals > 0,
    player.assists > 0,
    player.points > 0,
    player.plus_minus !== undefined,
    (player.penalty_minutes || 0) > 0,
].filter(Boolean).length

$: skaterGridClass =
    statCount === 1
        ? 'player-card__stats-grid--single'
        : `player-card__stats-grid--skater-${Math.min(statCount, 5)}`

// Goalie stats count
$: goalieStatCount = [
    player.saves !== undefined,
    player.shots_against !== undefined,
    goalieSavePct !== null,
    (player.empty_net_goals || 0) > 0,
].filter(Boolean).length

$: goalieGridClass =
    goalieStatCount === 1
        ? 'player-card__stats-grid--single'
        : goalieStatCount === 2
          ? 'player-card__stats-grid--goalie-2'
          : goalieStatCount === 3
            ? 'player-card__stats-grid--goalie-3'
            : 'player-card__stats-grid--goalie-4'

// Goalie helpers
$: isGoalie =
    (player.position || '').toUpperCase() === 'G' ||
    (player.position || '').toUpperCase() === 'GOALIE'
$: goalieSavePct = getSavePercentage(player)

// Game result helpers
$: gameResult = player.game_result || ''
$: resultIndicator = getResultIndicator(gameResult)

function getResultIndicator(result) {
    switch (result) {
        case 'W':
            return {
                bg: 'bg-gradient-to-br from-green-500 to-green-600',
                text: 'W',
                label: 'Voitto',
                textColor: 'text-white',
                border: 'ring-green-300',
            }
        case 'SOW':
            return {
                bg: 'bg-gradient-to-br from-emerald-500 to-emerald-600',
                text: 'SV',
                label: 'Voitto VL',
                textColor: 'text-white',
                border: 'ring-emerald-300',
            }
        case 'L':
            return {
                bg: 'bg-gradient-to-br from-red-500 to-red-600',
                text: 'L',
                label: 'Häviö',
                textColor: 'text-white',
                border: 'ring-red-300',
            }
        case 'SOL':
            return {
                bg: 'bg-gradient-to-br from-rose-500 to-rose-600',
                text: 'SO',
                label: 'Häviö VL',
                textColor: 'text-white',
                border: 'ring-rose-300',
            }
        case 'OTW':
            return {
                bg: 'bg-gradient-to-br from-amber-500 to-orange-500',
                text: 'OT',
                label: 'Voitto JA',
                textColor: 'text-white',
                border: 'ring-amber-300',
            }
        case 'OTL':
            return {
                bg: 'bg-gradient-to-br from-orange-500 to-orange-600',
                text: 'OT',
                label: 'Häviö JA',
                textColor: 'text-white',
                border: 'ring-orange-300',
            }
        default:
            return {
                bg: 'bg-gradient-to-br from-gray-400 to-gray-500',
                text: '?',
                label: 'Ei tietoa',
                textColor: 'text-white',
                border: 'ring-gray-300',
            }
    }
}

function getSavePercentage(player) {
    const provided = player.save_percentage ?? player.savePercentage
    // Use provided percentage if it's a positive number
    if (typeof provided === 'number' && provided > 0) {
        // If it's already a percentage (like 0.857), convert to percentage format
        // If it's a percentage value (like 85.7), keep it as is
        return Number(provided > 1 ? provided : (provided * 100).toFixed(1))
    }

    const saves = Number(player.saves ?? player.goalie_saves)
    const shotsAgainst = Number(player.shots_against ?? player.shotsAgainst)

    if (Number.isFinite(saves) && Number.isFinite(shotsAgainst) && shotsAgainst > 0) {
        // Calculate and return as percentage (e.g., 85.7)
        return Number(((saves / shotsAgainst) * 100).toFixed(1))
    }

    return null
}
</script>

<div class="player-card__container relative w-full min-h-[320px]">
    <!-- Player Card -->
    <div class="player-card" class:flipped={isFlipped}>
        <div class="player-card__inner">
            <!-- Front of Card -->
            <div
                class="player-card__face player-card__face--front bg-white w-full overflow-hidden relative cursor-pointer rounded-lg shadow-lg"
                style={`border: 1.5px solid transparent; background: linear-gradient(white, white) padding-box, linear-gradient(135deg, ${_hexToRgba(_teamColorVars["--team-primary-color"], 0.7)}, ${_hexToRgba(_teamColorVars["--team-secondary-color"], 0.8)}, ${_hexToRgba(_teamColorVars["--team-accent-color"], 0.6)}) border-box; ${Object.entries(
                    _teamColorVars,
                )
                    .map(([key, value]) => `${key}: ${value}`)
                    .join("; ")}`}
                on:click={_handleCardClick}
                role="button"
                tabindex="0"
                on:keydown={(e) => e.key === "Enter" && _handleCardClick(e)}
                aria-label="Click to flip player card"
            >
                <!-- Enhanced Double Border -->
                <div class="player-card__border-outer"></div>
                <div
                    class="player-card__border-middle"
                    class:player-card__border-middle--animated={_enableAnimatedBorders}
                ></div>
                <div class="player-card__border-inner"></div>
                <div
                    class="player-card__content relative bg-white rounded-lg p-4 h-full flex flex-col overflow-visible"
                >
                    <div class="player-card__logo-bg team-logo-bg">
                        <TeamLogo team={player.team || "NHL"} size="100" />
                    </div>

                    <!-- Top Left Player Info -->
                    <div class="player-card__player-info absolute top-4 left-4 z-10">
                        <div class="player-card__player-header flex items-center gap-2">
                            <h3
                                class="player-card__player-name text-lg font-semibold text-gray-900"
                            >
                                {displayName}
                            </h3>
                        </div>
                        <div class="player-card__player-details text-sm text-gray-600 min-w-0">
                            {player.position && player.position !== "N/A"
                                ? player.position
                                : ""}{player.jersey_number
                                ? " #" + player.jersey_number
                                : ""}{player.position && player.position !== "N/A"
                                ? " • "
                                : ""}{teamWithCity}
                        </div>
                    </div>

                    <!-- Top Right Team Logo -->
                    <div class="player-card__team-logo absolute top-2 right-2 z-10">
                        <div
                            class="player-card__team-logo-container relative team-logo-container"
                            role="img"
                            aria-label={`Team logo for ${teamWithCity}`}
                            on:mouseenter={() => (_isLogoHovered = true)}
                            on:mouseleave={() => (_isLogoHovered = false)}
                            on:focus={() => (_isLogoHovered = true)}
                            on:blur={() => (_isLogoHovered = false)}
                            title={teamWithCity}
                        >
                            <!-- Filtered duplicate logo for shine effect - BEHIND main logo -->
                            <div
                                class="absolute inset-0 z-0 opacity-70 scale-125 transform-gpu filter drop-shadow-[0_0_12px_rgba(59,130,246,0.6)] brightness-110 saturate-150 hue-rotate-15 blur-sm"
                            >
                                <TeamLogo team={player.team || "NHL"} size="48" />
                            </div>
                            <!-- Main logo on top -->
                            <div class="relative z-10">
                                <TeamLogo team={player.team || "NHL"} size="48" />
                            </div>
                            {#if isLive}
                                <div class="player-card__live-indicator absolute -top-1 -right-1">
                                    <span
                                        class="player-card__live-badge bg-red-500 text-white text-xs font-bold px-2 py-1 rounded"
                                    >
                                        LIVE
                                    </span>
                                </div>
                            {/if}
                        </div>
                    </div>

                    <!-- Spacer for top content -->
                    <div class="h-20 mb-4"></div>

                    <!-- Game Stats -->
                    {#if isGoalie}
                        <div class="player-card__stats mb-4 w-full">
                            <div
                                class={`player-card__stats-grid ${goalieGridClass} grid gap-1 text-left w-full`}
                            >
                                {#if player.saves !== undefined}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--saves flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.saves}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Torjunnat
                                        </div>
                                    </div>
                                {/if}
                                {#if player.shots_against !== undefined}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--shots-against flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.shots_against}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Vastust. laukaukset
                                        </div>
                                    </div>
                                {/if}
                                {#if goalieSavePct !== null}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--save-pct flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {goalieSavePct}%
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Torj.%
                                        </div>
                                    </div>
                                {/if}
                                {#if (player.empty_net_goals || 0) > 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--empty-net-goals flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-red-600 truncate flex items-center justify-center gap-1"
                                        >
                                            🥅
                                            <span>{player.empty_net_goals}</span>
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-red-600 mt-1 truncate"
                                        >
                                            Tyhjä maali
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {:else if player.goals > 0 || player.assists > 0 || player.points > 0 || (player.penalty_minutes || 0) > 0 || player.plus_minus !== undefined || (player.empty_net_goals || 0) > 0}
                        <div class="player-card__stats mb-4 w-full">
                            <div
                                class={`player-card__stats-grid ${skaterGridClass} grid gap-1 text-left w-full`}
                            >
                                {#if player.goals > 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--goals flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.goals}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Maalit
                                        </div>
                                    </div>
                                {/if}
                                {#if player.assists > 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--assists flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.assists}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Syötöt
                                        </div>
                                    </div>
                                {/if}
                                {#if player.points > 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--points flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-finnish-blue-900 truncate"
                                        >
                                            {player.points}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-finnish-blue-600 mt-1 truncate"
                                        >
                                            Pisteet
                                        </div>
                                    </div>
                                {/if}
                                {#if (player.empty_net_goals || 0) > 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--empty-net-goals flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-red-600 truncate flex items-center justify-center gap-1"
                                        >
                                            🥅
                                            <span>{player.empty_net_goals}</span>
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-red-600 mt-1 truncate"
                                        >
                                            Tyhjä maali
                                        </div>
                                    </div>
                                {/if}
                                {#if player.plus_minus !== undefined}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--plus-minus flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.plus_minus > 0 ? "+" : ""}{player.plus_minus}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            +/-
                                        </div>
                                    </div>
                                {/if}
                                {#if (player.penalty_minutes || 0) > 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--penalty-minutes flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.penalty_minutes}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            R.min
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/if}

                    <!-- Game Score -->
                    {#if player.game_score}
                        <div class="player-card__game-score">
                            <div
                                class="player-card__game-matchup text-sm font-medium text-gray-700 mb-1 text-center"
                            >
                                {formatGameMatchup(player, gamesData)}
                            </div>
                            <div
                                class="player-card__game-score-display flex items-center justify-center space-x-3"
                            >
                                {#if gamesData && gamesData.findGameById && player.game_id}
                                    {@const game = gamesData.findGameById(player.game_id)}
                                    {#if game && game.homeTeam && game.awayTeam && game.homeScore !== undefined && game.awayScore !== undefined}
                                        <!-- Away team score with logo as background -->
                                        <div
                                            class="player-card__team-score player-card__team-score--away relative flex items-center justify-center text-lg font-bold"
                                            style="width: 60px; height: 40px;"
                                        >
                                            <div
                                                class="player-card__team-score-logo-bg player-card__team-score-logo-bg--away absolute inset-0"
                                                style="background-image: url('{base}/nhl-logos/{game.awayTeam.toLowerCase()}.svg'); background-size: 32px; background-position: center; background-repeat: no-repeat; opacity: 0.15;"
                                            ></div>
                                            <span class="player-card__team-score-value relative z-10">{game.awayScore}</span>
                                        </div>
                                        <!-- VS separator -->
                                        <span class="player-card__score-separator text-sm text-gray-500 mx-1">-</span>
                                        <!-- Home team score with logo as background -->
                                        <div
                                            class="player-card__team-score player-card__team-score--home relative flex items-center justify-center text-lg font-bold"
                                            style="width: 60px; height: 40px;"
                                        >
                                            <div
                                                class="player-card__team-score-logo-bg player-card__team-score-logo-bg--home absolute inset-0"
                                                style="background-image: url('{base}/nhl-logos/{game.homeTeam.toLowerCase()}.svg'); background-size: 32px; background-position: center; background-repeat: no-repeat; opacity: 0.15;"
                                            ></div>
                                            <span class="player-card__team-score-value relative z-10">{game.homeScore}</span>
                                        </div>
                                    {:else}
                                        <!-- Fallback to original score display -->
                                        <div class="player-card__score text-lg font-bold">
                                            {formatGameScore(player, gamesData)}
                                        </div>
                                    {/if}
                                {:else}
                                    <!-- Fallback to original score display -->
                                    <div class="player-card__score text-lg font-bold">
                                        {formatGameScore(player, gamesData)}
                                    </div>
                                {/if}
                            </div>
                            {#if formatGameVenue(player)}
                                <div
                                    class="player-card__game-venue text-xs text-gray-500 mt-2 text-center min-w-0"
                                >
                                    📍 {formatGameVenue(player)}
                                </div>
                            {/if}
                        </div>
                    {/if}
                    <div
                        class="player-card__footer mt-auto flex items-center justify-between pt-3 border-t border-gray-100"
                    >
                        <!-- Enhanced Result Indicator -->
                        {#if showResult && gameResult}
                            <div class="relative group">
                                <div
                                    class={`w-6 h-6 rounded-lg ${resultIndicator.bg} ${resultIndicator.textColor} flex items-center justify-center text-xs font-bold shadow-lg transition-all duration-200`}
                                    title={resultIndicator.label}
                                >
                                    {resultIndicator.text}
                                </div>
                            </div>
                        {/if}

                        <button
                            class="player-card__details-button-inline"
                            on:click={_toggleComprehensiveDetails}
                            on:keydown={(e) => e.key === "Enter" && _toggleComprehensiveDetails()}
                            aria-label="Show comprehensive player details for {displayName}"
                            title="Näytä kattavat tiedot"
                        >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                <path
                                    d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"
                                />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Back of Card -->
            <div
                class="player-card__face player-card__face--back bg-white w-full overflow-hidden relative cursor-pointer rounded-lg shadow-lg"
                style={`border: 1.5px solid transparent; background: linear-gradient(white, white) padding-box, linear-gradient(225deg, ${_hexToRgba(_teamColorVars["--team-accent-color"], 0.6)}, ${_hexToRgba(_teamColorVars["--team-secondary-color"], 0.8)}, ${_hexToRgba(_teamColorVars["--team-primary-color"], 0.7)}) border-box; ${Object.entries(
                    _teamColorVars,
                )
                    .map(([key, value]) => `${key}: ${value}`)
                    .join("; ")}`}
                on:click={_handleCardClick}
                role="button"
                tabindex="0"
                on:keydown={(e) => e.key === "Enter" && _handleCardClick(e)}
                aria-label="Click to flip player card back"
            >
                <!-- Enhanced Double Border -->
                <div class="player-card__border-outer player-card__border-outer--back"></div>
                <div
                    class="player-card__border-middle player-card__border-middle--back"
                    class:player-card__border-middle--animated={_enableAnimatedBorders}
                ></div>
                <div class="player-card__border-inner player-card__border-inner--back"></div>
                <div
                    class="player-card__content relative bg-white rounded-lg h-full flex flex-col overflow-visible"
                >
                    <!-- Top Left Player Info -->
                    <div class="player-card__player-info absolute top-4 left-4 z-10">
                        <div class="player-card__player-header flex items-center gap-2">
                            <h3
                                class="player-card__player-name text-lg font-semibold text-gray-900"
                            >
                                {displayName}
                            </h3>
                        </div>
                        <div class="player-card__player-details text-sm text-gray-600 min-w-0">
                            {player.position && player.position !== "N/A"
                                ? player.position
                                : ""}{player.jersey_number
                                ? " #" + player.jersey_number
                                : ""}{player.position && player.position !== "N/A"
                                ? " • "
                                : ""}{teamWithCity}
                        </div>
                    </div>

                    <!-- Top Right Team Logo -->
                    <div class="player-card__team-logo absolute top-2 right-2 z-10">
                        <!-- Filtered duplicate logo for shine effect - BEHIND main logo -->
                        <div
                            class="absolute inset-0 z-0 opacity-70 scale-125 transform-gpu filter drop-shadow-[0_0_12px_rgba(59,130,246,0.6)] brightness-110 saturate-150 hue-rotate-15 blur-sm"
                        >
                            <TeamLogo team={player.team || "NHL"} size="48" />
                        </div>
                        <!-- Main logo on top -->
                        <div class="relative z-10">
                            <TeamLogo team={player.team || "NHL"} size="48" />
                        </div>
                    </div>

                    <!-- Spacer for top content -->
                    <div class="player-card__spacer h-20 mb-4"></div>

                    <!-- Additional Stats and Time on Ice Wrapper -->
                    <div class="flex-grow p-4 flex flex-col">
                        <!-- Additional Stats -->
                        <div class="player-card__advanced-stats mb-4 w-full">
                            <div
                                class="player-card__advanced-stats-grid grid gap-y-4 gap-x-3 text-left w-full"
                            >
                                {#if player.shots !== undefined && player.shots >= 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--shots flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.shots}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Laukaukset
                                        </div>
                                    </div>
                                {/if}
                                {#if player.hits !== undefined && player.hits >= 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--hits flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.hits}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Taklaukset
                                        </div>
                                    </div>
                                {/if}
                                {#if player.blocked_shots !== undefined && player.blocked_shots >= 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--blocked-shots flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.blocked_shots}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Blokit
                                        </div>
                                    </div>
                                {/if}
                                {#if player.takeaways !== undefined && player.takeaways >= 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--takeaways flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.takeaways}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Riistot
                                        </div>
                                    </div>
                                {/if}
                                {#if player.giveaways !== undefined && player.giveaways >= 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--giveaways flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.giveaways}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Menetykset
                                        </div>
                                    </div>
                                {/if}
                                {#if (player.empty_net_goals || 0) > 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--empty-net-goals flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-red-600 truncate flex items-center justify-center gap-1"
                                        >
                                            🥅
                                            <span>{player.empty_net_goals}</span>
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-red-600 mt-1 truncate"
                                        >
                                            Tyhjä maali
                                        </div>
                                    </div>
                                {/if}
                                {#if player.faceoff_wins !== undefined && player.faceoffs_taken !== undefined && player.faceoffs_taken > 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--faceoffs flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.faceoff_wins}/{player.faceoffs_taken}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Vahingot / FO
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        </div>

                        <!-- Time on Ice -->
                        {#if player.time_on_ice}
                            <div class="player-card__time-on-ice text-center">
                                <div
                                    class="player-card__time-on-ice-text text-lg font-bold text-gray-900"
                                >
                                    Aika kentällä: <span class="player-card__time-on-ice-value"
                                        >{player.time_on_ice}</span
                                    >
                                </div>
                            </div>
                        {/if}

                        <div
                            class="player-card__footer mt-auto flex items-center justify-between pt-3 border-t border-gray-100"
                        >
                            <!-- Enhanced Result Indicator -->
                            {#if showResult && gameResult}
                                <div class="relative group">
                                    <div
                                        class={`w-6 h-6 rounded-lg ${resultIndicator.bg} ${resultIndicator.textColor} flex items-center justify-center text-xs font-bold shadow-lg transition-all duration-200`}
                                        title={resultIndicator.label}
                                    >
                                        {resultIndicator.text}
                                    </div>
                                </div>
                            {/if}

                            <button
                                class="player-card__details-button-inline"
                                on:click={_toggleComprehensiveDetails}
                                on:keydown={(e) =>
                                    e.key === "Enter" && _toggleComprehensiveDetails()}
                                aria-label="Show comprehensive player details for {displayName}"
                                title="Näytä kattavat tiedot"
                            >
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                    <path
                                        d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"
                                    />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Season Stats Modal -->
    {#if showSeasonStats}
        <div
            class="player-card__modal-overlay fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50"
            role="button"
            tabindex="0"
            on:click={_handleBackdropClick}
            on:keydown={(e) =>
                (e.key === "Escape" || e.key === "Enter" || e.key === " ") &&
                _handleBackdropClick(e)}
        >
            <div
                class="player-card__modal-content bg-white rounded-lg max-w-4xl w-full mx-4 max-h-screen overflow-y-auto"
            >
                <div class="player-card__modal-header p-6">
                    <div
                        class="player-card__modal-title-row flex items-center justify-between mb-6"
                    >
                        <div class="flex items-center gap-4">
                            <div class="player-card__modal-avatar">
                                {#if playerPhotoUrl}
                                    <img
                                        src={playerPhotoUrl}
                                        alt={`Kuva pelaajasta ${displayName}`}
                                        class="player-card__modal-photo"
                                        loading="lazy"
                                    />
                                {:else if _lqipUrl}
                                    <img
                                        src={_lqipUrl}
                                        alt={`Kuva pelaajasta ${displayName}`}
                                        class="player-card__modal-photo blur-sm"
                                        loading="lazy"
                                    />
                                {:else}
                                    <div class="player-card__modal-initials" aria-hidden="true">
                                        {playerInitials}
                                    </div>
                                {/if}
                            </div>
                            <div>
                                <h2
                                    class="player-card__modal-title text-2xl font-bold text-gray-900"
                                >
                                    {displayName} - Kauden tilastot
                                </h2>
                                <div class="player-card__modal-subtitle text-sm text-gray-600">
                                    {player.position && player.position !== "N/A"
                                        ? player.position
                                        : "Pelaaja"}
                                    {player.jersey_number ? ` #${player.jersey_number}` : ""}
                                    {player.team_full || player.team
                                        ? ` • ${player.team_full || player.team}`
                                        : ""}
                                </div>
                            </div>
                        </div>
                        <button
                            type="button"
                            class="player-card__modal-close text-gray-400 hover:text-gray-600"
                            on:click={_closeSeasonStats}
                            aria-label="Sulje"
                        >
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <path
                                    d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
                                />
                            </svg>
                        </button>
                    </div>

                    <!-- Season Stats Content -->
                    <div class="player-card__modal-body text-center text-gray-500">
                        <p>Kauden tilastot eivät ole vielä saatavilla</p>
                        <p class="text-sm mt-2">Tämä toiminto kehitetään tulevaisuudessa</p>
                    </div>

                    <div
                        class="player-card__modal-footer mt-6 pt-4 border-t border-gray-200 flex justify-end"
                    >
                        <button
                            type="button"
                            class="player-card__modal-close-button bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                            on:click={_closeSeasonStats}
                        >
                            Sulje
                        </button>
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <!-- Comprehensive Details Modal Component -->
    <ComprehensivePlayerDetails {player} bind:showComprehensiveDetails />
</div>
