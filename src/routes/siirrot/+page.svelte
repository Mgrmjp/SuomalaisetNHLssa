<script>
import { base } from '$app/paths'
import OffseasonMoves from '$lib/components/game/OffseasonMoves.svelte'
import NavTabs from '$lib/components/ui/NavTabs.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'

const { data } = $props()
</script>

<svelte:head>
    <title>Suomalaisten NHL-siirrot | Suomi NHL</title>
    <meta name="description" content="Seuraa suomalaisten NHL-pelaajien offseason-siirtoja, pelaajakauppoja ja vapaan agentin sopimuksia." />
    <meta property="og:title" content="Suomalaisten NHL-siirrot | Suomi NHL" />
    <meta property="og:description" content="Suomalaispelaajien offseason-siirrot, pelaajakaupat ja vapaan agentin sopimukset." />
</svelte:head>

<PageShell width="dashboard">
    <PageHeader
        title="Suomalaisten NHL-siirrot"
        subtitle="Pelaajakaupat ja sopimukset offseason-kaudella"
        backHref={base + "/"}
        backLabel="Takaisin tuloksiin"
        children={undefined}
    />
    <div class="moves-navigation">
        <NavTabs />
    </div>
    {#if data.offseasonMoves}
        <OffseasonMoves movesData={data.offseasonMoves} />
    {:else}
        <section class="panel" aria-label="Siirtotiedot">
            <div class="panel__inner">
                <p>Siirtotiedot eivät ole vielä saatavilla.</p>
            </div>
        </section>
    {/if}
</PageShell>

<style>
    .moves-navigation {
        margin-bottom: var(--space-6);
    }
</style>
