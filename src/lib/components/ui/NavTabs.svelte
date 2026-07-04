<script>
// @ts-nocheck

import {
    Users as JoukkueetIcon,
    Sparkles as LupauksetIcon,
    ClipboardList as PisteporssiIcon,
    BarChart3 as SarjataulukkoIcon,
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
        justify-content: stretch;
        width: 100%;
        min-width: 0;
        max-width: 100%;
        overflow: hidden;
        padding: 0;
        margin: 0;
    }

    .nav-tabs-list {
        display: flex;
        width: 100%;
        min-width: 0;
        max-width: 100%;
        gap: 0.2rem;
        padding: 0.25rem;
        border: var(--card-border);
        border-radius: 0;
        background: rgba(255, 255, 255, 0.76);
        overflow-x: auto;
        scrollbar-width: none;
    }

    .nav-tabs-list::-webkit-scrollbar {
        display: none;
    }

    .nav-tab-item {
        position: relative;
        display: inline-flex;
        flex: 1 0 auto;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        min-height: 2.4rem;
        padding: 0.5rem 0.9rem;
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

    .nav-tab-icon {
        width: 1.05rem;
        height: 1.05rem;
        color: #98a2b3;
        transition:
            color 0.16s ease,
            transform 0.16s ease;
    }

    .nav-tab-item:hover .nav-tab-icon {
        color: var(--accent);
    }

    .nav-tab-item--active .nav-tab-icon {
        color: #ffffff;
        transform: scale(1.04);
    }

    @media (min-width: 768px) {
        .nav-tab-item {
            padding-inline: 1rem;
        }
    }

    @media (max-width: 767px) {
        .nav-tabs-container {
            overflow: visible;
        }

        .nav-tabs-list {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.25rem;
            padding: 0.25rem;
            overflow: visible;
        }

        .nav-tab-item {
            flex: none;
            min-width: 0;
            gap: 0.25rem;
            min-height: 2.25rem;
            padding: 0.35rem 0.25rem;
            font-size: 0.72rem;
            line-height: 1.05;
            white-space: normal;
        }

        .nav-tab-icon {
            width: 0.82rem;
            height: 0.82rem;
            flex: 0 0 auto;
        }
    }

    @media (max-width: 360px) {
        .nav-tabs-list {
            gap: 0.2rem;
        }

        .nav-tab-item {
            font-size: 0.68rem;
        }
    }
</style>
