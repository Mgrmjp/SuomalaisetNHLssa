<script>
    import { onMount } from "svelte";
    import { fetchLocalJSON } from "$lib/utils/apiHelpers.js";

    // Available game dates
    const gameDates = [
        "2025-09-30",
        "2025-10-01",
        "2025-10-02",
        "2025-10-03",
        "2025-10-04",
        "2025-10-05",
        "2025-10-06",
        "2025-10-07",
        "2025-10-08",
        "2025-10-09",
        "2025-10-10",
        "2025-10-11",
        "2025-10-12",
        "2025-10-13",
        "2025-10-14",
        "2025-10-15",
        "2025-10-16",
        "2025-10-17",
        "2025-10-18",
        "2025-10-19",
        "2025-10-20",
        "2025-10-21",
        "2025-10-22",
        "2025-10-23",
        "2025-10-24",
        "2025-10-25",
        "2025-10-26",
        "2025-10-27",
        "2025-10-28",
        "2025-10-29",
        "2025-10-30",
        "2025-10-31",
        "2025-11-01",
        "2025-11-02",
        "2025-11-03",
        "2025-11-04",
        "2025-11-05",
        "2025-11-06",
        "2025-11-07",
        "2025-11-08",
        "2025-11-09",
        "2025-11-10",
        "2025-11-11",
        "2025-11-12",
        "2025-11-13",
        "2025-11-14",
        "2025-11-15",
        "2025-11-16",
        "2025-11-17",
        "2025-11-18",
        "2025-11-19",
        "2025-11-20",
        "2025-11-21",
        "2025-11-22",
        "2025-11-23",
        "2025-11-24",
        "2025-11-25",
        "2025-11-26",
        "2025-11-27",
        "2025-11-28",
        "2025-11-29",
        "2025-11-30",
        "2025-12-01",
        "2025-12-02",
        "2025-12-03",
        "2025-12-04",
        "2025-12-05",
        "2025-12-06",
        "2025-12-07",
        "2025-12-08",
        "2025-12-09",
        "2025-12-10",
        "2025-12-11",
        "2025-12-12",
        "2025-12-13",
        "2025-12-14",
        "2025-12-15",
        "2025-12-16",
        "2025-12-17",
        "2025-12-18",
        "2025-12-19",
        "2025-12-20",
        "2025-12-21",
        "2025-12-22",
        "2025-12-23",
        "2025-12-24",
        "2025-12-25",
        "2025-12-26",
        "2025-12-27",
        "2025-12-28",
        "2025-12-29",
        "2025-12-30",
        "2025-12-31",
        "2026-01-01",
        "2026-01-02",
        "2026-01-03",
        "2026-01-04",
        "2026-01-05",
        "2026-01-06",
    ];

    let _patternEntries = [];

    const weightSteps = [500, 600, 700, 800];

    function hashString(input) {
        let hash = 0;
        for (let i = 0; i < input.length; i++) {
            hash = (hash << 5) - hash + input.charCodeAt(i);
            hash |= 0;
        }
        return hash;
    }

    onMount(async () => {
        const nameSet = new Set();

        // Load a sample of game files to extract player names (limit to avoid too many requests)
        const sampleDates = gameDates.filter((_, i) => i % 5 === 0); // Every 5th date

        for (const date of sampleDates) {
            try {
                const data = await fetchLocalJSON(`/data/prepopulated/games/${date}.json`);
                if (data?.players) {
                    data.players.forEach((p) => {
                        if (p?.name) {
                            nameSet.add(p.name);
                        }
                    });
                }
            } catch (_e) {
                // Skip errors, just continue with other dates
            }
        }

        const playerNames = Array.from(nameSet).slice(0, 120);

        // Build lightweight entries with deterministic weight per name
        _patternEntries = [...playerNames, ...playerNames].map((name, idx) => {
            const weight = weightSteps[Math.abs(hashString(name)) % weightSteps.length];
            return {
                name,
                offset: (idx % 3) * 6,
                rotation: -6,
                weight,
            };
        });
    });
</script>

<div class="player-pattern" aria-hidden="true">
    {#each patternEntries as entry}
        <span
            class="player-pattern__name"
            style={`--pat-offset:${entry.offset}px;--pat-rot:${entry.rotation}deg;--pat-weight:${entry.weight};`}
        >
            {entry.name}
        </span>
    {/each}
</div>

<style>
    .player-pattern {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.08;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 28px 24px;
        padding: 48px 32px;
        background: radial-gradient(circle at 10% 10%, rgba(255, 255, 255, 0.4), transparent 35%),
            radial-gradient(circle at 90% 30%, rgba(255, 255, 255, 0.25), transparent 30%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.06), rgba(15, 23, 42, 0.12));
    }

    .player-pattern__name {
        font-size: 0.85rem;
        font-weight: var(--pat-weight, 700);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #0f172a;
        mix-blend-mode: multiply;
        transform: translateY(var(--pat-offset)) rotate(var(--pat-rot, -6deg));
    }

    @media (max-width: 640px) {
        .player-pattern {
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 16px;
            padding: 28px 16px;
        }

        .player-pattern__name {
            font-size: 0.75rem;
            letter-spacing: 0.06em;
            transform: translateY(calc(var(--pat-offset) * 0.66))
                rotate(calc(var(--pat-rot, -6deg) * 0.66));
        }
    }
</style>
