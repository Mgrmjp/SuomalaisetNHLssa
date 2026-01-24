<script>
    import { base } from "$app/paths";
    import TeamLogo from "$lib/components/ui/TeamLogo.svelte";
    import Snowfall from "$lib/components/ui/Snowfall.svelte";
    import { correctFullName } from "$lib/utils/finnishNameUtils.js";

    /** @type {{ data: { player: any, sameTeamPlayers: any[], seasonId: string, slug: string, updatedAt: string } }} */
    let { data } = $props();

    const { player, sameTeamPlayers, seasonId, slug } = data;
    const formattedSeason = `${seasonId.substring(0, 4)}-${seasonId.substring(6, 8)}`;

    const playerName = player.skaterFullName || player.goalieFullName || "Unknown Player";
    const displayName = $derived(correctFullName(playerName));
    const teamName = player.teamAbbrevs || "NHL";
    const position = player.positionCode || "N/A";
    const isGoalie = position === "G";

    function getTeamFullName(abbrev) {
        const teamNames = {
            "BOS": "Boston Bruins",
            "BUF": "Buffalo Sabres",
            "DET": "Detroit Red Wings",
            "FLA": "Florida Panthers",
            "MTL": "Montreal Canadiens",
            "OTT": "Ottawa Senators",
            "TBL": "Tampa Bay Lightning",
            "TOR": "Toronto Maple Leafs",
            "CAR": "Carolina Hurricanes",
            "CBJ": "Columbus Blue Jackets",
            "NJD": "New Jersey Devils",
            "NYI": "New York Islanders",
            "NYR": "New York Rangers",
            "PHI": "Philadelphia Flyers",
            "PIT": "Pittsburgh Penguins",
            "WSH": "Washington Capitals",
            "ARI": "Arizona Coyotes",
            "CHI": "Chicago Blackhawks",
            "COL": "Colorado Avalanche",
            "DAL": "Dallas Stars",
            "MIN": "Minnesota Wild",
            "NSH": "Nashville Predators",
            "STL": "St. Louis Blues",
            "WPG": "Winnipeg Jets",
            "ANA": "Anaheim Ducks",
            "CGY": "Calgary Flames",
            "EDM": "Edmonton Oilers",
            "LAK": "Los Angeles Kings",
            "SJS": "San Jose Sharks",
            "SEA": "Seattle Kraken",
            "VAN": "Vancouver Canucks",
            "VGK": "Vegas Golden Knights"
        };
        return teamNames[abbrev] || abbrev;
    }

    // Helper to convert name to URL-friendly slug
    function nameToSlug(name) {
        return name.toLowerCase()
            .replace(/ä/g, 'a')
            .replace(/ö/g, 'o')
            .replace(/å/g, 'o')
            .replace(/\s+/g, '-')
            .replace(/[^a-z0-9-]/g, '');
    }

    const teamFullName = $derived(getTeamFullName(teamName));

    function getPlayerName(p) {
        return correctFullName(p.skaterFullName || p.goalieFullName);
    }

    function getPlayerSlug(p) {
        return nameToSlug(getPlayerName(p));
    }
</script>

<svelte:head>
    <title>{displayName} - {teamFullName} - Tilastot | Suomalaiset NHL:ssä</title>
    <meta
        name="description"
        content={`Katso {displayName}in tilastot kaudella {formattedSeason}. {teamFullName}, {position}, {player.gamesPlayed} ottelua, {player.goals || 0}+${player.assists || 0}={player.points || 0}.`}
    />
    <meta property="og:title" content={`${displayName} - ${teamFullName} - NHL-tilastot`} />
    <meta
        property="og:description"
        content={`${displayName} - ${teamFullName}: {player.gamesPlayed} ottelua, {player.goals || 0} maalia, {player.assists || 0} syöttöä, {player.points || 0} pistettä kaudella {formattedSeason}.`}
    />
    <meta property="og:url" content={`https://suomalaisetnhlssa.fi/pelaajat/${slug}`} />

    <!-- Person Schema for SEO -->
    {@html `<script type="application/ld+json">${JSON.stringify({
        "@context": "https://schema.org",
        "@type": "Person",
        "name": displayName,
        "jobTitle": `Professional Ice Hockey ${isGoalie ? "Goaltender" : "Player"}`,
        "memberOf": {
            "@type": "SportsTeam",
            "name": teamFullName,
            "sport": "Ice Hockey"
        },
        "nationality": {
            "@type": "Country",
            "name": "Finland"
        }
    })}</script>`}

    <!-- Breadcrumb Schema -->
    {@html `<script type="application/ld+json">${JSON.stringify({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Etusivu",
                "item": "https://suomalaisetnhlssa.fi/"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Pelaajat",
                "item": "https://suomalaisetnhlssa.fi/pelaajat"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": displayName,
                "item": `https://suomalaisetnhlssa.fi/pelaajat/${slug}`
            }
        ]
    })}</script>`}
</svelte:head>

<div class="min-h-screen bg-slate-50 relative overflow-hidden">
    <Snowfall count={8} />

    <div class="max-w-4xl mx-auto px-4 py-12 relative z-10">
        <!-- Back link -->
        <div class="mb-6">
            <a
                href={base + "/pelaajat"}
                class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 19l-7-7 7-7"
                    />
                </svg>
                Takaisin pelaajiin
            </a>
        </div>

        <!-- Player Header -->
        <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100 mb-8">
            <div class="bg-gradient-to-r from-blue-600 to-indigo-600 p-8 text-white">
                <div class="flex items-center gap-6">
                    <div class="w-32 h-32 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border-4 border-white/20">
                        <img
                            src={`${base}/headshots/${player.playerId}.webp`}
                            alt={`${displayName} - ${teamFullName}`}
                            class="w-full h-full rounded-full object-cover"
                            loading="eager"
                            onerror={(e) => {
                                e.currentTarget.style.display = 'none';
                                e.currentTarget.nextElementSibling.style.display = 'flex';
                            }}
                        />
                        <div class="w-full h-full hidden items-center justify-center text-4xl font-bold text-white">
                            {displayName.split(' ').map(n => n[0]).join('')}
                        </div>
                    </div>
                    <div>
                        <h1 class="text-3xl font-bold mb-2">{displayName}</h1>
                        <div class="flex items-center gap-3 text-blue-100">
                            <span class="font-semibold">{teamFullName}</span>
                            <span>•</span>
                            <span>{position}</span>
                            <span>•</span>
                            <span>#{player.jerseyNumber || player.playerId}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats Grid -->
            <div class="p-8">
                <h2 class="text-xl font-bold text-gray-900 mb-6">Kauden {formattedSeason} tilastot</h2>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div class="text-center p-4 bg-slate-50 rounded-xl">
                        <div class="text-3xl font-bold text-gray-900">{player.gamesPlayed}</div>
                        <div class="text-sm text-gray-500 mt-1">Ottelut</div>
                    </div>
                    <div class="text-center p-4 bg-slate-50 rounded-xl">
                        <div class="text-3xl font-bold text-gray-900">{player.goals}</div>
                        <div class="text-sm text-gray-500 mt-1">Maalit</div>
                    </div>
                    <div class="text-center p-4 bg-slate-50 rounded-xl">
                        <div class="text-3xl font-bold text-gray-900">{player.assists}</div>
                        <div class="text-sm text-gray-500 mt-1">Syötöt</div>
                    </div>
                    <div class="text-center p-4 bg-blue-50 rounded-xl border border-blue-100">
                        <div class="text-3xl font-bold text-blue-600">{player.points}</div>
                        <div class="text-sm text-blue-600 mt-1 font-medium">Pisteet</div>
                    </div>
                </div>

                {#if !isGoalie}
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mt-4">
                        <div class="text-center p-4 bg-slate-50 rounded-xl">
                            <div class="text-2xl font-bold text-gray-900">{player.plusMinus > 0 ? '+' : ''}{player.plusMinus}</div>
                            <div class="text-sm text-gray-500 mt-1">+/-</div>
                        </div>
                        <div class="text-center p-4 bg-slate-50 rounded-xl">
                            <div class="text-2xl font-bold text-gray-900">{player.penaltyMinutes || 0}</div>
                            <div class="text-sm text-gray-500 mt-1">R.min</div>
                        </div>
                        <div class="text-center p-4 bg-slate-50 rounded-xl">
                            <div class="text-2xl font-bold text-gray-900">{player.pointsPerGame?.toFixed(2) || '0.00'}</div>
                            <div class="text-sm text-gray-500 mt-1">Pisteka.</div>
                        </div>
                        <div class="text-center p-4 bg-slate-50 rounded-xl">
                            <div class="text-2xl font-bold text-gray-900">{player.shootingPct ? (player.shootingPct * 100).toFixed(1) + '%' : '-'}</div>
                            <div class="text-sm text-gray-500 mt-1">Laukais-%</div>
                        </div>
                    </div>
                {:else}
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mt-4">
                        <div class="text-center p-4 bg-slate-50 rounded-xl">
                            <div class="text-2xl font-bold text-gray-900">{player.saves || 0}</div>
                            <div class="text-sm text-gray-500 mt-1">Torjunnat</div>
                        </div>
                        <div class="text-center p-4 bg-slate-50 rounded-xl">
                            <div class="text-2xl font-bold text-gray-900">{player.goalsAgainst || 0}</div>
                            <div class="text-sm text-gray-500 mt-1">Päästetyt</div>
                        </div>
                        <div class="text-center p-4 bg-slate-50 rounded-xl">
                            <div class="text-2xl font-bold text-gray-900">{player.savePercentage ? (player.savePercentage * 100).toFixed(2) + '%' : '-'}</div>
                            <div class="text-sm text-gray-500 mt-1">Torjunta-%</div>
                        </div>
                        <div class="text-center p-4 bg-slate-50 rounded-xl">
                            <div class="text-2xl font-bold text-gray-900">{player.gamesStarted || 0}</div>
                            <div class="text-sm text-gray-500 mt-1">Aloitukset</div>
                        </div>
                    </div>
                {/if}
            </div>
        </div>

        <!-- Same Team Players (Internal Linking) -->
        {#if sameTeamPlayers.length > 0}
            <div class="bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
                <h2 class="text-xl font-bold text-gray-900 mb-4">Samassa joukkueessa pelaavat</h2>
                <p class="text-gray-600 mb-6">Muut suomalaispelaajat joukkueessa {teamFullName}:</p>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {#each sameTeamPlayers as teammate}
                        <a
                            href={`${base}/pelaajat/${getPlayerSlug(teammate)}`}
                            class="flex items-center gap-4 p-4 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50/30 transition-all group"
                        >
                            <div class="w-14 h-14 rounded-full bg-slate-100 flex-shrink-0 overflow-hidden">
                                <img
                                    src={`${base}/headshots/${teammate.playerId}.webp`}
                                    alt={`${getPlayerName(teammate)} - ${teamFullName}`}
                                    class="w-full h-full object-cover"
                                    loading="lazy"
                                    onerror={(e) => {
                                        e.currentTarget.style.display = 'none';
                                        e.currentTarget.nextElementSibling.style.display = 'flex';
                                    }}
                                />
                                <div class="w-full h-full hidden items-center justify-center text-sm font-bold text-gray-600">
                                    {getPlayerName(teammate).split(' ').map(n => n[0]).join('')}
                                </div>
                            </div>
                            <div>
                                <h3 class="font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                                    {getPlayerName(teammate)}
                                </h3>
                                <div class="text-sm text-gray-500">
                                    {teammate.points} pistettä • {teammate.positionCode}
                                </div>
                            </div>
                        </a>
                    {/each}
                </div>
            </div>
        {/if}

        <!-- Updated timestamp -->
        <div class="mt-8 text-center text-sm text-gray-400">
            Päivitetty: {new Date(data.updatedAt).toLocaleString("fi-FI")}
        </div>
    </div>
</div>
