<div class="card card--skeleton">
    <!-- Top accent stripe -->
    <div class="card__stripe card__stripe--skeleton"></div>

    <!-- Header -->
    <div class="card__top">
        <div class="card__player-info">
            <div class="card__name-skeleton"></div>
            <div class="card__team-skeleton"></div>
        </div>
        <div class="card__badge-skeleton"></div>
    </div>

    <!-- Team row -->
    <div class="card__team-row-skeleton"></div>

    <!-- Matchup pill -->
    <div class="card__matchup-skeleton"></div>

    <!-- Primary stat ring -->
    <div class="card__stat">
        <div class="card__ring-skeleton"></div>
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
        border-radius: 20px;
        padding: 1rem;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 249, 252, 0.94));
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 8px 24px rgba(15, 23, 42, 0.06);
        min-height: 260px;
    }

    @media (max-width: 767px) {
        .card { padding: 0.85rem; border-radius: 16px; }
    }

    .card__stripe--skeleton {
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: #e5e7eb;
        z-index: 2;
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
        border-radius: 6px;
        margin-bottom: 0.35rem;
    }

    .card__team-skeleton {
        height: 10px;
        width: 40%;
        background: #e5e7eb;
        border-radius: 6px;
    }

    .card__badge-skeleton {
        width: 44px;
        height: 24px;
        background: #e5e7eb;
        border-radius: 999px;
        flex-shrink: 0;
    }

    .card__team-row-skeleton {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        margin-top: 0.35rem;
    }

    .card__team-row-skeleton::before {
        content: '';
        display: block;
        width: 28px;
        height: 28px;
        background: #f3f4f6;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .card__team-row-skeleton::after {
        content: '';
        display: block;
        height: 12px;
        width: 50%;
        background: #f3f4f6;
        border-radius: 6px;
    }

    .card__matchup-skeleton {
        height: 28px;
        border-radius: 999px;
        background: #f3f4f6;
        margin-top: 0.5rem;
    }

    .card__stat {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
    }

    .card__ring-skeleton {
        width: 80px;
        height: 80px;
        border-radius: 999px;
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
        border-radius: 4px;
    }

    .card__stat-meta-context-skeleton {
        height: 10px;
        width: 80px;
        background: #e5e7eb;
        border-radius: 4px;
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
        border-radius: 4px;
    }

    .card__sub-stat-label-skeleton {
        height: 8px;
        width: 32px;
        background: #e5e7eb;
        border-radius: 4px;
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
        border-radius: 4px;
    }

    .card__footer-btn-skeleton {
        width: 44px;
        height: 22px;
        background: #e5e7eb;
        border-radius: 6px;
    }
</style>
