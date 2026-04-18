<script>
// @ts-nocheck
import { getHeadshotCandidates } from '$lib/utils/playerHeadshots.js'

// biome-ignore lint/correctness/noUnusedVariables: used in template
const {
    playerId,
    // biome-ignore lint/correctness/noUnusedVariables: used in template
    alt = 'Player headshot',
    teamAbbrev = '',
    explicitUrl = '',
    seasonId = '',
    // biome-ignore lint/correctness/noUnusedVariables: used in template
    loading = 'lazy',
    // biome-ignore lint/correctness/noUnusedVariables: used in template
    imageClass = '',
    // biome-ignore lint/correctness/noUnusedVariables: used in template
    fallbackClass = '',
    // biome-ignore lint/correctness/noUnusedVariables: used in template
    initials = '',
    // biome-ignore lint/correctness/noUnusedVariables: used in template
    zoom = 1,
    // biome-ignore lint/correctness/noUnusedVariables: used in template
    objectPosition = '50% 20%',
    // biome-ignore lint/correctness/noUnusedVariables: used in template
    autoFocusFace = false,
} = $props()

let _candidateIndex = $state(0)

const _candidates = $derived(
    getHeadshotCandidates(playerId, {
        teamAbbrev,
        headshotUrl: explicitUrl,
        seasonId: seasonId || undefined,
    })
)

const _currentSrc = $derived(_candidates[_candidateIndex] || null)
const _hasImage = $derived(Boolean(_currentSrc))

$effect(() => {
    playerId
    explicitUrl
    teamAbbrev
    seasonId
    autoFocusFace
    _candidateIndex = 0
})

function _handleError() {
    if (_candidateIndex < _candidates.length - 1) {
        _candidateIndex += 1
    } else {
        _candidateIndex = _candidates.length
    }
}
</script>

{#if _hasImage}
    <img
        src={_currentSrc}
        alt={alt}
        class={imageClass}
        style={`display: block; object-position: ${objectPosition}; transform: scale(${zoom}); transform-origin: center top;`}
        {loading}
        onerror={_handleError}
    />
{:else}
    <div class={fallbackClass}>
        {#if initials}
            <span>{initials}</span>
        {/if}
    </div>
{/if}
