<script>
    import { base } from "$app/paths";

    let { team, size = "48", className = "" } = $props();

    const teamFullNames = {
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

    function getTeamLogoUrl(teamAbbrev) {
        const normalizedTeam = (teamAbbrev || "").toString().toLowerCase().trim();
        if (!normalizedTeam) return `${base}/nhl-logos/placeholder.svg`;

        const pathPrefix = base === "" || base === "." ? "" : base;
        return `${pathPrefix}/nhl-logos/${normalizedTeam}.svg`;
    }

    const logoUrl = $derived(getTeamLogoUrl(team));
    const teamFullName = $derived(teamFullNames[team] || team);
</script>

<div class="team-logo-wrapper {className}" style={`--logo-size: ${size}px`}>
    <img
        src={logoUrl}
        alt="{teamFullName} logo"
        class="team-logo"
        width={size}
        height={size}
        loading="eager"
        onerror={(e) => {
            e.currentTarget.src = `${base}/nhl-logos/placeholder.svg`;
        }}
    />
</div>

<style>
    .team-logo-wrapper {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: var(--logo-size);
        height: var(--logo-size);
    }

    .team-logo {
        display: block;
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
</style>
