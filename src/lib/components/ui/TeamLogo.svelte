<script>
import { base } from '$app/paths'

export let team
export let size = '24'

// Use local NHL team logos (with base path) to avoid remote fetches

function getTeamLogoUrl(teamAbbrev) {
    const normalizedTeam = (teamAbbrev || '').toString().toLowerCase().trim()
    if (!normalizedTeam) return `${base}/nhl-logos/placeholder.svg`

    return `${base}/nhl-logos/${normalizedTeam}.svg`
}

$: logoUrl = getTeamLogoUrl(team)
</script>

<div class="team-logo-wrapper" style={`--logo-size: ${size}px`}>
	<img
	  src={logoUrl}
	  alt="{team} logo"
	  class="team-logo"
	  width={size}
	  height={size}
	  loading="eager"
	  on:error={(event) => {
	    // Final fallback to placeholder if local logo fails
	    event.target.src = `${base}/nhl-logos/placeholder.svg`;
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
