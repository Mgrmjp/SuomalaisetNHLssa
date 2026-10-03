<script>
// @ts-nocheck

import { onMount } from 'svelte'
import Button from '$lib/components/ui/Button.svelte'
import ControlGroup from '$lib/components/ui/ControlGroup.svelte'
import Notice from '$lib/components/ui/Notice.svelte'
import ViewMetadata from '$lib/components/ui/ViewMetadata.svelte'
import ViewState from '$lib/components/ui/ViewState.svelte'
import { isStandingsStale } from '$lib/services/standingsService.js'
import {
    loadStandings,
    refreshStandings,
    standings,
    standingsLoading,
    standingsMetadata,
} from '$lib/stores/gameData.js'
import ConferenceStandings from './ConferenceStandings.svelte'

let error = $state('')
let activeConference = $state('eastern')
let showAdvancedStats = $state(false)
let now = $state(Date.now())
const hasData = $derived(Boolean($standingsMetadata))
const stale = $derived(hasData && isStandingsStale($standingsMetadata, now))
const season = $derived(
    $standingsMetadata
        ? `${String($standingsMetadata.seasonId).slice(0, 4)}–${String($standingsMetadata.seasonId).slice(6)}`
        : ''
)
const formatDate = (date) =>
    new Date(date).toLocaleDateString('fi-FI', { timeZone: 'Europe/Helsinki' })
const formatTime = (date) =>
    new Date(date).toLocaleString('fi-FI', {
        timeZone: 'Europe/Helsinki',
        dateStyle: 'short',
        timeStyle: 'short',
    })

async function reload(force = false) {
    error = ''
    try {
        await (force ? refreshStandings() : loadStandings())
    } catch (err) {
        error = err.message || 'Sarjataulukon lataaminen epäonnistui.'
    }
}
onMount(() => {
    reload()
    const timer = setInterval(() => {
        now = Date.now()
    }, 60000)
    const refreshTimer = setInterval(() => {
        if (!document.hidden) reload(true)
    }, 5 * 60000)
    return () => {
        clearInterval(timer)
        clearInterval(refreshTimer)
    }
})
</script>

<div class="standings-view">
    <div class="view-toolbar">
        <div>
            <h2 class="section-title">NHL {season}</h2>
            <p class="view-description">Virallinen runkosarjan sarjataulukko</p>
        </div>
        <div class="view-actions">
            <ControlGroup label="Konferenssi">
                <Button selected={activeConference === 'eastern'} onclick={() => activeConference = 'eastern'}>Itäinen</Button>
                <Button selected={activeConference === 'western'} onclick={() => activeConference = 'western'}>Läntinen</Button>
            </ControlGroup>
            <Button selected={showAdvancedStats} onclick={() => showAdvancedStats = !showAdvancedStats}>Lisätilastot</Button>
            <Button disabled={$standingsLoading} onclick={() => reload(true)}>{$standingsLoading ? 'Ladataan…' : 'Päivitä'}</Button>
        </div>
    </div>
    {#if (stale || error) && hasData}
        <Notice variant="warning">
            {error ? 'Päivitys epäonnistui. Näytetään viimeisin onnistunut sarjataulukko.' : 'Sarjataulukon tarkistuksesta on yli kolme tuntia.'}
            <span>Tarkistettu {formatTime($standingsMetadata.fetchedAt)}.</span>
        </Notice>
    {/if}
    {#if $standingsLoading && !hasData}
        <ViewState busy message="Ladataan virallista sarjataulukkoa…" />
    {:else if !hasData}
        <ViewState title="Sarjataulukkoa ei ole saatavilla" message={error || 'Viralliset tiedot eivät ole vielä saatavilla.'}>
            {#snippet actions()}
                <Button onclick={() => reload(true)}>Yritä uudelleen</Button>
            {/snippet}
        </ViewState>
    {:else}
        <ConferenceStandings conferenceData={$standings[activeConference]} conferenceName={activeConference}
            wildCardTeams={$standingsMetadata.wildCards[activeConference]} {showAdvancedStats} />
        <ViewMetadata>
            <p>Lähde: <a href="https://www.nhl.com/standings" target="_blank" rel="noreferrer">NHL</a> · Tiedot {formatDate(`${$standingsMetadata.sourceDate}T12:00:00Z`)} · Tarkistettu {formatTime($standingsMetadata.fetchedAt)}</p>
            <p>Päivittyy tunnin välein ja ottelutulosten päivitysten yhteydessä.</p>
        </ViewMetadata>
    {/if}
</div>

<style>
    .standings-view { display: grid; gap: var(--space-5); min-width: 0; }
</style>
