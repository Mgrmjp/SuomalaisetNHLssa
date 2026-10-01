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
    },
]

const currentPath = $derived($page.url.pathname)
</script>

<nav class="nav-tabs-container" aria-label="Päänavigaatio">
    <div class="nav-tabs-list" role="group">
        {#each _navItems as item}
            {@const isActive =
                currentPath === item.href ||
                (item.href !== `${base}/` && currentPath.startsWith(item.href))}
            <a
                href={item.href}
                class="nav-tab-item group"
                class:nav-tab-item--active={isActive}
                aria-current={isActive ? "page" : undefined}
            >
                <item.Icon class="nav-tab-icon" aria-hidden="true" />
                {item.label}
            </a>
        {/each}
    </div>
</nav>

<style>
    .nav-tabs-container {
        display: flex;
        justify-content: center;
        width: fit-content;
        min-width: 0;
        max-width: 100%;
        margin: 0 auto;
        padding: 0;
    }

    .nav-tabs-list {
        display: flex;
        min-width: 0;
        max-width: 100%;
        gap: 0.2rem;
        padding: 0.25rem;
        border: var(--card-border);
        border-radius: 0;
        background: rgba(255, 255, 255, 0.76);
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    }

    .nav-tabs-list::-webkit-scrollbar {
        display: none;
    }

    .nav-tab-item {
        position: relative;
        display: inline-flex;
        flex: 0 0 auto;
        align-items: center;
        justify-content: center;
        gap: 0.4rem;
        min-height: 2.4rem;
        padding: 0.5rem 0.75rem;
        border-radius: 0;
        color: #475467;
        font-size: 0.88rem;
        font-weight: 700;
        line-height: 1;
        text-decoration: none;
        white-space: nowrap;
        transition:
            background 0.16s ease,
            color 0.16s ease,
            transform 0.16s ease;
    }

    .nav-tab-item:hover {
        color: var(--color-ink);
        background: rgba(16, 24, 40, 0.04);
    }

    .nav-tab-item:focus-visible {
        outline: 3px solid rgba(16, 24, 40, 0.18);
        outline-offset: 2px;
    }

    .nav-tab-item--active {
        background: var(--accent);
        color: #ffffff;
    }

    .nav-tab-item :global(.nav-tab-icon) {
        width: 1.05rem;
        height: 1.05rem;
        color: #98a2b3;
        transition:
            color 0.16s ease,
            transform 0.16s ease;
    }

    .nav-tab-item:hover :global(.nav-tab-icon) {
        color: var(--accent);
    }

    .nav-tab-item--active :global(.nav-tab-icon) {
        color: #ffffff;
        transform: scale(1.04);
    }

    @media (min-width: 768px) {
        .nav-tab-item {
            padding-inline: 0.85rem;
        }
    }

    @media (max-width: 767px) {
        .nav-tabs-container {
            max-width: 100%;
        }

        .nav-tab-item {
            gap: 0.3rem;
            min-height: 2.25rem;
            padding: 0.35rem 0.55rem;
            font-size: 0.75rem;
        }

        .nav-tab-item :global(.nav-tab-icon) {
            width: 0.82rem;
            height: 0.82rem;
            flex: 0 0 auto;
        }
    }

    @media (max-width: 360px) {
        .nav-tab-item {
            gap: 0.25rem;
            padding: 0.35rem 0.45rem;
            font-size: 0.7rem;
        }
    }
</style>
