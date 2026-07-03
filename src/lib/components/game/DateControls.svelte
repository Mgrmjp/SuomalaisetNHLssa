<script>
// @ts-nocheck
import {
    availableDates,
    currentDateReadOnly,
    latestPrepopulatedDate,
    selectedDate,
    setDate,
    showCalendarView,
} from '$lib/stores/gameData.js'
import MonthView from './MonthView.svelte'

// Convert reactive statements to $derived
const currentDateValue = $derived($selectedDate || formatLocalDate($currentDateReadOnly))
const todayIso = formatLocalDate(new Date())

/** @param {string} a
 * @param {string} b */
function minDateString(a, b) {
    const aDate = new Date(`${a}T00:00:00`)
    const bDate = new Date(`${b}T00:00:00`)
    return aDate <= bDate ? a : b
}

const maxDate = $derived(
    $latestPrepopulatedDate ? minDateString(todayIso, $latestPrepopulatedDate) : todayIso
)

// Check if at first or last available date
const isPrevDisabled = $derived(
    $availableDates.length > 0 && currentDateValue === $availableDates[0]
)
const isNextDisabled = $derived($availableDates.length > 0 && currentDateValue === maxDate)

function _goToPreviousDay() {
    const currentDateObj = new Date(`${currentDateValue}T00:00:00`)
    const availableDateObjects = $availableDates.map((d) => new Date(`${d}T00:00:00`))

    // Find the previous available date
    const previousDates = availableDateObjects
        .filter((d) => d.getTime() < currentDateObj.getTime())
        .sort((a, b) => b.getTime() - a.getTime())

    if (previousDates.length > 0 && previousDates[0]) {
        setDate(formatLocalDate(previousDates[0]))
    }
}

function _goToToday() {
    const todayDateObj = new Date()
    const availableDateObjects = $availableDates.map((d) => new Date(`${d}T00:00:00`))

    // Find the closest available date to today (including today)
    const todayOrClosest = availableDateObjects
        .filter((d) => d.getTime() <= todayDateObj.getTime())
        .sort((a, b) => b.getTime() - a.getTime())

    if (todayOrClosest.length > 0 && todayOrClosest[0]) {
        setDate(formatLocalDate(todayOrClosest[0]))
    } else if (availableDateObjects.length > 0) {
        // If no dates are available up to today, use the latest available date
        const latestAvailable = availableDateObjects.sort((a, b) => b.getTime() - a.getTime())[0]
        setDate(formatLocalDate(latestAvailable))
    }
}

function _goToNextDay() {
    const currentDateObj = new Date(`${currentDateValue}T00:00:00`)
    const availableDateObjects = $availableDates.map((d) => new Date(`${d}T00:00:00`))

    // Find the next available date
    const nextDates = availableDateObjects
        .filter((d) => d.getTime() > currentDateObj.getTime())
        .sort((a, b) => a.getTime() - b.getTime())

    if (nextDates.length > 0 && nextDates[0]) {
        setDate(formatLocalDate(nextDates[0]))
    }
}

/** @param {Date | string} date */
function formatLocalDate(date) {
    const d = typeof date === 'string' ? new Date(`${date}T00:00:00`) : date
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
}

/** @param {string} date */
function _formatDotted(date) {
    return new Date(`${date}T00:00:00`).toLocaleDateString('fi-FI', {
        day: 'numeric',
        month: 'numeric',
        year: 'numeric',
    })
}

function _toggleCalendar() {
    showCalendarView.update((v) => !v)
}
</script>

<div class="date-controls">
    <div class="date-controls__card">
        <div class="date-controls__label">Valittu päivämäärä</div>
        <div class="date-controls__navigation-row">
            <button
                type="button"
                onclick={_goToPreviousDay}
                class="date-controls__nav-btn nav-btn"
                disabled={isPrevDisabled}
                aria-label="Edellinen päivä"
                title="Edellinen päivä"
            >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 19l-7-7 7-7"
                    />
                </svg>
            </button>

            <button
                type="button"
                onclick={_toggleCalendar}
                class="date-controls__picker-input picker-input"
                aria-label="Avaa kalenteri"
            >
                <span>
                    {#if currentDateValue}
                        {_formatDotted(currentDateValue)}
                    {:else}
                        Valitse päivämäärä
                    {/if}
                </span>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                </svg>
            </button>

            <button
                type="button"
                onclick={_goToToday}
                class="date-controls__today-btn"
            >
                Tänään
            </button>

            <button
                type="button"
                onclick={_goToNextDay}
                class="date-controls__nav-btn date-controls__nav-btn--next nav-btn"
                disabled={isNextDisabled}
                aria-label="Seuraava päivä"
                title="Seuraava päivä"
            >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 5l7 7-7 7"
                    />
                </svg>
            </button>
        </div>

        {#if $showCalendarView}
            <div class="date-controls__calendar">
                <MonthView />
            </div>
        {/if}
    </div>
</div>

<style>
    .date-controls {
        width: 100%;
        max-width: var(--rail-max, 920px);
        margin: 0 auto;
    }

    .date-controls__card {
        position: relative;
        overflow: visible;
        z-index: 10;
        border-radius: var(--card-radius, 20px);
        background: var(--card-bg, rgba(255, 255, 255, 0.94));
        border: var(--card-border, 1px solid rgba(16, 24, 40, 0.08));
        box-shadow: none;
        backdrop-filter: none;
        clip-path: none;
        padding: var(--card-padding-y, 1.25rem) var(--card-padding-x, 1.5rem);
    }

    .date-controls__card::after {
        display: none;
    }

    .date-controls__label {
        margin: 0 0 0.4rem 3.25rem;
        color: var(--eyebrow-color, #667085);
        font-size: var(--eyebrow-size, 0.68rem);
        font-weight: var(--eyebrow-weight, 700);
        letter-spacing: var(--eyebrow-track, 0.12em);
        text-transform: uppercase;
    }

    .date-controls__navigation-row {
        display: grid;
        grid-template-columns: 2.75rem minmax(0, 1fr) auto 2.75rem;
        align-items: center;
        gap: 0.5rem;
    }

    .date-controls__today-btn {
        min-height: 2.75rem;
        padding: 0.65rem 1.15rem;
        border: 1px solid rgba(16, 24, 40, 0.14);
        border-radius: 0;
        background: var(--accent);
        color: #fff;
        font-size: 0.88rem;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.15s ease, transform 0.15s ease;
    }

    .date-controls__today-btn:hover {
        background: var(--accent-strong);
        transform: translateY(-1px);
    }

    .nav-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.75rem;
        height: 2.75rem;
        padding: 0;
        border-radius: 0;
        border: 1px solid rgba(16, 24, 40, 0.1);
        background: rgba(248, 250, 252, 0.9);
        cursor: pointer;
        color: #344054;
        box-shadow: none;
        transition: background 0.15s ease, color 0.15s ease;
    }

    .nav-btn svg {
        width: 1.2rem;
        height: 1.2rem;
    }

    .nav-btn:hover:not(:disabled) {
        background: #ffffff;
        color: var(--accent);
    }

    .nav-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }

    :global(.picker-input) {
        width: 100%;
        min-height: 2.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.65rem 0.85rem;
        border-radius: 0;
        border: 1px solid rgba(16, 24, 40, 0.1);
        background: rgba(248, 250, 252, 0.82);
        color: #101828;
        font-size: 0.95rem;
        font-weight: 700;
        text-align: left;
        cursor: pointer;
    }

    :global(.picker-input svg) {
        width: 1.2rem;
        height: 1.2rem;
        flex: 0 0 auto;
        color: #98a2b3;
    }

    :global(.picker-input:hover) {
        background: #ffffff;
        border-color: rgba(16, 24, 40, 0.18);
    }

    .date-controls__calendar {
        display: flex;
        justify-content: center;
        margin-top: 1rem;
    }

    @media (max-width: 480px) {
        .date-controls__card {
            padding: 1rem;
        }

        .date-controls__label {
            margin-left: 2.9rem;
            font-size: 0.64rem;
        }

        .date-controls__navigation-row {
            grid-template-columns: 2.5rem minmax(0, 1fr) auto 2.5rem;
            gap: 0.375rem;
        }

        .nav-btn {
            width: 2.5rem;
            height: 2.5rem;
        }

        :global(.picker-input),
        .date-controls__today-btn {
            min-height: 2.5rem;
        }

        :global(.picker-input) {
            padding-inline: 0.7rem;
            font-size: 0.88rem;
        }

        .date-controls__today-btn {
            padding-inline: 0.75rem;
            font-size: 0.8rem;
        }
    }
</style>
