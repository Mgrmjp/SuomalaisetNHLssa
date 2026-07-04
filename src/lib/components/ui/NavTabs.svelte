<script>
// @ts-nocheck
import { base } from '$app/paths'
import { page } from '$app/stores'

// Navigation items
const _navItems = [
    {
        href: `${base}/`,
        label: 'Tulokset',
        icon: 'M7.6,3,5.1,4.6l4,6.3,1.8-2.8L7.6,3m8.8,0L7.5,17H2v4H8.5L19,4.6,16.4,3M15,14.6l-1.8,2.8L15.5,21H22V17H16.5Z',
    },
    {
        href: `${base}/sarjataulukko`,
        label: 'Sarjataulukko',
        icon: 'M3 9L21 9M12 9V20M6.2 20H17.8C18.9201 20 19.4802 20 19.908 19.782C20.2843 19.5903 20.5903 19.2843 20.782 18.908C21 18.4802 21 17.9201 21 16.8V7.2C21 6.0799 21 5.51984 20.782 5.09202C20.5903 4.71569 20.2843 4.40973 19.908 4.21799C19.4802 4 18.9201 4 17.8 4H6.2C5.0799 4 4.51984 4 4.09202 4.21799C3.71569 4.40973 3.40973 4.71569 3.21799 5.09202C3 5.51984 3 6.07989 3 7.2V16.8C3 17.9201 3 18.4802 3.21799 18.908C3.40973 19.2843 3.71569 19.5903 4.09202 19.782C4.51984 20 5.07989 20 6.2 20Z',
    },
    {
        href: `${base}/joukkueet`,
        label: 'Joukkueet',
        icon: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M23 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75',
    },
    {
        href: `${base}/pisteporssi`,
        label: 'Pistepörssi',
        icon: 'M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2 M8 2h8 M9 10h6 M9 14h6 M9 18h6',
    },
    {
        href: `${base}/lupaukset`,
        label: 'Lupaukset',
        icon: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z',
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
                <svg
                    class="nav-tab-icon"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    {#if item.label === "Tulokset"}
                        <!-- Custom path for Tulokset icon which is filled -->
                        <path fill="currentColor" stroke="none" d={item.icon} />
                    {:else}
                        {#each item.icon.split(" M") as d, i}
                            <path d={i > 0 ? "M" + d : d} />
                        {/each}
                    {/if}
                </svg>
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
