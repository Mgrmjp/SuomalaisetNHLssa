<script>
import { base } from '$app/paths'

export let player
export let showComprehensiveDetails = false

// Reactive variables for player photo
let _playerPhotoUrl = null
let _photoError = false
let _imageLoading = true
let _lqipUrl = null
let _imageLoaded = false

// Get player headshot URL
function getPlayerHeadshotUrl(playerId) {
    if (!playerId) return null
    return `${base}/headshots/thumbs/${playerId}.jpg`
}

// Generate LQIP (Low Quality Image Placeholder)
function _generateLQIP(playerId) {
    if (!playerId) return null
    const canvas = document.createElement('canvas')
    canvas.width = 64
    canvas.height = 64
    const ctx = canvas.getContext('2d')

    const hue = (parseInt(playerId, 10) * 137.508) % 360
    ctx.fillStyle = `hsl(${hue}, 30%, 85%)`
    ctx.fillRect(0, 0, 64, 64)

    return canvas.toDataURL()
}

// Preload player image
function preloadPlayerImage(playerId) {
    if (!playerId) return

    _imageLoading = true
    _imageLoaded = false
    _playerPhotoUrl = null

    // Set LQIP immediately
    _lqipUrl = getPlayerHeadshotUrl(playerId)

    // Load full image after delay
    setTimeout(() => {
        const img = new Image()
        const url = player.headshot_url

        img.onload = () => {
            _playerPhotoUrl = url
            _photoError = false
            _imageLoading = false
            // Add delay before removing blur
            setTimeout(() => {
                _imageLoaded = true
            }, 100)
        }

        img.onerror = () => {
            _photoError = true
            _playerPhotoUrl = null
            _imageLoading = false
        }

        img.src = url
    }, 500)
}

// Preload image when player changes
$: if (player?.playerId) {
    preloadPlayerImage(player.playerId)
}

function _closeComprehensiveDetails(event) {
    event.preventDefault()
    event.stopPropagation()
    showComprehensiveDetails = false
}

function _handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
        showComprehensiveDetails = false
    }
}

function _toggleSeasonStats(event) {
    if (event) {
        event.preventDefault()
        event.stopPropagation()
    }
    // This will be handled by the parent component
    const seasonStatsEvent = new CustomEvent('toggle-season-stats')
    window.dispatchEvent(seasonStatsEvent)
}

$: displayName = player.name?.default || player.name || 'Unknown Player'
$: isLive = player.game_status === 'Live' || player.game_status === 'In Progress'
$: headshotUrl = player.headshot_url || null
$: playerInitials = displayName
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase())
    .join('')
    .slice(0, 2)
$: iceTime = player.time_on_ice || player.ice_time
$: hasGameStats =
    player.goals > 0 ||
    player.assists > 0 ||
    player.points > 0 ||
    (player.penalty_minutes || 0) > 0 ||
    player.plus_minus !== undefined
$: hasAdvancedStats =
    player.position !== 'G' &&
    (player.faceoffs_taken > 0 ||
        player.takeaways > 0 ||
        player.giveaways > 0 ||
        player.blocked_shots > 0 ||
        player.hits > 0 ||
        player.power_play_goals > 0 ||
        player.short_handed_goals > 0 ||
        player.even_strength_goals > 0 ||
        player.power_play_assists > 0 ||
        player.short_handed_assists > 0)
$: hasContextStats =
    player.shifts > 0 ||
    player.average_ice_time ||
    iceTime ||
    (player.blocked_shots > 0 && player.position === 'D') ||
    player.shots > 0
</script>

<!-- Comprehensive Details Modal -->
{#if showComprehensiveDetails}
    <div
        class="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 comprehensive-details-overlay"
        role="button"
        tabindex="0"
        on:click={_handleBackdropClick}
        on:keydown={(e) =>
            (e.key === "Escape" || e.key === "Enter" || e.key === " ") && _handleBackdropClick(e)}
    >
        <div
            class="bg-white rounded-lg max-w-6xl w-full mx-4 max-h-screen overflow-y-auto comprehensive-details-dialog"
        >
            <div class="p-6 comprehensive-details-content">
                <div
                    class="flex items-start justify-between gap-4 mb-6 comprehensive-details-header"
                >
                    <div class="flex items-center gap-4 player-identity">
                        <div class="player-photo player-identity__photo">
                            {#if lqipUrl || playerPhotoUrl}
                                <img
                                    src={playerPhotoUrl || lqipUrl}
                                    alt={`Kuva pelaajasta ${displayName}`}
                                    class="player-photo__img {!imageLoaded ? 'blur-sm' : ''}"
                                    loading="lazy"
                                />
                            {:else}
                                <div class="player-photo__initials" aria-hidden="true">
                                    {playerInitials}
                                </div>
                            {/if}
                            <div class="player-photo__team">
                                <div class="player-photo__team-blur" aria-hidden="true">
                                    <TeamLogo team={player.team || "NHL"} size="40" />
                                </div>
                                <TeamLogo
                                    team={player.team || "NHL"}
                                    size="40"
                                    class="player-photo__team-logo"
                                />
                            </div>
                            {#if isLive}
                                <div class="player-photo__live">LIVE</div>
                            {/if}
                        </div>
                        <div class="player-identity__meta">
                            <h2 class="text-2xl font-bold text-gray-900">
                                {displayName}
                            </h2>
                            <div class="text-lg text-gray-600">
                                {player.position && player.position !== "N/A"
                                    ? player.position
                                    : ""}{player.jersey_number ? " #" + player.jersey_number : ""} •
                                {player.team_full || player.team || "Unknown Team"}
                            </div>
                            {#if player.age || player.birth_date || player.birthplace || player.jersey_number}
                                <div class="personal-info-panel personal-info-panel--inline mt-3">
                                    <div class="personal-info-panel__grid">
                                        {#if player.age}
                                            <div class="personal-info-panel__card">
                                                <div class="text-sm text-gray-600">Ikä</div>
                                                <div class="text-base font-semibold text-gray-900">
                                                    {player.age} vuotta
                                                </div>
                                            </div>
                                        {/if}
                                        {#if player.birth_date}
                                            <div class="personal-info-panel__card">
                                                <div class="text-sm text-gray-600">
                                                    Syntymäpäivä
                                                </div>
                                                <div class="text-base font-semibold text-gray-900">
                                                    {new Date(player.birth_date).toLocaleDateString(
                                                        "fi-FI",
                                                    )}
                                                </div>
                                            </div>
                                        {/if}
                                        {#if player.birthplace}
                                            <div class="personal-info-panel__card">
                                                <div class="text-sm text-gray-600">
                                                    Syntymäpaikka
                                                </div>
                                                <div class="text-base font-semibold text-gray-900">
                                                    {player.birthplace}
                                                </div>
                                            </div>
                                        {/if}
                                        {#if player.jersey_number}
                                            <div class="personal-info-panel__card">
                                                <div class="text-sm text-gray-600">Pelinumero</div>
                                                <div class="text-base font-semibold text-gray-900">
                                                    #{player.jersey_number}
                                                </div>
                                            </div>
                                        {/if}
                                    </div>
                                </div>
                            {/if}
                        </div>
                    </div>
                    <button
                        type="button"
                        class="p-2 rounded-lg gradient-button-ghost gradient-button-ghost--sm"
                        on:click={_closeComprehensiveDetails}
                        aria-label="Sulje"
                    >
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                            <path
                                d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
                            />
                        </svg>
                    </button>
                </div>

                {#if hasGameStats || hasAdvancedStats || hasContextStats}
                    <div class="stat-panel stat-panel--combined">
                        <div class="stat-panel__header">
                            <div class="stat-panel__icon">
                                <svg viewBox="0 0 20 20" fill="currentColor">
                                    <path
                                        d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"
                                    />
                                </svg>
                            </div>
                            <div>
                                <h3 class="stat-panel__title">Pelin tilastot</h3>
                                <p class="stat-panel__subtitle">
                                    {player.team} {player.game_score} vs {player.opponent} • {new Date(player.game_date).toLocaleDateString("fi-FI", {
                                        day: "numeric",
                                        month: "short",
                                    })}
                                </p>
                            </div>
                        </div>

                        <div class="stat-panel__grid stat-panel__grid--flexible">
                            {#if hasGameStats}
                                {#if player.goals > 0}
                                    <div class="stat-panel__card stat-panel__card--goals">
                                        <div class="stat-panel__value">{player.goals}</div>
                                        <div class="stat-panel__label">Maalit</div>
                                    </div>
                                {/if}
                                {#if player.assists > 0}
                                    <div class="stat-panel__card stat-panel__card--assists">
                                        <div class="stat-panel__value">{player.assists}</div>
                                        <div class="stat-panel__label">Syötöt</div>
                                    </div>
                                {/if}
                                {#if player.points > 0}
                                    <div class="stat-panel__card stat-panel__card--points">
                                        <div class="stat-panel__value">{player.points}</div>
                                        <div class="stat-panel__label">Pisteet</div>
                                    </div>
                                {/if}
                                {#if player.plus_minus !== undefined}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">
                                            {player.plus_minus > 0 ? "+" : ""}{player.plus_minus}
                                        </div>
                                        <div class="stat-panel__label">+/-</div>
                                    </div>
                                {/if}
                                {#if (player.penalty_minutes || 0) > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">
                                            {player.penalty_minutes}
                                        </div>
                                        <div class="stat-panel__label">Rangaistusminuutit</div>
                                    </div>
                                {/if}
                            {/if}

                            {#if hasAdvancedStats}
                                {#if player.faceoffs_taken > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">
                                            {player.faceoff_wins || 0}/{player.faceoffs_taken}
                                        </div>
                                        <div class="stat-panel__label">Aloitukset</div>
                                        <div class="stat-panel__micro">
                                            {Math.round(
                                                ((player.faceoff_wins || 0) /
                                                    player.faceoffs_taken) *
                                                    100,
                                            )}%
                                        </div>
                                    </div>
                                {/if}
                                {#if player.takeaways > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.takeaways}</div>
                                        <div class="stat-panel__label">Riistot</div>
                                    </div>
                                {/if}
                                {#if player.giveaways > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.giveaways}</div>
                                        <div class="stat-panel__label">Menetykset</div>
                                    </div>
                                {/if}
                                {#if player.blocked_shots > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.blocked_shots}</div>
                                        <div class="stat-panel__label">Blokit</div>
                                    </div>
                                {/if}
                                {#if player.hits > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.hits}</div>
                                        <div class="stat-panel__label">Taklaukset</div>
                                    </div>
                                {/if}
                                {#if player.power_play_goals > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">
                                            {player.power_play_goals}
                                        </div>
                                        <div class="stat-panel__label">YV-maalit</div>
                                    </div>
                                {/if}
                                {#if player.short_handed_goals > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">
                                            {player.short_handed_goals}
                                        </div>
                                        <div class="stat-panel__label">AV-maalit</div>
                                    </div>
                                {/if}
                                {#if player.even_strength_goals > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">
                                            {player.even_strength_goals}
                                        </div>
                                        <div class="stat-panel__label">Tasakentin</div>
                                    </div>
                                {/if}
                                {#if player.power_play_assists > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">
                                            {player.power_play_assists}
                                        </div>
                                        <div class="stat-panel__label">YV-syötöt</div>
                                    </div>
                                {/if}
                                {#if player.short_handed_assists > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">
                                            {player.short_handed_assists}
                                        </div>
                                        <div class="stat-panel__label">AV-syötöt</div>
                                    </div>
                                {/if}
                            {/if}

                            {#if hasContextStats}
                                {#if player.shifts > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.shifts}</div>
                                        <div class="stat-panel__label">Vaihdot</div>
                                    </div>
                                {/if}
                                {#if player.average_ice_time && player.average_ice_time !== "00:00"}
                                    <div class="stat-panel__card stat-panel__card--ice-time">
                                        <div class="stat-panel__value">
                                            {player.average_ice_time}
                                        </div>
                                        <div class="stat-panel__label">Kesk. peliaika</div>
                                    </div>
                                {:else if iceTime && iceTime !== "00:00"}
                                    <div class="stat-panel__card stat-panel__card--ice-time">
                                        <div class="stat-panel__value">{iceTime}</div>
                                        <div class="stat-panel__label">Peliaika</div>
                                    </div>
                                {/if}
                                {#if player.blocked_shots > 0 && player.position === "D"}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.blocked_shots}</div>
                                        <div class="stat-panel__label">Blokit</div>
                                    </div>
                                {/if}
                                {#if player.shots > 0}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.shots}</div>
                                        <div class="stat-panel__label">Laukaukset</div>
                                    </div>
                                {/if}
                            {/if}
                        </div>
                    </div>
                {/if}

                <!-- Recent Results Section -->
                {#if player.recent_results && player.recent_results.length > 0}
                    <div class="stat-panel">
                        <div class="stat-panel__header">
                            <div class="stat-panel__icon">
                                <svg viewBox="0 0 20 20" fill="currentColor">
                                    <path
                                        d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"
                                    />
                                </svg>
                            </div>
                            <div>
                                <h3 class="stat-panel__title">Viimeisimmät pelit</h3>
                                <p class="stat-panel__subtitle">Pelaajan tilastot viimeisistä 5 pelistä</p>
                            </div>
                        </div>
                        <div class="recent-results-grid">
                            {#each player.recent_results as game}
                                <div class="recent-result-item">
                                    <div class="recent-result-date">
                                        {new Date(game.date).toLocaleDateString("fi-FI", {
                                            month: "short",
                                            day: "numeric",
                                        })}
                                    </div>
                                    <div class="recent-result-opponent">
                                        <TeamLogo team={game.opponent} size="16" />
                                        <span>{game.opponent}</span>
                                    </div>
                                    <div class="recent-result-stats">
                                        <div class="recent-result-stat recent-result-stat--goals">
                                            <span class="recent-result-stat__label">M</span>
                                            <span class="recent-result-stat__value">{game.goals}</span>
                                        </div>
                                        <div class="recent-result-stat recent-result-stat--assists">
                                            <span class="recent-result-stat__label">S</span>
                                            <span class="recent-result-stat__value">{game.assists}</span>
                                        </div>
                                        <div class="recent-result-stat recent-result-stat--points">
                                            <span class="recent-result-stat__label">P</span>
                                            <span class="recent-result-stat__value">{game.points}</span>
                                        </div>
                                    </div>
                                    <div class="recent-result-indicator">
                                        {#if game.result === "W"}
                                            <div
                                                class="w-2.5 h-2.5 rounded-full bg-green-500 shadow-sm"
                                                title="Voitto"
                                            ></div>
                                        {:else if game.result === "L"}
                                            <div
                                                class="w-2.5 h-2.5 rounded-full bg-red-500 shadow-sm"
                                                title="Tappio"
                                            ></div>
                                        {:else}
                                            <div
                                                class="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-sm"
                                                title="Tasapeli"
                                            ></div>
                                        {/if}
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Advanced Skater Statistics -->

                <!-- Advanced Goalie Statistics -->

                <!-- Game Context Statistics -->
            </div>
        </div>
    </div>
{/if}

<style>
    @import "./ComprehensivePlayerDetails.css";
</style>
