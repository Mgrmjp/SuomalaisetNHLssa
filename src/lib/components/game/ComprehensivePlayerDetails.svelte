<script>
import { base } from '$app/paths'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { games } from '$lib/stores/gameData.js'
import { isPlayerGameLive } from '$lib/utils/gameStateHelpers.mjs'

const { player, isOpen = false, onclose } = $props()

let _playerPhotoUrl = $state(null)
let _photoError = $state(false)
let _imageLoading = $state(true)
let _lqipUrl = $state(null)
let _imageLoaded = $state(false)

function getLocalHeadshotUrl(playerId) {
    if (!playerId) return null
    return `/headshots/${playerId}.webp`
}

function loadPlayerImage(playerId) {
    if (!playerId) return
    _imageLoading = true
    _photoError = false
    _lqipUrl = getLocalHeadshotUrl(playerId)
    
    const localUrl = getLocalHeadshotUrl(playerId)
    const img = new Image()
    
    img.onload = () => {
        _playerPhotoUrl = localUrl
        _photoError = false
        _imageLoading = false
    }
    
    img.onerror = () => {
        if (player.headshot_url) {
            _playerPhotoUrl = player.headshot_url
            _photoError = false
        } else {
            _photoError = true
            _playerPhotoUrl = null
        }
        _imageLoading = false
    }
    
    img.src = localUrl
}

$effect(() => {
    if (player?.playerId) {
        loadPlayerImage(player.playerId)
    }
})

function portal(node) {
    const placeholder = document.createElement('div')
    placeholder.className = 'portal-placeholder'
    placeholder.style.cssText = 'display: none;'
    node.parentNode.insertBefore(placeholder, node)
    node._portalPlaceholder = placeholder
    document.body.appendChild(node)
    return {
        update() {
            if (node.parentNode !== document.body) {
                document.body.appendChild(node)
            }
        },
        destroy() {
            if (document.body.contains(node)) {
                document.body.removeChild(node)
            }
            if (node._portalPlaceholder?.parentNode) {
                node._portalPlaceholder.parentNode.removeChild(node._portalPlaceholder)
            }
        },
    }
}

const displayName = $derived(player.name?.default || player.name || 'Unknown Player')
const gamesData = $derived($games)
const _isLive = $derived(isPlayerGameLive(player, gamesData))
const _playerInitials = $derived(displayName.split(' ').map((p) => p.charAt(0).toUpperCase()).join('').slice(0, 2))
const isGoalie = $derived((player.position || '').toUpperCase() === 'G' || (player.position || '').toUpperCase() === 'GOALIE')
const _goalieSavePct = $derived(getSavePercentage(player))

function getSavePercentage(player) {
    const provided = player.save_percentage ?? player.savePercentage
    if (typeof provided === 'number' && provided > 0) {
        return Number(provided > 1 ? provided : (provided * 100).toFixed(1))
    }
    const saves = Number(player.saves ?? player.goalie_saves)
    const shotsAgainst = Number(player.shots_against ?? player.shotsAgainst)
    if (Number.isFinite(saves) && Number.isFinite(shotsAgainst) && shotsAgainst > 0) {
        return Number(((saves / shotsAgainst) * 100).toFixed(1))
    }
    return null
}

function handleBackdropClick(e) {
    if (e.target === e.currentTarget) {
        onclose?.()
    }
}

</script>

{#if isOpen}
    <div
        use:portal
        class="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-[100]"
        onclick={handleBackdropClick}
        role="button"
        tabindex="0"
        onkeydown={(e) => e.key === "Escape" && onclose?.()}
    >
        <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="p-6">
                <!-- Header -->
                <div class="flex items-start gap-4 mb-6">
                    {#if _playerPhotoUrl || _lqipUrl}
                        <img
                            src={_playerPhotoUrl || _lqipUrl}
                            alt={displayName}
                            class="w-32 h-32 rounded-full object-cover shrink-0"
                        />
                    {:else}
                        <div class="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center text-4xl font-bold text-gray-500 shrink-0">
                            {_playerInitials}
                        </div>
                    {/if}
                    <div class="flex-1 pt-2">
                        <h2 class="text-2xl font-bold text-gray-900">{displayName}</h2>
                        <div class="text-gray-600">{player.team_full || player.team || "Unknown Team"}</div>
                    </div>
                    <button onclick={onclose} class="shrink-0 w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 hover:text-gray-700 transition-colors cursor-pointer">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                    </button>
                </div>

                <!-- Game Stats -->
                <div class="bg-gray-50 rounded-lg p-4 mb-6">
                    <h3 class="text-sm font-semibold text-gray-500 mb-3">Pelin tilastot</h3>
                    
                    {#if isGoalie}
                        <div class="grid grid-cols-4 gap-4 text-center">
                            <div>
                                <div class="text-2xl font-bold text-gray-900">{player.saves || 0}</div>
                                <div class="text-xs text-gray-500">Torjunnat</div>
                            </div>
                            <div>
                                <div class="text-2xl font-bold text-gray-900">{player.goals_against || 0}</div>
                                <div class="text-xs text-gray-500">Päästetyt</div>
                            </div>
                            <div>
                                <div class="text-2xl font-bold text-gray-900">{_goalieSavePct || 0}%</div>
                                <div class="text-xs text-gray-500">Torjunta-%</div>
                            </div>
                            <div>
                                <div class="text-2xl font-bold text-gray-900">{player.time_on_ice || '-'}</div>
                                <div class="text-xs text-gray-500">Peliaika</div>
                            </div>
                        </div>
                    {:else}
                        <div class="grid grid-cols-4 gap-4 text-center">
                            <div>
                                <div class="text-2xl font-bold text-gray-900">{player.goals || 0}</div>
                                <div class="text-xs text-gray-500">Maalit</div>
                            </div>
                            <div>
                                <div class="text-2xl font-bold text-gray-900">{player.assists || 0}</div>
                                <div class="text-xs text-gray-500">Syötöt</div>
                            </div>
                            <div>
                                <div class="text-2xl font-bold text-blue-600">{player.points || 0}</div>
                                <div class="text-xs text-gray-500">Pisteet</div>
                            </div>
                            <div>
                                <div class="text-2xl font-bold {player.plus_minus >= 0 ? 'text-green-600' : 'text-red-600'}">
                                    {player.plus_minus > 0 ? '+' : ''}{player.plus_minus ?? 0}
                                </div>
                                <div class="text-xs text-gray-500">+/-</div>
                            </div>
                        </div>
                    {/if}
                </div>

                <!-- Additional Stats -->
                {#if !isGoalie && (player.shots || player.hits || player.blocked_shots || player.takeaways || player.giveaways)}
                    <div class="bg-gray-50 rounded-lg p-4 mb-6">
                        <h3 class="text-sm font-semibold text-gray-500 mb-3">Muut tilastot</h3>
                        <div class="flex flex-wrap gap-6 text-sm">
                            {#if player.shots > 0}
                                <div><span class="font-semibold">{player.shots}</span> <span class="text-gray-500">Laukaukset</span></div>
                            {/if}
                            {#if player.hits > 0}
                                <div><span class="font-semibold">{player.hits}</span> <span class="text-gray-500">Taklaukset</span></div>
                            {/if}
                            {#if player.blocked_shots > 0}
                                <div><span class="font-semibold">{player.blocked_shots}</span> <span class="text-gray-500">Blokit</span></div>
                            {/if}
                            {#if player.takeaways > 0}
                                <div><span class="font-semibold">{player.takeaways}</span> <span class="text-gray-500">Riistot</span></div>
                            {/if}
                            {#if player.giveaways > 0}
                                <div><span class="font-semibold">{player.giveaways}</span> <span class="text-gray-500">Menetykset</span></div>
                            {/if}
                        </div>
                    </div>
                {/if}

                <!-- Recent Games -->
                {#if player.recent_results && player.recent_results.length > 0}
                    <div>
                        <h3 class="text-sm font-semibold text-gray-500 mb-3">Viimeisimmät pelit</h3>
                        <div class="space-y-2">
                            {#each player.recent_results.slice(0, 5) as game}
                                {@const isWin = game.result === 'W' || game.result === 'OTW' || game.result === 'SOW'}
                                {@const opponentCode = game.opponent?.toLowerCase()}
                                <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                    <div class="w-10 text-xs text-gray-500">{parseInt(game.date.split('-')[2])}.{parseInt(game.date.split('-')[1])}.</div>
                                    <div class="w-8 text-center">
                                        <img src="/nhl-logos/{opponentCode}.svg" alt={game.opponent} class="w-6 h-6 mx-auto" onerror={(e) => e.target.style.display = 'none'} />
                                    </div>
                                    <div class="flex-1 text-sm">{game.opponent_full || game.opponent}</div>
                                    <div class="text-sm font-semibold {isWin ? 'text-green-600' : 'text-red-600'}">
                                        {game.team_score} - {game.opponent_score}
                                    </div>
                                    <div class="w-4 h-4 rounded-full {isWin ? 'bg-green-500' : 'bg-red-500'}"></div>
                                    <div class="flex gap-3 text-xs text-gray-500">
                                        {#if !isGoalie}
                                            <span>M: {game.goals ?? 0}</span>
                                            <span>S: {game.assists ?? 0}</span>
                                            <span>P: {game.points ?? 0}</span>
                                        {:else}
                                            <span>T: {game.saves ?? 0}</span>
                                            <span>P: {game.goals_against ?? 0}</span>
                                        {/if}
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    </div>
{/if}
