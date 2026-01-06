<script>
    import ComprehensivePlayerDetails from "$lib/components/game/ComprehensivePlayerDetails.svelte";
    import { onMount } from "svelte";
    import { base } from "$app/paths";
    import { games } from "$lib/stores/gameData.js";
    import {
        formatGameMatchup,
        formatGameVenue,
        formatGameScore,
    } from "$lib/utils/gameFormatHelpers.mjs";
    import { getTeamColorVariables } from "$lib/utils/teamColors.js";
    import { isPlayerGameLive, shouldShowGameResult } from "$lib/utils/gameStateHelpers.mjs";
    import TeamLogo from "$lib/components/ui/TeamLogo.svelte";
    import "./PlayerCard.css";

    let { player } = $props();

    // Reactive variables for player photo
    let playerPhotoUrl = $state(null);
    let _photoError = $state(false);
    let _imageLoading = $state(true);
    let _lqipUrl = $state(null);

    // Get player headshot URL
    function getPlayerHeadshotUrl(playerId) {
        if (!playerId) return null;
        return `${base}/headshots/thumbs/${playerId}.jpg`;
    }

    // Generate LQIP (Low Quality Image Placeholder)
    function _generateLQIP(playerId) {
        if (!playerId) return null;
        // Create a simple colored rectangle as LQIP based on player ID
        const canvas = document.createElement("canvas");
        canvas.width = 64;
        canvas.height = 64;
        const ctx = canvas.getContext("2d");

        // Generate color based on player ID
        const hue = (parseInt(playerId, 10) * 137.508) % 360;
        ctx.fillStyle = `hsl(${hue}, 30%, 85%)`;
        ctx.fillRect(0, 0, 64, 64);

        return canvas.toDataURL();
    }

    // Preload player image
    function preloadPlayerImage(playerId) {
        if (!playerId) return;

        _imageLoading = true;
        playerPhotoUrl = null; // Reset full image

        // Set LQIP immediately
        _lqipUrl = getPlayerHeadshotUrl(playerId);

        // Load full image after delay
        setTimeout(() => {
            const img = new Image();
            const url = player.headshot_url;

            img.onload = () => {
                playerPhotoUrl = url;
                _photoError = false;
                _imageLoading = false;
            };

            img.onerror = () => {
                _photoError = true;
                playerPhotoUrl = null;
                _imageLoading = false;
            };

            img.src = url;
        }, 500);
    }

    // Preload image when player changes
    $effect(() => {
        if (player?.playerId) {
            preloadPlayerImage(player.playerId);
        }
    });
    let _photoLoading = $state(true);

    // Load player photo when component mounts or player changes
    $effect(() => {
        if (player?.playerId) {
            loadPlayerPhoto(player.playerId, player.headshot_url);
        }
    });

    /**
     * Load player photo from our API, falling back to precomputed headshot_url if available
     */
    async function loadPlayerPhoto(_playerId, precomputedUrl) {
        // If we already have a precomputed URL from data, use it first
        if (precomputedUrl) {
            playerPhotoUrl = precomputedUrl;
            _photoLoading = false;
            _photoError = false;
            return;
        }

        // If no precomputed URL is available, skip network fetch to avoid 404 spam in dev/offline
        _photoLoading = false;
        _photoError = true;
        playerPhotoUrl = null;
    }

    let showSeasonStats = $state(false);
    let showComprehensiveDetails = $state(false);
    let _isLogoHovered = $state(false);
    let isFlipped = $state(false);

    // Convert hex to rgba with opacity for subtle borders
    function _hexToRgba(hex, opacity = 0.7) {
        if (!hex || !hex.startsWith("#")) return `rgba(0, 0, 0, ${opacity})`;

        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        if (!result) return `rgba(0, 0, 0, ${opacity})`;

        const r = parseInt(result[1], 16);
        const g = parseInt(result[2], 16);
        const b = parseInt(result[3], 16);

        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }

    // Subtle border opacity
    function _hexToRgbaBorder(hex) {
        return _hexToRgba(hex, 0.3);
    }

    // Team names are now fetched from API and stored in team_full field
    function getTeamWithCity(teamAbbrev) {
        if (!teamAbbrev) return "Unknown Team";
        // Use team_full from API data if available, otherwise fallback to abbreviation
        const fullTeamName = player?.team_full || player?.opponent_full;
        if (fullTeamName && fullTeamName !== teamAbbrev) {
            return fullTeamName;
        }
        return teamAbbrev;
    }

    function _toggleSeasonStats(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        showSeasonStats = !showSeasonStats;
    }

    function _closeSeasonStats(event) {
        event.preventDefault();
        event.stopPropagation();
        showSeasonStats = false;
    }

    function _toggleComprehensiveDetails(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        showComprehensiveDetails = !showComprehensiveDetails;
    }

    function _handleBackdropClick(event) {
        if (event.target === event.currentTarget) {
            showSeasonStats = false;
            showComprehensiveDetails = false;
        }
    }

    function toggleFlip() {
        isFlipped = !isFlipped;
    }

    function _handleCardClick(event) {
        // Only flip if clicking on the card itself, not on buttons or interactive elements
        if (event.target.closest("button") || event.target.closest("a")) {
            return;
        }
        toggleFlip();
    }

    const displayName = $derived(
        player.name?.default ||
            player.name ||
            player.fullName ||
            player.skaterFullName ||
            "Unknown Player",
    );
    const gamesData = $derived($games);
    const isLive = $derived(isPlayerGameLive(player, gamesData));
    const showResult = $derived(shouldShowGameResult(player, gamesData));
    const teamWithCity = $derived(getTeamWithCity(player.team || "NHL"));
    const opponentWithCity = $derived(getTeamWithCity(player.opponent || "NHL"));
    const playerHeadshot = $derived(playerPhotoUrl);
    const formattedScore = $derived(formatGameScore(player, gamesData));

    // Team color variables
    let _teamColorVars = $state({
        "--team-primary-color": "#000000",
        "--team-secondary-color": "#FFFFFF",
        "--team-accent-color": "#000000",
    });

    // Animation control
    const _enableAnimatedBorders = true;

    // Load team colors when component mounts or player changes
    onMount(async () => {
        if (player?.team) {
            try {
                _teamColorVars = await getTeamColorVariables(player.team);
            } catch (error) {
                console.warn(`Failed to load team colors for ${player.team}:`, error);
            }
        }
    });

    // Update colors when player changes
    $effect(() => {
        if (player?.team) {
            loadTeamColors();
        }
    });

    async function loadTeamColors() {
        if (player?.team) {
            try {
                _teamColorVars = await getTeamColorVariables(player.team);
            } catch (error) {
                console.warn(`Failed to load team colors for ${player.team}:`, error);
            }
        }
    }
    const playerInitials = $derived(
        displayName
            .split(" ")
            .map((part) => part.charAt(0).toUpperCase())
            .join("")
            .slice(0, 2),
    );

    // Calculate number of stats for responsive grid (skaters)
    const statCount = $derived(
        [
            player.goals > 0,
            player.assists > 0,
            player.points > 0,
            !isGoalie && player.plus_minus !== undefined,
            (player.penalty_minutes || 0) > 0,
        ].filter(Boolean).length,
    );

    const skaterGridClass = $derived(
        statCount === 1
            ? "player-card__stats-grid--single"
            : `player-card__stats-grid--skater-${Math.min(statCount, 5)}`,
    );

    // Goalie stats count
    const goalieStatCount = $derived(
        [
            player.saves !== undefined,
            player.shots_against !== undefined,
            player.goals_against !== undefined,
            goalieSavePct !== null,
            (player.empty_net_goals || 0) > 0,
        ].filter(Boolean).length,
    );

    const goalieGridClass = $derived(
        goalieStatCount === 1
            ? "player-card__stats-grid--single"
            : goalieStatCount === 2
              ? "player-card__stats-grid--goalie-2"
              : goalieStatCount === 3
                ? "player-card__stats-grid--goalie-3"
                : "player-card__stats-grid--goalie-4",
    );

    // Goalie helpers
    const isGoalie = $derived(
        (player.position || "").toUpperCase() === "G" ||
            (player.position || "").toUpperCase() === "GOALIE",
    );
    const goalieSavePct = $derived(getSavePercentage(player));

    // Game result helpers
    const gameResult = $derived(player.game_result || "");
    const resultIndicator = $derived(getResultIndicator(gameResult));

    function getResultIndicator(result) {
        switch (result) {
            case "W":
                return {
                    bg: "bg-green-100",
                    text: "W",
                    label: "Voitto",
                    textColor: "text-green-700",
                    border: "ring-green-300",
                };
            case "SOW":
                return {
                    bg: "bg-emerald-100",
                    text: "SV",
                    label: "Voitto VL",
                    textColor: "text-emerald-700",
                    border: "ring-emerald-300",
                };
            case "L":
                return {
                    bg: "bg-red-100",
                    text: "L",
                    label: "Häviö",
                    textColor: "text-red-700",
                    border: "ring-red-300",
                };
            case "SOL":
                return {
                    bg: "bg-rose-100",
                    text: "SO",
                    label: "Häviö VL",
                    textColor: "text-rose-700",
                    border: "ring-rose-300",
                };
            case "OTW":
                return {
                    bg: "bg-amber-100",
                    text: "JA",
                    label: "Voitto JA",
                    textColor: "text-amber-700",
                    border: "ring-amber-300",
                };
            case "OTL":
                return {
                    bg: "bg-orange-100",
                    text: "JA",
                    label: "Häviö JA",
                    textColor: "text-orange-700",
                    border: "ring-orange-300",
                };
            default:
                return {
                    bg: "bg-gray-100",
                    text: "?",
                    label: "Ei tietoa",
                    textColor: "text-gray-700",
                    border: "ring-gray-300",
                };
        }
    }

    function getSavePercentage(player) {
        const provided = player.save_percentage ?? player.savePercentage;
        // Use provided percentage if it's a positive number
        if (typeof provided === "number" && provided > 0) {
            // If it's already a percentage (like 0.857), convert to percentage format
            // If it's a percentage value (like 85.7), keep it as is
            return Number(provided > 1 ? provided : (provided * 100).toFixed(1));
        }

        const saves = Number(player.saves ?? player.goalie_saves);
        const shotsAgainst = Number(player.shots_against ?? player.shotsAgainst);

        if (Number.isFinite(saves) && Number.isFinite(shotsAgainst) && shotsAgainst > 0) {
            // Calculate and return as percentage (e.g., 85.7)
            return Number(((saves / shotsAgainst) * 100).toFixed(1));
        }

        return null;
    }
</script>

<div class="player-card__container relative w-full min-h-[320px]">
    <!-- Player Card -->
    <div class="player-card" class:flipped={isFlipped}>
        <div class="player-card__inner">
            <!-- Front of Card -->
            <div
                class="player-card__face player-card__face--front bg-white w-full overflow-hidden relative cursor-pointer rounded-xl shadow-sm transition-all duration-300 hover:shadow-md"
                style={`border: 1px solid rgba(226, 232, 240, 0.8); background: white;`}
                onclick={_handleCardClick}
                role="button"
                tabindex="0"
                onkeydown={(e) => e.key === "Enter" && _handleCardClick(e)}
                aria-label="Click to flip player card"
            >
                <!-- Clean single border with top accent stripe -->
                <div
                    class="absolute top-0 left-0 right-0 h-1.5"
                    style={`background: var(--team-primary-color);`}
                ></div>

                <div
                    class="player-card__content relative bg-white h-full flex flex-col overflow-visible p-5"
                >
                    <div class="player-card__logo-bg team-logo-bg select-none pointer-events-none">
                        <TeamLogo team={player.team || "NHL"} size="120" />
                    </div>

                    <!-- Top Left Player Info -->
                    <div class="player-card__player-info relative z-10 mb-3">
                        <div class="player-card__player-header mb-0.5">
                            <h3
                                class="player-card__player-name text-lg font-bold text-gray-900 tracking-tight leading-tight"
                            >
                                {displayName}
                            </h3>
                        </div>
                        <div
                            class="player-card__team-subtitle text-xs font-semibold text-gray-600 mb-1.5"
                        >
                            {teamWithCity}
                        </div>
                        <div
                            class="player-card__player-details text-[10px] font-bold text-gray-400 tracking-widest uppercase flex items-center gap-1.5"
                        >
                            <span>{player.position || player.positionCode || "N/A"}</span>
                            {#if player.jersey_number || player.jerseyNumber}
                                <span class="text-gray-200">|</span>
                                <span>#{player.jersey_number || player.jerseyNumber}</span>
                            {/if}
                        </div>
                    </div>

                    <!-- Top Right Team Logo - Simplified -->
                    <div class="player-card__team-logo absolute top-3 right-3 z-10">
                        <div
                            class="player-card__team-logo-container relative team-logo-container"
                            role="img"
                            aria-label={`Team logo for ${player.team_full || player.team || "NHL"}`}
                            title={player.team_full || player.team || "NHL"}
                        >
                            <div class="player-card__team-logo-inner relative z-10 drop-shadow-sm">
                                <TeamLogo team={player.team || "NHL"} size="42" />
                            </div>
                        </div>
                    </div>

                    {#if isLive}
                        <div class="player-card__live-indicator absolute -top-1 -right-1">
                            <span
                                class="player-card__live-badge bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow-sm"
                            >
                                LIVE
                            </span>
                        </div>
                    {/if}

                    <!-- Spacer removed as we use relative layout now -->
                    <div class="mb-2"></div>

                    <!-- Game Stats -->
                    {#if isGoalie}
                        <div class="player-card__stats mb-2 w-full">
                            <div
                                class={`player-card__stats-grid ${goalieGridClass} grid gap-1 text-left w-full`}
                            >
                                <div
                                    class="player-card__stat-item player-card__stat-item--saves flex flex-col justify-center min-w-0 text-center"
                                    title="Torjunnat"
                                >
                                    <div
                                        class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                    >
                                        {player.saves}
                                    </div>
                                    <div
                                        class="player-card__stat-label text-[10px] text-gray-400 uppercase tracking-widest mt-1 truncate font-medium"
                                    >
                                        Torjunnat
                                    </div>
                                </div>
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
                                            class="player-card__stat-label text-[10px] text-gray-400 uppercase tracking-widest mt-1 truncate font-medium"
                                            title="Vastustajan laukaukset"
                                        >
                                            Vastust.
                                        </div>
                                    </div>
                                {/if}
                                <div
                                    class="player-card__stat-item player-card__stat-item--goals-against flex flex-col justify-center min-w-0 text-center"
                                    title="Päästetyt maalit"
                                >
                                    <div
                                        class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                    >
                                        {player.goals_against}
                                    </div>
                                    <div
                                        class="player-card__stat-label text-[10px] text-gray-400 uppercase tracking-widest mt-1 truncate font-medium"
                                    >
                                        Päästetyt
                                    </div>
                                </div>
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
                                            class="player-card__stat-label text-[10px] text-gray-400 uppercase tracking-widest mt-1 truncate font-medium"
                                            title="Torjuntaprosentti"
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
                                            class="player-card__stat-label text-[10px] text-red-500 uppercase tracking-widest mt-1 truncate font-medium"
                                        >
                                            Tyhjä maali
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {:else if player.goals > 0 || player.assists > 0 || player.points > 0 || (player.penalty_minutes || 0) > 0 || player.plus_minus !== undefined || (player.empty_net_goals || 0) > 0}
                        <div class="player-card__stats mb-2 w-full">
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
                                            class="player-card__stat-label text-[10px] text-gray-400 uppercase tracking-widest mt-1 truncate font-medium"
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
                                            class="player-card__stat-label text-[10px] text-gray-400 uppercase tracking-widest mt-1 truncate font-medium"
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
                                            class="player-card__stat-label text-[10px] text-finnish-blue-600 uppercase tracking-widest mt-1 truncate font-medium"
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
                                            class="player-card__stat-label text-[10px] text-red-500 uppercase tracking-widest mt-1 truncate font-medium"
                                        >
                                            Tyhjä maali
                                        </div>
                                    </div>
                                {/if}
                                {#if !isGoalie && (player.plus_minus !== undefined || player.plusMinus !== undefined)}
                                    {@const pm = player.plus_minus ?? player.plusMinus}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--plus-minus flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {pm > 0 ? "+" : ""}{pm}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-[10px] text-gray-400 uppercase tracking-widest mt-1 truncate font-medium"
                                            title="Plus-miinus tilasto"
                                        >
                                            +/-
                                        </div>
                                    </div>
                                {/if}
                                {#if (player.penalty_minutes || 0) > 0 || (player.penaltyMinutes || 0) > 0}
                                    <div
                                        class="player-card__stat-item player-card__stat-item--penalty-minutes flex flex-col justify-center min-w-0 text-center"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.penalty_minutes || player.penaltyMinutes}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-[10px] text-gray-400 uppercase tracking-widest mt-1 truncate font-medium"
                                            title="Rangaistusminuutit"
                                        >
                                            R.min
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/if}

                    <!-- Simplified Game Info -->
                    {#if isGoalie || player.goals > 0 || player.assists > 0 || player.points > 0 || (player.penalty_minutes || 0) > 0 || player.plus_minus !== undefined || (player.empty_net_goals || 0) > 0}
                        <div
                            class="player-card__game-info flex flex-col items-center justify-center gap-0.5 mt-0 mb-3"
                        >
                            <div class="text-[10px] tracking-wider font-medium text-gray-400">
                                {formatGameMatchup(player, gamesData)}
                            </div>
                            {#if formattedScore}
                                <div class="text-xs font-bold text-gray-700">
                                    {formattedScore}
                                </div>
                            {/if}
                            {#if formatGameVenue(player)}
                                <div
                                    class="text-[10px] tracking-wider font-medium text-gray-400 truncate max-w-[200px]"
                                >
                                    {formatGameVenue(player)}
                                </div>
                            {/if}
                        </div>
                    {/if}
                    <div
                        class="player-card__footer mt-auto flex items-center justify-between pt-4 border-t border-gray-100"
                    >
                        <!-- Enhanced Result Indicator - More subtle -->
                        {#if gameResult}
                            <div class="player-card__result-status flex items-center gap-2">
                                <div
                                    class={`w-5 h-5 rounded-md ${resultIndicator.bg} ${resultIndicator.textColor} flex items-center justify-center text-[10px] font-bold shadow-sm`}
                                    title={resultIndicator.label}
                                >
                                    {resultIndicator.text}
                                </div>
                                <span class="text-xs font-medium text-gray-500"
                                    >{resultIndicator.label}</span
                                >
                            </div>
                        {:else}
                            <!-- Spacer to keep layout consistent -->
                            <div></div>
                        {/if}

                        <button
                            class="player-card__details-button-inline group"
                            onclick={_toggleComprehensiveDetails}
                            onkeydown={(e) => e.key === "Enter" && _toggleComprehensiveDetails()}
                            aria-label="Show comprehensive player details for {displayName}"
                            title="Näytä kattavat tiedot"
                        >
                            <svg
                                width="14"
                                height="14"
                                viewBox="0 0 24 24"
                                fill="currentColor"
                                class="text-gray-400 group-hover:text-white transition-colors duration-200"
                            >
                                <path
                                    d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"
                                />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Back of Card - Matching Refined Style -->
            <div
                class="player-card__face player-card__face--back bg-white w-full overflow-hidden relative cursor-pointer rounded-xl shadow-sm"
                style={`border: 1px solid rgba(226, 232, 240, 0.8); background: white;`}
                onclick={_handleCardClick}
                role="button"
                tabindex="0"
                onkeydown={(e) => e.key === "Enter" && _handleCardClick(e)}
                aria-label="Click to flip player card back"
            >
                <!-- Clean single border with top accent stripe (back) -->
                <div
                    class="absolute top-0 left-0 right-0 h-1.5"
                    style={`background: var(--team-primary-color); opacity: 0.7;`}
                ></div>

                <div
                    class="player-card__content relative bg-white h-full flex flex-col overflow-visible p-5 pt-4"
                >
                    <!-- Top Left Player Info -->
                    <div class="player-card__player-info relative z-10 mb-3">
                        <div class="player-card__player-header mb-0.5">
                            <h3
                                class="player-card__player-name text-lg font-bold text-gray-900 tracking-tight leading-tight"
                            >
                                {displayName}
                            </h3>
                        </div>
                        <div class="player-card__team-subtitle text-xs font-semibold text-gray-600">
                            {teamWithCity}
                        </div>
                    </div>

                    <!-- Top Right Team Logo -->
                    <div class="player-card__team-logo absolute top-3 right-3 z-10 opacity-80">
                        <TeamLogo team={player.team || "NHL"} size="42" />
                    </div>

                    <!-- Spacer removed -->
                    <div class="mb-2"></div>

                    <!-- Additional Stats and Time on Ice Wrapper -->
                    <div class="flex-grow p-4 pt-2 flex flex-col">
                        <!-- Additional Stats -->
                        <div class="player-card__advanced-stats mb-2 w-full">
                            <div
                                class="player-card__advanced-stats-grid grid gap-y-4 gap-x-3 text-left w-full"
                            >
                                {#if isGoalie}
                                    <div
                                        class="player-card__stat-item flex flex-col justify-center min-w-0 text-center"
                                        title="Torjunnat"
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
                                    {#if player.shots_against !== undefined}
                                        <div
                                            class="player-card__stat-item flex flex-col justify-center min-w-0 text-center"
                                        >
                                            <div
                                                class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                            >
                                                {player.shots_against}
                                            </div>
                                            <div
                                                class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                                title="Vastustajan laukaukset kohti"
                                            >
                                                Laukaukset kohti
                                            </div>
                                        </div>
                                    {/if}
                                    <div
                                        class="player-card__stat-item flex flex-col justify-center min-w-0 text-center"
                                        title="Päästetyt maalit"
                                    >
                                        <div
                                            class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                        >
                                            {player.goals_against}
                                        </div>
                                        <div
                                            class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                        >
                                            Päästetyt
                                        </div>
                                    </div>
                                    {#if goalieSavePct !== null}
                                        <div
                                            class="player-card__stat-item flex flex-col justify-center min-w-0 text-center"
                                        >
                                            <div
                                                class="player-card__stat-value text-sm font-bold text-gray-900 truncate"
                                            >
                                                {goalieSavePct}%
                                            </div>
                                            <div
                                                class="player-card__stat-label text-xs text-gray-600 mt-1 truncate"
                                                title="Torjuntaprosentti"
                                            >
                                                Torjuntaprosentti
                                            </div>
                                        </div>
                                    {/if}
                                    {#if player.goals_against === 0 && player.saves > 0}
                                        <div
                                            class="player-card__stat-item flex flex-col justify-center min-w-0 text-center"
                                            title="Maali pysynyt puhtaana koko ottelun ajan"
                                        >
                                            <div
                                                class="player-card__stat-value text-sm font-bold text-green-600 truncate"
                                            >
                                                KYLLÄ
                                            </div>
                                            <div
                                                class="player-card__stat-label text-xs text-green-600 mt-1 truncate font-bold"
                                            >
                                                Nollapeli
                                            </div>
                                        </div>
                                    {/if}
                                {:else}
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
                                                Aloitukset
                                            </div>
                                        </div>
                                    {/if}
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
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modals -->
{#if showSeasonStats}
    <!-- Backdrop -->
    <div
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-opacity duration-300 pointer-events-auto"
        onclick={_handleBackdropClick}
        role="button"
        tabindex="0"
        onkeydown={(e) => e.key === "Escape" && _closeSeasonStats(e)}
        aria-label="Close modal"
        transition:fade={{ duration: 200 }}
    >
        <!-- Modal Content -->
        <div
            class="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden relative animate-in fade-in zoom-in-95 duration-200"
            role="dialog"
            aria-modal="true"
            aria-labelledby="season-stats-title"
            onclick={(e) => e.stopPropagation()}
        >
            <!-- Header -->
            <div class="bg-gray-50 px-6 py-4 border-b border-gray-100 flex items-center gap-4">
                <div class="player-card__modal-avatar shrink-0">
                    {#if playerPhotoUrl && !_photoError}
                        <img
                            src={playerPhotoUrl || player.headshot_url}
                            alt={displayName}
                            class={`player-card__modal-photo ${_photoLoading || _imageLoading ? "opacity-0 blur-sm" : "opacity-100 blur-0"}`}
                            onload={() => {
                                _photoLoading = false;
                                _imageLoading = false;
                            }}
                            onerror={() => {
                                _photoError = true;
                                _photoLoading = false;
                                _imageLoading = false;
                            }}
                        />
                        {#if (_photoLoading || _imageLoading) && _lqipUrl}
                            <img
                                src={_lqipUrl}
                                alt=""
                                class="absolute inset-0 w-full h-full object-cover blur-md scale-110 -z-10"
                            />
                        {/if}
                    {:else if _lqipUrl}
                        <img
                            src={_lqipUrl}
                            alt=""
                            class="absolute inset-0 w-full h-full object-cover"
                        />
                    {:else}
                        <div class="player-card__modal-initials">{playerInitials}</div>
                    {/if}
                </div>
                <div>
                    <h3 id="season-stats-title" class="text-lg font-bold text-gray-900">
                        {displayName}
                    </h3>
                    <div class="text-sm text-gray-500 flex items-center gap-2">
                        <span>{teamWithCity}</span>
                        <span>•</span>
                        <span>Kauden 2024-2025 tilastot</span>
                    </div>
                </div>
                <button
                    class="ml-auto p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                    onclick={_closeSeasonStats}
                    aria-label="Sulje"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-5 w-5"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path
                            fill-rule="evenodd"
                            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                            clip-rule="evenodd"
                        />
                    </svg>
                </button>
            </div>

            <!-- Content -->
            <div class="p-6">
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-gray-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-gray-900">
                            {player.season_goals || 0}
                        </div>
                        <div class="text-xs text-gray-500 uppercase tracking-wider mt-1">
                            Maalit
                        </div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-gray-900">
                            {player.season_assists || 0}
                        </div>
                        <div class="text-xs text-gray-500 uppercase tracking-wider mt-1">
                            Syötöt
                        </div>
                    </div>
                    <div
                        class="bg-finnish-blue-50 p-4 rounded-lg text-center col-span-2 border border-finnish-blue-100"
                    >
                        <div class="text-3xl font-bold text-finnish-blue-600">
                            {player.season_points || 0}
                        </div>
                        <div
                            class="text-xs text-finnish-blue-600 uppercase tracking-wider mt-1 font-medium"
                        >
                            Pisteet yhteensä
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}

{#if showComprehensiveDetails}
    <ComprehensivePlayerDetails
        {player}
        {gamesData}
        isOpen={showComprehensiveDetails}
        onclose={() => (showComprehensiveDetails = false)}
    />
{/if}
