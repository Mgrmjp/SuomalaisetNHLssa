<script>
const { compact = false } = $props()
</script>

<div
    class="skeleton-card card--skeleton ui-surface"
    class:skeleton-card--compact={compact}
    aria-hidden="true"
>
    <div class="skeleton-card__header">
        <div class="skeleton-card__identity">
            <div class="skeleton-card__block skeleton-card__name"></div>
            <div class="skeleton-card__block skeleton-card__details"></div>
        </div>
        <div class="skeleton-card__block skeleton-card__logo"></div>
    </div>
    <div class="skeleton-card__block skeleton-card__venue"></div>
    <div class="skeleton-card__stats">
        {#each [1, 2, 3, 4] as _}
            <div class="skeleton-card__stat">
                <div class="skeleton-card__block skeleton-card__value"></div>
                <div class="skeleton-card__block skeleton-card__label"></div>
            </div>
        {/each}
    </div>
    <div class="skeleton-card__block skeleton-card__switch"></div>
    <div class="skeleton-card__matchup">
        <div class="skeleton-card__block skeleton-card__team"></div>
        <div class="skeleton-card__block skeleton-card__score"></div>
        <div class="skeleton-card__block skeleton-card__team"></div>
    </div>
    <div class="skeleton-card__block skeleton-card__result"></div>
</div>

<style>
.skeleton-card {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-width: 0;
    min-height: 258px;
    overflow: hidden;
    padding: 1rem;
    border: var(--card-border);
    border-radius: var(--card-radius);
    background: var(--card-bg);
    box-shadow: var(--card-shadow);
}

.skeleton-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
        100deg,
        transparent 25%,
        rgba(255, 255, 255, 0.6) 50%,
        transparent 75%
    );
    transform: translateX(-100%);
    animation: skeleton-shimmer 1.8s ease-in-out infinite;
    pointer-events: none;
}

.skeleton-card__block {
    flex-shrink: 0;
    border-radius: 4px;
    background: #dbe7f5;
}

.skeleton-card__header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
}

.skeleton-card__identity {
    flex: 1;
    min-width: 0;
}

.skeleton-card__name {
    width: 80%;
    height: 16px;
    margin-bottom: 0.5rem;
}

.skeleton-card__details {
    width: 45%;
    height: 10px;
}

.skeleton-card__logo {
    width: 36px;
    height: 36px;
    border-radius: 50%;
}

.skeleton-card__venue {
    width: 65%;
    height: 10px;
}

.skeleton-card__stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.5rem;
}

.skeleton-card__stat {
    display: grid;
    justify-items: center;
    gap: 0.5rem;
}

.skeleton-card__value {
    width: 20px;
    height: 16px;
}

.skeleton-card__label {
    width: 32px;
    height: 8px;
}

.skeleton-card__switch {
    align-self: center;
    width: 40%;
    height: 10px;
    margin-top: auto;
}

.skeleton-card__matchup {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(116, 151, 190, 0.2);
}

.skeleton-card__team {
    width: 24px;
    height: 24px;
    border-radius: 50%;
}

.skeleton-card__score {
    width: 36px;
    height: 14px;
}

.skeleton-card__result {
    align-self: center;
    width: 44px;
    height: 8px;
}

.skeleton-card--compact {
    display: grid;
    grid-template-columns: minmax(0, 1.4fr) minmax(0, 0.8fr) minmax(0, 1fr) 2.5rem;
    grid-template-areas: 'identity stats game action';
    align-items: center;
    min-height: 80px;
    gap: 0.5rem 1rem;
    padding: 0.75rem;
    border-radius: var(--card-radius-sm);
}

.skeleton-card--compact .skeleton-card__header {
    grid-area: identity;
}
.skeleton-card--compact .skeleton-card__stats {
    grid-area: stats;
    gap: 0.25rem;
}
.skeleton-card--compact .skeleton-card__label {
    width: 14px;
    height: 6px;
}
.skeleton-card--compact .skeleton-card__matchup {
    grid-area: game;
    border: 0;
    padding: 0;
}
.skeleton-card--compact .skeleton-card__switch {
    grid-area: action;
    width: 24px;
    margin: 0;
}
.skeleton-card--compact .skeleton-card__venue,
.skeleton-card--compact .skeleton-card__result {
    display: none;
}
.skeleton-card--compact .skeleton-card__header {
    flex-direction: row-reverse;
    gap: 0.5rem;
}
.skeleton-card--compact .skeleton-card__logo {
    width: 28px;
    height: 28px;
}

@media (max-width: 767px) {
    .skeleton-card--compact {
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 2.5rem;
        grid-template-areas: 'identity identity action' 'stats game game';
        min-height: 112px;
        gap: 0.5rem;
    }
}

@keyframes skeleton-shimmer {
    to {
        transform: translateX(100%);
    }
}

@media (prefers-reduced-motion: reduce) {
    .skeleton-card::after {
        animation: none;
    }
}
</style>
