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

<div class="date-controls w-full mx-auto space-y-4">
    <div
        class="date-controls__card"
    >
        <div class="date-controls__navigation-row flex items-center gap-2 md:gap-4">
            <button
                type="button"
                onclick={_goToPreviousDay}
                class="date-controls__nav-btn nav-btn flex items-center justify-center min-w-[44px] min-h-[44px]"
                disabled={isPrevDisabled}
                aria-label="Edellinen päivä"
                title="Edellinen päivä"
            >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 19l-7-7 7-7"
                    />
                </svg>
            </button>

            <div class="date-controls__main-content flex-1 flex flex-col gap-3">
                <div
                    class="date-controls__header-row flex flex-col sm:flex-row items-center justify-between gap-3"
                >
                    <div class="date-controls__selected-info text-center sm:text-left">
                        <div
                            class="date-controls__label text-xs sm:text-sm font-semibold text-blue-800"
                        >
                            Valittu päivämäärä
                        </div>
                        <div
                            class="date-controls__value text-lg sm:text-xl font-bold text-gray-900"
                        >
                            {currentDateValue ? _formatDotted(currentDateValue) : "-"}
                        </div>
                    </div>
                    <div class="date-controls__actions flex gap-2 w-full sm:w-auto">
                        <button
                            type="button"
                            onclick={_toggleCalendar}
                            class="date-controls__toggle-btn flex-1 sm:flex-initial p-2.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 bg-gray-50 rounded-lg transition-all duration-200 border border-gray-200 flex items-center justify-center min-h-[44px]"
                            title="Näytä kalenteri"
                        >
                            <svg
                                class="w-6 h-6"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
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
                            class="date-controls__today-btn flex-[2] sm:flex-initial px-6 py-2.5 text-sm font-semibold text-white rounded-lg gradient-button-primary gradient-button-primary--hover:scale cursor-pointer shadow-sm min-h-[44px]"
                        >
                            Tänään
                        </button>
                    </div>
                </div>

                <div class="date-controls__picker-wrapper relative">
                    <button
                        type="button"
                        onclick={_toggleCalendar}
                        class="date-controls__picker-input picker-input w-full py-3 text-left flex items-center"
                        aria-label="Avaa kalenteri"
                    >
                        {#if currentDateValue}
                            {_formatDotted(currentDateValue)}
                        {:else}
                            Valitse päivämäärä
                        {/if}
                    </button>
                    <div
                        class="date-controls__picker-icon absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400"
                    >
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                        </svg>
                    </div>
                </div>
            </div>

            <button
                type="button"
                onclick={_goToNextDay}
                class="date-controls__nav-btn date-controls__nav-btn--next nav-btn flex items-center justify-center min-w-[44px] min-h-[44px]"
                disabled={isNextDisabled}
                aria-label="Seuraava päivä"
                title="Seuraava päivä"
            >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <div
                class="mt-4 animate-in fade-in slide-in-from-top-4 duration-300 flex justify-center"
            >
                <MonthView />
            </div>
        {/if}
    </div>
</div>

<style>
    .date-controls__card {
        position: relative;
        overflow: visible;
        z-index: 10;
        max-width: var(--rail-max, 920px);
        margin: 0 auto;
        border-radius: var(--card-radius, 20px);
        background:
            linear-gradient(90deg, #003580, #4f7dd8, #b9cdf0) top / 100% 3px no-repeat,
            var(--card-bg, rgba(255, 255, 255, 0.9));
        background-clip: padding-box;
        background-origin: padding-box;
        border: var(--card-border, 1px solid rgba(16, 24, 40, 0.08));
        box-shadow: var(--card-shadow, 0 24px 70px rgba(16, 24, 40, 0.08));
        backdrop-filter: blur(18px);
        padding: 1rem 1.25rem;
    }

    .date-controls__label {
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .date-controls__value {
        letter-spacing: 0;
    }

    .date-controls__today-btn {
        border: 1px solid rgba(0, 53, 128, 0.18);
        background: #003580;
        color: #fff;
        box-shadow:
            0 10px 22px rgba(0, 53, 128, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.18);
    }

    .date-controls__today-btn:hover {
        background: #002b66;
        transform: translateY(-1px);
        box-shadow:
            0 14px 28px rgba(0, 53, 128, 0.24),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }

    .nav-btn {
        padding: 0.5rem;
        border-radius: 0.9rem;
        border: 1px solid rgba(16, 24, 40, 0.1);
        background: white;
        cursor: pointer;
        color: #344054;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.07);
        transition: all 0.15s ease;
    }

    .nav-btn:hover:not(:disabled) {
        background: #f6f8fc;
        transform: translateY(-1px);
    }

    .nav-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }

    :global(.picker-input) {
        width: 100%;
        padding: 0.75rem 0.9rem;
        border-radius: 0.9rem;
        border: 1px solid rgba(16, 24, 40, 0.1);
        background: rgba(248, 250, 252, 0.82);
        color: #101828;
        font-weight: 650;
        cursor: pointer;
    }

    :global(.picker-input:hover) {
        background: #ffffff;
        border-color: rgba(0, 53, 128, 0.22);
    }
</style>
