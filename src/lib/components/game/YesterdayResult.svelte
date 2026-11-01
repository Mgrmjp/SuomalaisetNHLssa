<script>
// @ts-nocheck
import { ArrowLeft, CircleDot, Goal, Users } from 'lucide-svelte'
import { base } from '$app/paths'
import PlayerHeadshot from '$lib/components/ui/PlayerHeadshot.svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { currentDateReadOnly, prepopulatedDates, setDate } from '$lib/stores/gameData.js'
import { dailyPlayerPoints } from '$lib/utils/dailyPlayers.js'
import { formatFinnishDate } from '$lib/utils/dateUtils.js'
import { correctFullName } from '$lib/utils/finnishNameUtils.js'
import { getSavePercentage, isGoalie } from '$lib/utils/positionHelpers.js'
import { selectYesterdayResult } from '$lib/utils/yesterdayResult.js'

const { date } = $props()
let loaded = $state(null)
let loading = $state(true)
let failed = $state(false)
// Retain one random choice while the visitor stays on this view, including refreshes.
const random = Math.random()
const refreshMinute = $derived(Math.floor($currentDateReadOnly.getTime() / 60000))
const result = $derived(loaded?.date === date ? loaded.result : null)
const totals = $derived({
    goals: result?.players.reduce((sum, player) => sum + (Number(player.goals) || 0), 0) || 0,
    assists: result?.players.reduce((sum, player) => sum + (Number(player.assists) || 0), 0) || 0,
})
const dateLabel = $derived(formatFinnishDate(date, { showWeekday: false }))

$effect(() => {
    const requestedDate = date
    const dates = $prepopulatedDates
    refreshMinute
    const controller = new AbortController()
    loading = true
    failed = false
    if (!dates.includes(requestedDate)) {
        loading = false
        return
    }
    async function load() {
        try {
            const response = await fetch(`${base}/data/prepopulated/games/${requestedDate}.json`, {
                signal: controller.signal,
                cache: 'no-cache',
            })
            if (!response.ok) throw new Error('Results unavailable')
            const snapshot = await response.json()
            if (!controller.signal.aborted) {
                const next = selectYesterdayResult(snapshot, requestedDate, random)
                if (next) loaded = { date: requestedDate, result: next }
            }
        } catch {
            if (!controller.signal.aborted) failed = true
        } finally {
            if (!controller.signal.aborted) loading = false
        }
    }
    load()
    return () => controller.abort()
})

function playerName(player) {
    return correctFullName(player.name?.default || player.name || player.fullName || '')
}
</script>

<section class="yesterday-result" aria-labelledby="yesterday-result-title" aria-busy={loading}>
    <div class="yesterday-result__heading">
        <div>
            <p class="yesterday-result__eyebrow">Poiminta eiliseltä</p>
            <h3 id="yesterday-result-title">{dateLabel}</h3>
        </div>
        <button type="button" class="yesterday-result__back" onclick={() => setDate(date)}>
            <ArrowLeft aria-hidden="true" /> Eilisen tulokset
        </button>
    </div>

    {#if result}
        <div class="yesterday-result__scoreboard">
            <div class="yesterday-result__team">
                <TeamLogo team={result.game.awayTeam} size="64" />
                <strong>{result.game.awayTeam}</strong>
            </div>
            <div class="yesterday-result__score">
                <strong aria-label={`${result.game.awayTeam} ${result.game.awayScore}, ${result.game.homeTeam} ${result.game.homeScore}`}>{result.game.awayScore} – {result.game.homeScore}</strong>
                <span>Lopputulos{result.game.isSO ? ' · VL' : result.game.isOT ? ' · JA' : ''}</span>
            </div>
            <div class="yesterday-result__team yesterday-result__team--home">
                <strong>{result.game.homeTeam}</strong>
                <TeamLogo team={result.game.homeTeam} size="64" />
            </div>
        </div>

        <p class="yesterday-result__totals-label">Suomalaisten tilastot</p>
        <dl class="yesterday-result__totals" aria-label="Suomalaisten tilastot ottelussa">
            <div><dt><Goal aria-hidden="true" /> Maalit</dt><dd>{totals.goals}</dd></div>
            <div><dt><CircleDot aria-hidden="true" /> Syötöt</dt><dd>{totals.assists}</dd></div>
            <div><dt><Users aria-hidden="true" /> Suomalaisia</dt><dd>{result.players.length}</dd></div>
        </dl>

        <h4 class="yesterday-result__players-title">Suomalaiset ottelussa</h4>
        <div class="yesterday-result__players">
            {#each result.players as player (player.playerId)}
                {@const name = playerName(player)}
                <div class="yesterday-result__player">
                    <div class="yesterday-result__portrait">
                        <PlayerHeadshot playerId={player.playerId} teamAbbrev={player.team} explicitUrl={player.headshot_url} alt={name} initials={name.split(' ').map((part) => part[0]).slice(0, 2).join('')} imageClass="yesterday-result__photo" fallbackClass="yesterday-result__initials" />
                    </div>
                    <div class="yesterday-result__identity">
                        <strong>{name}</strong>
                        <span>{player.team} · {player.position || player.positionCode}{#if player.jersey_number || player.jerseyNumber} · #{player.jersey_number || player.jerseyNumber}{/if}</span>
                    </div>
                    {#if isGoalie(player)}
                        {@const savePct = getSavePercentage(player)}
                        <div class="yesterday-result__player-stat"><strong>{player.saves ?? player.goalie_saves ?? '–'}</strong><span>torjuntaa</span></div>
                        <div class="yesterday-result__player-stat"><strong>{savePct == null ? '–' : (savePct * 100).toLocaleString('fi-FI', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}</strong><span>torjunta-%</span></div>
                    {:else}
                        <div class="yesterday-result__player-stat"><strong>{player.goals || 0}</strong><span>{Number(player.goals) === 1 ? 'maali' : 'maalia'}</span></div>
                        <div class="yesterday-result__player-stat"><strong>{player.assists || 0}</strong><span>{Number(player.assists) === 1 ? 'syöttö' : 'syöttöä'}</span></div>
                        <div class="yesterday-result__player-stat" class:yesterday-result__player-stat--points={dailyPlayerPoints(player) > 0}><strong>{dailyPlayerPoints(player)}</strong><span>{dailyPlayerPoints(player) === 1 ? 'piste' : 'pistettä'}</span></div>
                    {/if}
                </div>
            {/each}
        </div>
    {:else}
        <p class="yesterday-result__unavailable" role="status">
            {loading ? 'Haetaan eilisen ottelupoimintaa…' : failed ? 'Eilisen ottelupoimintaa ei saatu ladattua.' : 'Eiliseltä ei ole vielä valmiita ottelutuloksia suomalaispelaajille.'}
        </p>
    {/if}
</section>

<style>
    .yesterday-result { min-width: 0; margin-top: 1.25rem; }
    .yesterday-result__heading { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 0.75rem; }
    .yesterday-result__eyebrow { margin: 0 0 0.2rem; color: var(--color-muted); font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
    .yesterday-result__heading h3 { margin: 0; color: var(--color-ink); font-size: 1rem; font-weight: 700; }
    .yesterday-result__back { display: inline-flex; align-items: center; justify-content: center; gap: 0.4rem; min-height: 2.5rem; padding: 0.5rem 0.75rem; border: 1px solid var(--accent); border-radius: var(--card-radius-sm); background: var(--accent); color: white; font-size: 0.75rem; font-weight: 700; text-decoration: none; cursor: pointer; }
    .yesterday-result__back:hover { background: var(--accent-strong); }
    .yesterday-result__back :global(svg) { width: 1rem; height: 1rem; }
    .yesterday-result__scoreboard { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 0.5rem; padding: 1rem 0.75rem; border: var(--card-border); border-radius: var(--card-radius); background: var(--card-bg); box-shadow: 0 3px 10px #2a5b9110; }
    .yesterday-result__team { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 0.5rem; font-size: 1.1rem; }
    .yesterday-result__score { display: grid; justify-items: center; gap: 0.4rem; }
    .yesterday-result__score > strong { color: var(--color-ink); font-size: clamp(1.5rem, 3vw, 2.25rem); font-weight: 800; white-space: nowrap; font-variant-numeric: tabular-nums; }
    .yesterday-result__score > span { padding: 0.2rem 0.5rem; border-radius: 1rem; background: #dce9f8; color: var(--color-muted); font-size: 0.65rem; font-weight: 600; }
    .yesterday-result__totals-label { margin: 0.75rem 0 0; color: var(--color-muted); font-size: 0.65rem; font-weight: 600; text-align: center; }
    .yesterday-result__totals { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin: 0.75rem 0 1.25rem; }
    .yesterday-result__totals > div { display: flex; flex-direction: column; align-items: center; gap: 0.2rem; padding: 0.35rem; }
    .yesterday-result__totals > div + div { border-left: var(--card-border); }
    .yesterday-result__totals dt { display: flex; align-items: center; gap: 0.3rem; color: var(--color-muted); font-size: 0.75rem; }
    .yesterday-result__totals dt :global(svg) { width: 1rem; height: 1rem; }
    .yesterday-result__totals dd { order: -1; margin: 0; font-size: 1.4rem; font-weight: 800; }
    .yesterday-result__players-title { margin: 0 0 0.6rem; font-size: 1.1rem; font-weight: 800; }
    .yesterday-result__players { display: grid; gap: 0.5rem; }
    .yesterday-result__player { display: flex; align-items: center; gap: 0.65rem; padding: 0.65rem; border: var(--card-border); border-radius: 12px; background: var(--card-bg); }
    .yesterday-result__portrait { flex: 0 0 3rem; width: 3rem; height: 3rem; overflow: hidden; border: 1px solid #dce7f5; border-radius: 50%; background: white; }
    .yesterday-result__portrait :global(.yesterday-result__photo), .yesterday-result__portrait :global(.yesterday-result__initials) { width: 100%; height: 100%; object-fit: cover; }
    .yesterday-result__portrait :global(.yesterday-result__initials) { display: grid; place-items: center; color: var(--color-muted); font-size: 0.8rem; font-weight: 700; }
    .yesterday-result__identity { display: grid; flex: 1; gap: 0.2rem; min-width: 0; }
    .yesterday-result__identity strong { font-size: 0.85rem; overflow-wrap: anywhere; }
    .yesterday-result__identity > span { font-size: 0.65rem; color: var(--color-muted); }
    .yesterday-result__player-stat { display: grid; justify-items: center; gap: 0.15rem; min-width: 3rem; padding: 0.4rem; border-radius: 6px; }
    .yesterday-result__player-stat > strong { font-size: 1rem; font-weight: 800; }
    .yesterday-result__player-stat > span { font-size: 0.65rem; color: var(--color-muted); }
    .yesterday-result__player-stat--points { background: #dff5e3; }
    .yesterday-result__unavailable { margin: 0; padding: 1.25rem; border: var(--card-border); border-radius: var(--card-radius-sm); color: var(--color-muted); font-size: 0.8rem; line-height: 1.6; }
    @media (max-width: 480px) {
        .yesterday-result__team { flex-direction: column; gap: 0.25rem; font-size: 0.9rem; }
        .yesterday-result__team--home { flex-direction: column-reverse; }
        .yesterday-result__team :global(.team-logo-wrapper) { width: 44px; height: 44px; }
        .yesterday-result__player { flex-wrap: wrap; gap: 0.5rem; }
        .yesterday-result__identity { flex-basis: calc(100% - 4rem); }
        .yesterday-result__player-stat { flex: 1; }
    }
</style>
