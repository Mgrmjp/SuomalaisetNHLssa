<script>
// @ts-nocheck

import {
    Users as JoukkueetIcon,
    Sparkles as LupauksetIcon,
    ClipboardList as PisteporssiIcon,
    BarChart3 as SarjataulukkoIcon,
    ArrowLeftRight as SiirrotIcon,
    Activity as TuloksetIcon,
} from 'lucide-svelte'
import { base } from '$app/paths'
import { page } from '$app/stores'
import ControlGroup from '$lib/components/ui/ControlGroup.svelte'
import { PROSPECTS_ENABLED, TRANSFERS_ENABLED } from '$lib/config/features.js'

// Navigation items
const _navItems = [
    {
        href: `${base}/`,
        label: 'Tulokset',
        Icon: TuloksetIcon,
    },
    {
        href: `${base}/siirrot`,
        label: 'Siirrot',
        Icon: SiirrotIcon,
        enabled: TRANSFERS_ENABLED,
    },
    {
        href: `${base}/sarjataulukko`,
        label: 'Sarjataulukko',
        Icon: SarjataulukkoIcon,
    },
    {
        href: `${base}/joukkueet`,
        label: 'Joukkueet',
        Icon: JoukkueetIcon,
    },
    {
        href: `${base}/pisteporssi`,
        label: 'Pistepörssi',
        Icon: PisteporssiIcon,
    },
    {
        href: `${base}/lupaukset`,
        label: 'Lupaukset',
        Icon: LupauksetIcon,
        enabled: PROSPECTS_ENABLED,
    },
].filter((item) => item.enabled !== false)

const currentPath = $derived($page.url.pathname)
</script>

<nav class="nav-tabs-container" aria-label="Päänavigaatio">
    <ControlGroup label="Päänavigaation sivut" class="nav-tabs-list" scrollable>
        {#each _navItems as item}
            {@const isActive =
                currentPath === item.href ||
                (item.href !== `${base}/` && currentPath.startsWith(item.href))}
            <a
                href={item.href}
                class="nav-tab-item ui-control group"
                class:nav-tab-item--active={isActive}
                class:ui-control--selected={isActive}
                aria-current={isActive ? 'page' : undefined}
            >
                <item.Icon class="nav-tab-icon" aria-hidden="true" />
                {item.label}
            </a>
        {/each}
    </ControlGroup>
</nav>

<style>
.nav-tabs-container {
    --toolbar-control-height: 2.5rem;
    --toolbar-radius: 14px;
    --toolbar-padding: 0.25rem;
    --card-radius-sm: calc(var(--toolbar-radius) - var(--toolbar-padding) - 1px);
    display: flex;
    justify-content: center;
    width: fit-content;
    min-width: 0;
    max-width: 100%;
    margin: 0 auto;
    padding: 0;
}

.nav-tabs-container :global(.nav-tabs-list) {
    gap: 0.2rem;
    padding: var(--toolbar-padding);
    border: 1px solid white;
    border-radius: var(--toolbar-radius);
    background: rgba(245, 250, 255, 0.96);
    box-shadow:
        0 5px 18px rgba(31, 83, 141, 0.2),
        0 0 0 1px #bdd9f7;
}

.nav-tab-item {
    position: relative;
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    height: var(--toolbar-control-height);
    min-height: var(--toolbar-control-height);
    padding: 0 1.25rem;
    border-radius: var(--card-radius-sm);
    color: #475467;
    font-size: 0.8125rem;
    font-weight: 600;
    line-height: 1;
    text-decoration: none;
    white-space: nowrap;
    transition:
        background 0.16s ease,
        color 0.16s ease;
}

.nav-tab-item:hover {
    color: var(--color-ink);
    background: rgba(16, 24, 40, 0.04);
}

.nav-tab-item:focus-visible {
    outline: 3px solid rgba(16, 24, 40, 0.18);
    outline-offset: 2px;
}

.nav-tab-item--active,
.nav-tab-item--active:hover {
    background: var(--accent);
    color: white;
    box-shadow: 0 2px 5px #00358030;
}

.nav-tab-item :global(.nav-tab-icon) {
    width: 1.05rem;
    height: 1.05rem;
    color: #98a2b3;
    flex-shrink: 0;
    transition: color 0.16s ease;
}

.nav-tab-item:hover :global(.nav-tab-icon) {
    color: var(--accent);
}
.nav-tab-item--active :global(.nav-tab-icon),
.nav-tab-item--active:hover :global(.nav-tab-icon) {
    color: white;
}

@media (max-width: 767px) {
    .nav-tabs-container {
        --toolbar-control-height: 2.75rem;
        width: 100%;
    }
    .nav-tabs-container :global(.nav-tabs-list) {
        display: grid;
        grid-auto-flow: column;
        grid-auto-columns: minmax(0, 1fr);
        width: 100%;
        overflow: visible;
    }
    .nav-tab-item {
        min-width: 0;
        padding-inline: 0;
        flex-direction: column;
        gap: 0.15rem;
        font-size: clamp(0.6rem, 2.2vw, 0.75rem);
    }
    .nav-tab-item :global(.nav-tab-icon) {
        width: 1rem;
        height: 1rem;
    }
}
</style>
