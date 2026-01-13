<script>
    import { base } from "$app/paths";

    import { isPlayerGameLive } from "$lib/utils/gameStateHelpers.mjs";
    import { games } from "$lib/stores/gameData.js";
    import TeamLogo from "$lib/components/ui/TeamLogo.svelte";

    let { player, isOpen = false, onclose } = $props();

    // Internal state as Svelte 5 runes
    let playerPhotoUrl = $state(null);
    let photoError = $state(false);
    let imageLoading = $state(true);
    let lqipUrl = $state(null);
    let imageLoaded = $state(false);

    // Get local WebP headshot URL (optimized, served from our domain)
    function getLocalHeadshotUrl(playerId) {
        if (!playerId) return null;
        return `${base}/headshots/${playerId}.webp`;
    }

    // Get LQIP thumbnail URL (tiny placeholder)
    function getLqipUrl(playerId) {
        if (!playerId) return null;
        return `${base}/headshots/thumbs/${playerId}.jpg`;
    }

    // Load player image - try local WebP first, fallback to NHL CDN
    function loadPlayerImage(playerId) {
        if (!playerId) return;

        imageLoading = true;
        imageLoaded = false;
        photoError = false;

        // Set LQIP placeholder immediately
        lqipUrl = getLqipUrl(playerId);

        // Try local WebP first
        const localUrl = getLocalHeadshotUrl(playerId);
        const img = new Image();

        img.onload = () => {
            playerPhotoUrl = localUrl;
            photoError = false;
            imageLoading = false;
            setTimeout(() => {
                imageLoaded = true;
            }, 100);
        };

        img.onerror = () => {
            // Fallback to NHL CDN if local not found
            if (player.headshot_url) {
                const fallbackImg = new Image();
                fallbackImg.onload = () => {
                    playerPhotoUrl = player.headshot_url;
                    photoError = false;
                    imageLoading = false;
                    setTimeout(() => {
                        imageLoaded = true;
                    }, 100);
                };
                fallbackImg.onerror = () => {
                    photoError = true;
                    playerPhotoUrl = null;
                    imageLoading = false;
                };
                fallbackImg.src = player.headshot_url;
            } else {
                photoError = true;
                playerPhotoUrl = null;
                imageLoading = false;
            }
        };

        img.src = localUrl;
    }

    // Load image when player changes using $effect
    $effect(() => {
        if (player?.playerId) {
            loadPlayerImage(player.playerId);
        }
    });

    function _closeComprehensiveDetails(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        if (onclose) onclose();
    }

    function _handleBackdropClick(event) {
        if (event.target === event.currentTarget) {
            if (onclose) onclose();
        }
    }

    function _toggleSeasonStats(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        // This will be handled by the parent component
        const seasonStatsEvent = new CustomEvent("toggle-season-stats");
        window.dispatchEvent(seasonStatsEvent);
    }

    const displayName = $derived(player.name?.default || player.name || "Unknown Player");
    const gamesData = $derived($games);
    const isLive = $derived(isPlayerGameLive(player, gamesData));
    const headshotUrl = $derived(player.headshot_url || null);
    const playerInitials = $derived(
        displayName
            .split(" ")
            .map((part) => part.charAt(0).toUpperCase())
            .join("")
            .slice(0, 2),
    );
    const isGoalie = $derived(
        (player.position || "").toUpperCase() === "G" ||
            (player.position || "").toUpperCase() === "GOALIE",
    );
    const iceTime = $derived(player.time_on_ice || player.ice_time);
    const hasGameStats = $derived(
        player.goals > 0 ||
            player.assists > 0 ||
            player.points > 0 ||
            (player.penalty_minutes || 0) > 0 ||
            (!isGoalie && player.plus_minus !== undefined) ||
            (isGoalie && (player.saves > 0 || player.shots_against > 0)),
    );
    const hasAdvancedStats = $derived(
        player.position !== "G" &&
            (player.faceoffs_taken > 0 ||
                player.takeaways > 0 ||
                player.giveaways > 0 ||
                player.blocked_shots > 0 ||
                player.hits > 0 ||
                player.power_play_goals > 0 ||
                player.short_handed_goals > 0 ||
                player.even_strength_goals > 0 ||
                player.power_play_assists > 0 ||
                player.short_handed_assists > 0),
    );
    const hasContextStats = $derived(
        player.shifts > 0 ||
            player.average_ice_time ||
            iceTime ||
            (player.blocked_shots > 0 && player.position === "D") ||
            player.shots > 0 ||
            (isGoalie && player.time_on_ice),
    );
    const goalieSavePct = $derived(
        player.save_percentage !== undefined
            ? Math.round(player.save_percentage * 1000) / 10
            : player.shots_against > 0
              ? Math.round((player.saves / player.shots_against) * 1000) / 10
              : null,
    );

    // Action to portal element to body
    function portal(node) {
        // Add a class to hide the element initially
        const placeholder = document.createElement('div');
        placeholder.className = 'portal-placeholder';
        placeholder.style.cssText = 'display: none;';
        node.parentNode.insertBefore(placeholder, node);
        node._portalPlaceholder = placeholder;

        // Move to body
        document.body.appendChild(node);

        return {
            update() {
                // Keep it in body
                if (node.parentNode !== document.body) {
                    document.body.appendChild(node);
                }
            },
            destroy() {
                // Remove from body and restore placeholder
                if (document.body.contains(node)) {
                    document.body.removeChild(node);
                }
                if (node._portalPlaceholder && node._portalPlaceholder.parentNode) {
                    node._portalPlaceholder.parentNode.removeChild(node._portalPlaceholder);
                }
            }
        };
    }

    // Prevent body scroll when modal is open
    $effect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    });
</script>

<!-- Comprehensive Details Modal -->
{#if isOpen}
    <div
        use:portal
        class="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-end md:items-center justify-center modal-safe-overlay modal-overlay-mobile md:modal-overlay-desktop z-[100] comprehensive-details-overlay"
        role="button"
        tabindex="0"
        onclick={_handleBackdropClick}
        onkeydown={(e) =>
            (e.key === "Escape" || e.key === "Enter" || e.key === " ") && _handleBackdropClick(e)}
    >
        <div
            class="bg-white rounded-lg max-w-6xl w-full mx-4 max-h-[85dvh] max-h-[85vh] overflow-y-auto comprehensive-details-dialog modal-dialog-mobile md:modal-dialog-desktop"
        >
            <div class="p-6 comprehensive-details-content modal-content-mobile">
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
                            <h2 class="player-identity__name text-2xl font-bold text-gray-900">
                                {displayName}
                            </h2>
                            <div class="player-identity__basic-info text-lg text-gray-600">
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
                                                <div
                                                    class="personal-info-panel__label text-sm text-gray-600"
                                                >
                                                    Ikä
                                                </div>
                                                <div
                                                    class="personal-info-panel__value text-base font-semibold text-gray-900"
                                                >
                                                    {player.age} vuotta
                                                </div>
                                            </div>
                                        {/if}
                                        {#if player.birth_date}
                                            <div class="personal-info-panel__card">
                                                <div
                                                    class="personal-info-panel__label text-sm text-gray-600"
                                                >
                                                    Syntymäpäivä
                                                </div>
                                                <div
                                                    class="personal-info-panel__value text-base font-semibold text-gray-900"
                                                >
                                                    {new Date(player.birth_date).toLocaleDateString(
                                                        "fi-FI",
                                                    )}
                                                </div>
                                            </div>
                                        {/if}
                                        {#if player.birthplace}
                                            <div class="personal-info-panel__card">
                                                <div
                                                    class="personal-info-panel__label text-sm text-gray-600"
                                                >
                                                    Syntymäpaikka
                                                </div>
                                                <div
                                                    class="personal-info-panel__value text-base font-semibold text-gray-900"
                                                >
                                                    {player.birthplace}
                                                </div>
                                            </div>
                                        {/if}
                                        {#if player.jersey_number}
                                            <div class="personal-info-panel__card">
                                                <div
                                                    class="personal-info-panel__label text-sm text-gray-600"
                                                >
                                                    Pelinumero
                                                </div>
                                                <div
                                                    class="personal-info-panel__value text-base font-semibold text-gray-900"
                                                >
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
                        class="text-gray-400 hover:text-gray-600 p-2 rounded-full hover:bg-gray-100 transition-colors"
                        onclick={_closeComprehensiveDetails}
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
                            <div class="stat-panel__header-content">
                                <h3 class="stat-panel__title">Pelin tilastot</h3>
                                <p class="stat-panel__subtitle">
                                    {player.team}
                                    {player.game_score} vs {player.opponent} • {new Date(
                                        player.game_date,
                                    ).toLocaleDateString("fi-FI", {
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
                                {#if !isGoalie && player.plus_minus !== undefined}
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

                            {#if isGoalie}
                                {#if player.saves !== undefined}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.saves}</div>
                                        <div class="stat-panel__label">Torjunnat</div>
                                    </div>
                                {/if}
                                {#if player.shots_against !== undefined}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.shots_against}</div>
                                        <div class="stat-panel__label">Laukaukset kohti</div>
                                    </div>
                                {/if}
                                {#if player.goals_against !== undefined}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{player.goals_against}</div>
                                        <div class="stat-panel__label">Päästetyt maalit</div>
                                    </div>
                                {/if}
                                {#if goalieSavePct !== null}
                                    <div class="stat-panel__card">
                                        <div class="stat-panel__value">{goalieSavePct}%</div>
                                        <div class="stat-panel__label">Torjuntaprosentti</div>
                                    </div>
                                {/if}
                                {#if player.goals_against === 0 && player.saves > 0}
                                    <div class="stat-panel__card border-green-200 bg-green-50">
                                        <div class="stat-panel__value text-green-600">JEES</div>
                                        <div class="stat-panel__label text-green-700 font-bold">
                                            Nollapeli
                                        </div>
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
                                {#if isGoalie && iceTime}
                                    <div class="stat-panel__card stat-panel__card--ice-time">
                                        <div class="stat-panel__value">{iceTime}</div>
                                        <div class="stat-panel__label">Peliaika</div>
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
                            <div class="stat-panel__header-content">
                                <h3 class="stat-panel__title">Viimeisimmät pelit</h3>
                                <p class="stat-panel__subtitle">
                                    Pelaajan tilastot viimeisistä 5 pelistä
                                </p>
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
                                    <div class="recent-result-opponent__team">
                                        <TeamLogo team={game.opponent} size="24" />
                                        <span>{game.opponent}</span>
                                    </div>
                                    <div class="recent-result-score">
                                        <span class="recent-result-score__team">{player.team}</span>
                                        <span
                                            class="recent-result-score__value"
                                            class:is-winner={game.result === "W"}
                                            >{game.team_score}</span
                                        >
                                        <span class="recent-result-score__separator">-</span>
                                        <span
                                            class="recent-result-score__value"
                                            class:is-winner={game.result === "L"}
                                            >{game.opponent_score}</span
                                        >
                                        <span class="recent-result-score__team"
                                            >{game.opponent}</span
                                        >
                                    </div>
                                    <div class="recent-result-stats">
                                        {#if isGoalie}
                                            <div
                                                class="recent-result-stat recent-result-stat--goals"
                                                title="Päästetyt maalit"
                                            >
                                                <span class="recent-result-stat__label">P</span>
                                                <span class="recent-result-stat__value"
                                                    >{game.goals_against ?? "-"}</span
                                                >
                                            </div>
                                            <div
                                                class="recent-result-stat recent-result-stat--assists"
                                                title="Torjunnat"
                                            >
                                                <span class="recent-result-stat__label">T</span>
                                                <span class="recent-result-stat__value"
                                                    >{game.saves ?? "-"}</span
                                                >
                                            </div>
                                            <div
                                                class="recent-result-stat recent-result-stat--points"
                                                title="Torjuntaprosentti"
                                            >
                                                <span class="recent-result-stat__label">T%</span>
                                                <span class="recent-result-stat__value"
                                                    >{game.save_percentage
                                                        ? Math.round(game.save_percentage * 100)
                                                        : "-"}</span
                                                >
                                            </div>
                                        {:else}
                                            <div
                                                class="recent-result-stat recent-result-stat--goals"
                                                title="Maalit"
                                            >
                                                <span class="recent-result-stat__label">M</span>
                                                <span class="recent-result-stat__value"
                                                    >{game.goals}</span
                                                >
                                            </div>
                                            <div
                                                class="recent-result-stat recent-result-stat--assists"
                                                title="Syötöt"
                                            >
                                                <span class="recent-result-stat__label">S</span>
                                                <span class="recent-result-stat__value"
                                                    >{game.assists}</span
                                                >
                                            </div>
                                            <div
                                                class="recent-result-stat recent-result-stat--points"
                                                title="Pisteet"
                                            >
                                                <span class="recent-result-stat__label">P</span>
                                                <span class="recent-result-stat__value"
                                                    >{game.points}</span
                                                >
                                            </div>
                                        {/if}
                                    </div>
                                    <div class="recent-result-indicator">
                                        {#if game.result === "W"}
                                            <div
                                                class="recent-result-item__dot w-2.5 h-2.5 rounded-full bg-green-500 shadow-sm"
                                                title="Voitto"
                                            ></div>
                                        {:else if game.result === "L"}
                                            <div
                                                class="recent-result-item__dot w-2.5 h-2.5 rounded-full bg-red-500 shadow-sm"
                                                title="Tappio"
                                            ></div>
                                        {:else}
                                            <div
                                                class="recent-result-item__dot w-2.5 h-2.5 rounded-full bg-amber-500 shadow-sm"
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
