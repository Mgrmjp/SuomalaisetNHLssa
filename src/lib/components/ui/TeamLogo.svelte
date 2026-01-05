<script>
    import { base } from "$app/paths";

    let { team, size = "48", className = "" } = $props();

    function getTeamLogoUrl(teamAbbrev) {
        const normalizedTeam = (teamAbbrev || "").toString().toLowerCase().trim();
        if (!normalizedTeam) return `${base}/nhl-logos/placeholder.svg`;

        const pathPrefix = base === "" || base === "." ? "" : base;
        return `${pathPrefix}/nhl-logos/${normalizedTeam}.svg`;
    }

    const logoUrl = $derived(getTeamLogoUrl(team));
</script>

<div class="team-logo-wrapper {className}" style={`--logo-size: ${size}px`}>
    <img
        src={logoUrl}
        alt="{team} logo"
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
