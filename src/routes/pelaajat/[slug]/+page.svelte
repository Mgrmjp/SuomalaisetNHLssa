<script>
// @ts-nocheck
import { base } from '$app/paths'
import PlayerHeadshot from '$lib/components/ui/PlayerHeadshot.svelte'
import Snowfall from '$lib/components/ui/Snowfall.svelte'
import { correctFullName } from '$lib/utils/finnishNameUtils.js'
import { jsonLdScript } from '$lib/utils/jsonLd.js'

/** @type {{ data: { player: any, sameTeamPlayers: any[], seasonId: string, slug: string, updatedAt: string } }} */
const { data } = $props()

const { player, sameTeamPlayers, seasonId, slug } = data
const formattedSeason = `${seasonId.substring(0, 4)}-${seasonId.substring(6, 8)}`

const playerName = player.skaterFullName || player.goalieFullName || player.name || 'Unknown Player'
const displayName = $derived(correctFullName(playerName))
const teamName =
    player.profileTeamAbbrev || player.currentTeam || player.teamAbbrevs || player.lastTeam || 'NHL'
const position = player.positionCode || player.position || 'N/A'
const isGoalie = position === 'G'
const hasSeasonStats = $derived(Boolean(player.hasSeasonStats ?? !player.isRosterProfile))
const profileGamesPlayed = $derived(player.gamesPlayed ?? player.careerGamesPlayed)

function getTeamFullName(abbrev) {
    const teamNames = {
        BOS: 'Boston Bruins',
        BUF: 'Buffalo Sabres',
        DET: 'Detroit Red Wings',
        FLA: 'Florida Panthers',
        MTL: 'Montreal Canadiens',
        OTT: 'Ottawa Senators',
        TBL: 'Tampa Bay Lightning',
        TOR: 'Toronto Maple Leafs',
        CAR: 'Carolina Hurricanes',
        CBJ: 'Columbus Blue Jackets',
        NJD: 'New Jersey Devils',
        NYI: 'New York Islanders',
        NYR: 'New York Rangers',
        PHI: 'Philadelphia Flyers',
        PIT: 'Pittsburgh Penguins',
        WSH: 'Washington Capitals',
        ARI: 'Arizona Coyotes',
        CHI: 'Chicago Blackhawks',
        COL: 'Colorado Avalanche',
        DAL: 'Dallas Stars',
        MIN: 'Minnesota Wild',
        NSH: 'Nashville Predators',
        STL: 'St. Louis Blues',
        WPG: 'Winnipeg Jets',
        ANA: 'Anaheim Ducks',
        CGY: 'Calgary Flames',
        EDM: 'Edmonton Oilers',
        LAK: 'Los Angeles Kings',
        SJS: 'San Jose Sharks',
        SEA: 'Seattle Kraken',
        UTA: 'Utah Hockey Club',
        VAN: 'Vancouver Canucks',
        VGK: 'Vegas Golden Knights',
    }
    return teamNames[abbrev] || abbrev
}

// Helper to convert name to URL-friendly slug
function nameToSlug(name) {
    return name
        .toLowerCase()
        .replace(/ä/g, 'a')
        .replace(/ö/g, 'o')
        .replace(/å/g, 'o')
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '')
}

const teamFullName = $derived(getTeamFullName(teamName))
const pageTitle = $derived(
    hasSeasonStats
        ? `${displayName} - ${teamFullName} - Tilastot | Suomalaiset NHL:ssä`
        : `${displayName} - NHL-profiili | Suomalaiset NHL:ssä`
)
const ogTitle = $derived(
    hasSeasonStats
        ? `${displayName} - ${teamFullName} - NHL-tilastot`
        : `${displayName} - suomalainen NHL-pelaaja`
)
const playerDescription = $derived(
    hasSeasonStats
        ? `Katso pelaajan ${displayName} tilastot kaudella ${formattedSeason}. ${teamFullName}, ${position}, ${player.gamesPlayed || 0} ottelua, ${player.goals || 0}+${player.assists || 0}=${player.points || 0}.`
        : `Katso pelaajan ${displayName} NHL-profiili. Suomalainen ${position}, ${teamFullName}.`
)
const ogDescription = $derived(
    hasSeasonStats
        ? `${displayName} - ${teamFullName}: ${player.gamesPlayed || 0} ottelua, ${player.goals || 0} maalia, ${player.assists || 0} syöttöä, ${player.points || 0} pistettä kaudella ${formattedSeason}.`
        : `${displayName} - suomalainen NHL-pelaaja. ${teamFullName}.`
)
const playerImage = $derived(
    player.headshot && /^https?:\/\//i.test(player.headshot)
        ? player.headshot
        : player.headshot
          ? `https://cms.nhk.bamgrid.com/images/${player.headshot}`
          : undefined
)

function getPlayerName(p) {
    return correctFullName(p.skaterFullName || p.goalieFullName)
}

function getPlayerSlug(p) {
    return nameToSlug(getPlayerName(p))
}
</script>

<svelte:head>
    <title>{pageTitle}</title>
    <meta
        name="description"
        content={playerDescription}
    />
    <meta property="og:title" content={ogTitle} />
    <meta
        property="og:description"
        content={ogDescription}
    />
    <meta property="og:url" content={`https://suomalaisetnhlssa.fi/pelaajat/${slug}`} />

    <!-- Person Schema for SEO -->
    {@html jsonLdScript({
        "@context": "https://schema.org",
        "@type": "Person",
        "name": displayName,
        "url": `https://suomalaisetnhlssa.fi/pelaajat/${slug}`,
        "image": playerImage,
        "jobTitle": `Professional Ice Hockey ${isGoalie ? "Goaltender" : "Player"}`,
        "memberOf": {
            "@type": "SportsTeam",
            "name": teamFullName,
            "sport": "Ice Hockey"
        },
        "affiliation": {
            "@type": "SportsTeam",
            "name": teamFullName,
            "sport": "Ice Hockey"
        },
        "nationality": {
            "@type": "Country",
            "name": "Finland"
        }
    })}

    <!-- Breadcrumb Schema -->
    {@html jsonLdScript({
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
    })}
</svelte:head>

<div class="min-h-screen bg-slate-50 relative overflow-hidden">
    <Snowfall count={8} />

    <div class="max-w-4xl mx-auto px-3 sm:px-4 py-8 sm:py-12 relative z-10">
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
        <div class="bg-white overflow-hidden border border-slate-200 mb-6 sm:mb-8">
            <div class="bg-slate-950 p-5 sm:p-8 text-white border-b border-slate-800">
                <div class="flex flex-col sm:flex-row items-center gap-4 sm:gap-6 text-center sm:text-left">
                    <div class="w-24 h-24 sm:w-32 sm:h-32 bg-slate-900 flex items-center justify-center border border-slate-700">
                        <PlayerHeadshot
                            playerId={player.playerId}
                            explicitUrl={player.headshot}
                            teamAbbrev={teamName}
                            seasonId={seasonId}
                            alt={`${displayName} - ${teamFullName}`}
                            imageClass="w-full h-full object-cover"
                            fallbackClass="w-full h-full flex items-center justify-center text-4xl font-bold text-white"
                            initials={displayName.split(' ').map(n => n[0]).join('')}
                            loading="eager"
                        />
                    </div>
                    <div class="min-w-0">
                        <h1 class="text-2xl sm:text-3xl font-bold mb-2">{displayName}</h1>
                        <div class="flex flex-wrap items-center justify-center sm:justify-start gap-x-3 gap-y-1 text-sm sm:text-base text-slate-300">
                            <span class="font-semibold">{teamFullName}</span>
                            <span>•</span>
                            <span>{position}</span>
                            <span>•</span>
                            <span>#{player.jerseyNumber || player.sweaterNumber || player.playerId}</span>
                            {#if player.age}
                                <span>•</span>
                                <span>{player.age}v</span>
                            {/if}
                        </div>
                        {#if player.latestMove}
                            <div class="mt-3 inline-flex max-w-full border border-slate-700 px-3 py-1 text-[0.65rem] sm:text-xs uppercase tracking-[0.12em] sm:tracking-[0.18em] text-slate-300">
                                Siirtyi: {player.latestMove.oldTeam} → {player.latestMove.newTeam}
                            </div>
                        {/if}
                    </div>
                </div>
            </div>

            <!-- Stats Grid -->
            <div class="p-4 sm:p-8">
                <h2 class="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">
                    {hasSeasonStats ? `Kauden ${formattedSeason} tilastot` : 'NHL-profiili'}
                </h2>
                {#if hasSeasonStats}
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-6">
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-2xl sm:text-3xl font-bold text-gray-900">{player.gamesPlayed}</div>
                            <div class="text-sm text-gray-500 mt-1">Ottelut</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-2xl sm:text-3xl font-bold text-gray-900">{player.goals}</div>
                            <div class="text-sm text-gray-500 mt-1">Maalit</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-2xl sm:text-3xl font-bold text-gray-900">{player.assists}</div>
                            <div class="text-sm text-gray-500 mt-1">Syötöt</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-900 border border-slate-800">
                            <div class="text-2xl sm:text-3xl font-bold text-white">{player.points}</div>
                            <div class="text-sm text-slate-300 mt-1 font-medium">Pisteet</div>
                        </div>
                    </div>
                {:else}
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-6">
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-2xl sm:text-3xl font-bold text-gray-900">{profileGamesPlayed ?? '-'}</div>
                            <div class="text-sm text-gray-500 mt-1">NHL-ottelut</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-2xl sm:text-3xl font-bold text-gray-900">{teamName}</div>
                            <div class="text-sm text-gray-500 mt-1">Joukkue</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-2xl sm:text-3xl font-bold text-gray-900">{position}</div>
                            <div class="text-sm text-gray-500 mt-1">Pelipaikka</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-900 border border-slate-800">
                            <div class="text-base sm:text-xl font-bold text-white">{player.birthplace || 'Suomi'}</div>
                            <div class="text-sm text-slate-300 mt-1 font-medium">Syntymäpaikka</div>
                        </div>
                    </div>
                {/if}

                {#if hasSeasonStats && !isGoalie}
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-6 mt-3 sm:mt-4">
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-xl sm:text-2xl font-bold text-gray-900">{player.plusMinus > 0 ? '+' : ''}{player.plusMinus}</div>
                            <div class="text-sm text-gray-500 mt-1">+/-</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-xl sm:text-2xl font-bold text-gray-900">{player.penaltyMinutes || 0}</div>
                            <div class="text-sm text-gray-500 mt-1">R.min</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-xl sm:text-2xl font-bold text-gray-900">{player.pointsPerGame?.toFixed(2) || '0.00'}</div>
                            <div class="text-sm text-gray-500 mt-1">Pisteka.</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-xl sm:text-2xl font-bold text-gray-900">{player.shootingPct ? (player.shootingPct * 100).toFixed(1) + '%' : '-'}</div>
                            <div class="text-sm text-gray-500 mt-1">Laukais-%</div>
                        </div>
                    </div>
                {:else if hasSeasonStats}
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-6 mt-3 sm:mt-4">
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-xl sm:text-2xl font-bold text-gray-900">{player.saves || 0}</div>
                            <div class="text-sm text-gray-500 mt-1">Torjunnat</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-xl sm:text-2xl font-bold text-gray-900">{player.goalsAgainst || 0}</div>
                            <div class="text-sm text-gray-500 mt-1">Päästetyt</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-xl sm:text-2xl font-bold text-gray-900">{player.savePercentage ? (player.savePercentage * 100).toFixed(2) + '%' : '-'}</div>
                            <div class="text-sm text-gray-500 mt-1">Torjunta-%</div>
                        </div>
                        <div class="text-center p-3 sm:p-4 bg-slate-50 border border-slate-200">
                            <div class="text-xl sm:text-2xl font-bold text-gray-900">{player.gamesStarted || 0}</div>
                            <div class="text-sm text-gray-500 mt-1">Aloitukset</div>
                        </div>
                    </div>
                {/if}
            </div>
        </div>

        <!-- Same Team Players (Internal Linking) -->
        {#if sameTeamPlayers.length > 0}
            <div class="bg-white border border-slate-200 p-4 sm:p-8">
                <h2 class="text-lg sm:text-xl font-bold text-gray-900 mb-3 sm:mb-4">Samassa joukkueessa pelaavat</h2>
                <p class="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6">Muut suomalaispelaajat joukkueessa {teamFullName}:</p>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {#each sameTeamPlayers as teammate}
                        <a
                            href={`${base}/pelaajat/${getPlayerSlug(teammate)}`}
                            class="flex items-center gap-3 sm:gap-4 p-3 sm:p-4 border border-slate-200 hover:border-slate-400 hover:bg-slate-50 transition-all group"
                        >
                            <div class="w-12 h-12 sm:w-14 sm:h-14 bg-slate-100 flex-shrink-0 overflow-hidden">
                                <PlayerHeadshot
                                    playerId={teammate.playerId}
                                    teamAbbrev={teammate.teamAbbrevs}
                                    seasonId={seasonId}
                                    alt={`${getPlayerName(teammate)} - ${teamFullName}`}
                                    imageClass="w-full h-full object-cover"
                                    fallbackClass="w-full h-full flex items-center justify-center text-sm font-bold text-gray-600"
                                    initials={getPlayerName(teammate).split(' ').map(n => n[0]).join('')}
                                    loading="lazy"
                                />
                            </div>
                            <div>
                                <h3 class="font-bold text-gray-900 group-hover:text-slate-700 transition-colors">
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
