<script>
    import { displayDate } from '$lib/stores/gameData.js'

    /**
     * @type {{ variant?: 'no-games' | 'no-scorers' | 'break' }}
     */
    let { variant = 'no-scorers' } = $props()

    const messages = {
        'no-games': {
            title: 'Ei otteluita tänään',
            text: 'NHL:ssä ei pelata otteluita päivälle',
        },
        'no-scorers': {
            title: 'Ei suomalaista pisteidentekijää',
            text: 'Yhtään suomalaispelaajaa ei ole merkitty pisteille tai dataa ei ole vielä saatavilla päivälle',
        },
        'break': {
            title: 'NHL-tauko',
            text: 'NHL:ssä on meneillään tauko. Pelit jatkuvat pian!',
        },
    }

    const currentMessage = $derived(messages[variant] || messages['no-scorers'])
</script>

<div class="empty-state-wrapper">
    <div class="empty-state-card">
        <div class="empty-state-content">
            <h3 class="empty-state-title">{currentMessage.title}</h3>
            <p class="empty-state-text">
                {currentMessage.text}
                <span class="empty-state-date">{$displayDate}</span>.
            </p>
        </div>
    </div>
</div>

<style>
    .empty-state-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 3rem 1rem;
        min-height: 300px;
    }

    .empty-state-card {
        max-width: 500px;
        width: 100%;
        background: white;
        border-radius: 12px;
        padding: 2.5rem 2rem;
        text-align: center;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }

    .empty-state-content {
        position: relative;
    }

    .empty-state-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }

    .empty-state-text {
        font-size: 0.875rem;
        color: #6b7280;
        line-height: 1.5;
        max-width: 26rem;
        margin: 0 auto;
    }

    .empty-state-date {
        font-weight: 600;
        color: #1e40af;
    }

    @media (max-width: 640px) {
        .empty-state-wrapper {
            padding: 2rem 1rem;
            min-height: 250px;
        }

        .empty-state-card {
            padding: 2rem 1.5rem;
        }

        .empty-state-title {
            font-size: 1.125rem;
        }

        .empty-state-text {
            font-size: 0.8125rem;
        }
    }
</style>
