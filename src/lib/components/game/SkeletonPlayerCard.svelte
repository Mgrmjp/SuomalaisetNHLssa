<div class="card ui-surface card--skeleton">
    <!-- Header -->
    <div class="card__top">
        <div class="card__player-info">
            <div class="card__name-skeleton"></div>
            <div class="card__team-skeleton"></div>
        </div>
        <div class="card__badge-skeleton"></div>
    </div>

    <!-- Matchup pill -->
    <div class="card__matchup-skeleton"></div>

    <!-- Primary stat ring -->
    <div class="card__stat">
        <div class="card__value-skeleton"></div>
        <div class="card__stat-meta-skeleton">
            <div class="card__stat-meta-label-skeleton"></div>
            <div class="card__stat-meta-context-skeleton"></div>
        </div>
    </div>

    <!-- Sub stats -->
    <div class="card__sub-stats-skeleton">
        <div class="card__sub-stat-skeleton">
            <div class="card__sub-stat-value-skeleton"></div>
            <div class="card__sub-stat-label-skeleton"></div>
        </div>
        <div class="card__sub-stat-skeleton">
            <div class="card__sub-stat-value-skeleton"></div>
            <div class="card__sub-stat-label-skeleton"></div>
        </div>
    </div>

    <!-- Footer -->
    <div class="card__footer">
        <div class="card__footer-hint-skeleton"></div>
        <div class="card__footer-btn-skeleton"></div>
    </div>
</div>

<style>
    .card {
        position: relative;
        overflow: hidden;
        border-radius: var(--card-radius-sm);
        padding: 1rem;
        background: var(--card-bg);
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: var(--card-shadow);
        min-height: 260px;
        border-radius: var(--card-radius);
    }

    @media (max-width: 767px) {
        .card { padding: 0.85rem; border-radius: var(--card-radius); }
    }


    .card__top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.5rem;
    }

    .card__name-skeleton {
        height: 16px;
        width: 70%;
        background: #e5e7eb;
        border-radius: var(--card-radius-sm);
        margin-bottom: 0.35rem;
    }

    .card__team-skeleton {
        height: 10px;
        width: 40%;
        background: #e5e7eb;
        border-radius: var(--card-radius-sm);
    }

    .card__badge-skeleton {
        width: 44px;
        height: 24px;
        background: #e5e7eb;
        border-radius: var(--card-radius-sm);
        flex-shrink: 0;
    }

    .card__matchup-skeleton {
        height: 28px;
        border-radius: var(--card-radius-sm);
        background: #f3f4f6;
        margin-top: 0.5rem;
    }

    .card__stat {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
    }

    .card__value-skeleton {
        width: 72px;
        height: 28px;
        border-radius: var(--card-radius-sm);
        background: #f3f4f6;
        flex-shrink: 0;
    }

    .card__stat-meta-skeleton {
        display: grid;
        gap: 0.25rem;
    }

    .card__stat-meta-label-skeleton {
        height: 10px;
        width: 60px;
        background: #e5e7eb;
        border-radius: var(--card-radius-sm);
    }

    .card__stat-meta-context-skeleton {
        height: 10px;
        width: 80px;
        background: #e5e7eb;
        border-radius: var(--card-radius-sm);
    }

    .card__sub-stats-skeleton {
        display: flex;
        justify-content: center;
        gap: 1rem;
        padding: 0.5rem 0;
        border-top: 1px solid rgba(229, 231, 235, 0.5);
    }

    .card__sub-stat-skeleton {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.2rem;
    }

    .card__sub-stat-value-skeleton {
        height: 14px;
        width: 18px;
        background: #e5e7eb;
        border-radius: var(--card-radius-sm);
    }

    .card__sub-stat-label-skeleton {
        height: 8px;
        width: 32px;
        background: #e5e7eb;
        border-radius: var(--card-radius-sm);
    }

    .card__footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 0.25rem;
    }

    .card__footer-hint-skeleton {
        height: 8px;
        width: 80px;
        background: #f3f4f6;
        border-radius: var(--card-radius-sm);
    }

    .card__footer-btn-skeleton {
        width: 44px;
        height: 22px;
        background: #e5e7eb;
        border-radius: var(--card-radius-sm);
    }
</style>
