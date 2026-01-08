<script>
    import { base } from "$app/paths";
    import { page } from "$app/stores";

    // Navigation items
    const navItems = [
        {
            href: `${base}/`,
            label: "Tulokset",
            icon: "M7.6,3,5.1,4.6l4,6.3,1.8-2.8L7.6,3m8.8,0L7.5,17H2v4H8.5L19,4.6,16.4,3M15,14.6l-1.8,2.8L15.5,21H22V17H16.5Z",
        },
        {
            href: `${base}/sarjataulukko`,
            label: "Sarjataulukko",
            icon: "M3 9L21 9M12 9V20M6.2 20H17.8C18.9201 20 19.4802 20 19.908 19.782C20.2843 19.5903 20.5903 19.2843 20.782 18.908C21 18.4802 21 17.9201 21 16.8V7.2C21 6.0799 21 5.51984 20.782 5.09202C20.5903 4.71569 20.2843 4.40973 19.908 4.21799C19.4802 4 18.9201 4 17.8 4H6.2C5.0799 4 4.51984 4 4.09202 4.21799C3.71569 4.40973 3.40973 4.71569 3.21799 5.09202C3 5.51984 3 6.07989 3 7.2V16.8C3 17.9201 3 18.4802 3.21799 18.908C3.40973 19.2843 3.71569 19.5903 4.09202 19.782C4.51984 20 5.07989 20 6.2 20Z",
        },
        {
            href: `${base}/joukkueet`,
            label: "Joukkueet",
            icon: "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M23 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75",
        },
        {
            href: `${base}/pisteporssi`,
            label: "Pistepörssi",
            icon: "M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2 M8 2h8 M9 10h6 M9 14h6 M9 18h6",
        },
    ];

    $: currentPath = $page.url.pathname;
</script>

<div class="nav-tabs-container flex md:justify-center mb-10 overflow-x-auto pr-4 py-2">
    <div
        class="nav-tabs-list inline-flex bg-slate-100/80 backdrop-blur-md p-1.5 rounded-2xl gap-1 border border-slate-200/50 shadow-inner"
        role="group"
    >
        {#each navItems as item}
            {@const isActive =
                currentPath === item.href ||
                (item.href !== `${base}/` && currentPath.startsWith(item.href))}
            <a
                href={item.href}
                class="nav-tab-item group relative inline-flex items-center rounded-xl px-6 py-2.5 text-sm font-bold transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 whitespace-nowrap
                {isActive
                    ? 'bg-white text-blue-700 shadow-[0_4px_14px_rgba(29,78,216,0.15)] ring-1 ring-blue-50 nav-tab-item--active scale-[1.02]'
                    : 'text-slate-500 hover:text-slate-900 hover:bg-white/60'}"
                aria-current={isActive ? "page" : undefined}
            >
                <svg
                    class="nav-tab-icon mr-2.5 h-5 w-5 transition-all duration-300
                    {isActive
                        ? 'text-blue-600 scale-110'
                        : 'text-slate-400 group-hover:text-slate-600 group-hover:rotate-3'}"
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
</div>
