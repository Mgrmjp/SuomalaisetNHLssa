<script>
import flatpickr from 'flatpickr'
import { onDestroy, onMount } from 'svelte'
import 'flatpickr/dist/flatpickr.css'
import { Finnish } from 'flatpickr/dist/l10n/fi.js'
import {
    availableDates,
    currentDateReadOnly,
    earliestPrepopulatedDate,
    latestPrepopulatedDate,
    selectedDate,
    setDate
} from '$lib/stores/gameData.js'

// availableDates is now a derived store, so we need to use $availableDates
import { getRelativeFinnishDate } from '$lib/utils/dateUtils.js'

$: currentDateValue = $selectedDate || formatLocalDate($currentDateReadOnly)
$: pickerValue = currentDateValue ? new Date(`${currentDateValue}T00:00:00`) : new Date()

function _goToPreviousDay() {
    const currentDateObj = new Date(`${currentDateValue}T00:00:00`)
    const availableDateObjects = $availableDates.map((d) => new Date(`${d}T00:00:00`))

    // Find the previous available date
    const previousDates = availableDateObjects.filter((d) => d < currentDateObj).sort((a, b) => b - a)

    if (previousDates.length > 0) {
        setDate(formatLocalDate(previousDates[0]))
    }
}

function _goToToday() {
    const today = formatLocalDate($currentDateReadOnly)

    // Find the nearest available date (today or most recent past date with games)
    const todayDate = new Date(`${today}T00:00:00`)
    const sortedDates = $availableDates.map((d) => new Date(`${d}T00:00:00`)).sort((a, b) => b - a)

    // Find the most recent date with games (today or earlier)
    let nearestDate = sortedDates.find((d) => d <= todayDate)

    // If no past dates found, use the earliest available date
    if (!nearestDate && sortedDates.length > 0) {
        nearestDate = sortedDates[sortedDates.length - 1]
    }

    if (nearestDate) {
        setDate(formatLocalDate(nearestDate))
    }
}

function _goToNextDay() {
    const currentDateObj = new Date(`${currentDateValue}T00:00:00`)
    const today = formatLocalDate($currentDateReadOnly)
    const availableDateObjects = $availableDates.map((d) => new Date(`${d}T00:00:00`))

    // Find the next available date (but not past today)
    const nextDates = availableDateObjects.filter((d) => d > currentDateObj && formatLocalDate(d) <= today).sort((a, b) => a - b)

    if (nextDates.length > 0) {
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

$: todayIso = formatLocalDate(new Date())

function minDateString(a, b) {
    const aDate = new Date(`${a}T00:00:00`)
    const bDate = new Date(`${b}T00:00:00`)
    return aDate <= bDate ? a : b
}

$: maxDate = $latestPrepopulatedDate ? minDateString(todayIso, $latestPrepopulatedDate) : todayIso
$: minDate = $earliestPrepopulatedDate || '2020-10-01'

// Check if at first or last available date
$: isPrevDisabled = $availableDates.length > 0 && currentDateValue === $availableDates[0]
$: isNextDisabled = $availableDates.length > 0 && currentDateValue === maxDate
$: relativeLabel = getRelativeFinnishDate(currentDateValue, new Date(`${maxDate}T00:00:00`))

/** @param {string} date */
function _formatDotted(date) {
    return new Date(`${date}T00:00:00`).toLocaleDateString('fi-FI', {
        day: 'numeric',
        month: 'numeric',
        year: 'numeric',
    })
}

/** @type {any} */
let pickerInstance
/** @type {any} */
let inputElement

onMount(() => {
    pickerInstance = flatpickr(inputElement, {
        locale: Finnish,
        dateFormat: 'd.m.Y',
        defaultDate: pickerValue,
        enable: $availableDates.map((d) => new Date(`${d}T00:00:00`)),
        onChange: (selectedDates) => {
            if (selectedDates[0]) {
                setDate(formatLocalDate(selectedDates[0]))
            }
        },
    })
})

onDestroy(() => {
    if (pickerInstance) pickerInstance.destroy()
})

// Update flatpickr when available dates change
$: if (pickerInstance && $availableDates.length > 0) {
    pickerInstance.set('enable', $availableDates.map((d) => new Date(`${d}T00:00:00`)))
}

// Sync picker instance with reactive pickerValue
$: if (pickerInstance && pickerValue) {
    pickerInstance.setDate(pickerValue, false)
}
</script>

<div class="date-controls w-full max-w-3xl mx-auto space-y-4">
    <div
        class="date-controls__card w-full bg-white border border-gray-200 rounded-xl shadow-lg p-4 md:p-5"
    >
        <div class="flex items-center gap-3 md:gap-4 flex-wrap">
            <button
                type="button"
                on:click={_goToPreviousDay}
                class="nav-btn"
                disabled={isPrevDisabled}
                aria-label="Edellinen päivä"
                title="Edellinen päivä"
            >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 19l-7-7 7-7"
                    />
                </svg>
            </button>

            <div class="flex-1 flex flex-col gap-3">
                <div class="flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <div class="text-sm font-semibold text-blue-800">Valittu päivämäärä</div>
                        <div class="text-xl font-bold text-gray-900">
                            {_formatDotted(currentDateValue)}
                        </div>
                    </div>
                    <button
                        type="button"
                        on:click={_goToToday}
                        class="px-4 py-2 text-sm font-semibold text-white rounded-lg gradient-button-primary gradient-button-primary--hover:scale cursor-pointer shadow-sm"
                    >
                        Tänään
                    </button>
                </div>

                <div class="relative">
                    <input
                        bind:this={inputElement}
                        id="game-date-picker"
                        type="text"
                        class="picker-input w-full"
                        placeholder="Valitse päivämäärä"
                        readonly
                    />
                    <div
                        class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400"
                    >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                on:click={_goToNextDay}
                class="nav-btn"
                disabled={isNextDisabled}
                aria-label="Seuraava päivä"
                title="Seuraava päivä"
            >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 5l7 7-7 7"
                    />
                </svg>
            </button>
        </div>
    </div>
</div>

<style>
    .date-controls__card {
        position: relative;
        overflow: visible;
        z-index: 10;
        background: linear-gradient(140deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 252, 0.95));
        border: 1px solid #e2e8f0;
        box-shadow:
            0 10px 22px rgba(15, 23, 42, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.75);
    }

    .nav-btn {
        padding: 0.5rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        background: white;
        cursor: pointer;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
        transition: all 0.15s ease;
    }

    .nav-btn:hover:not(:disabled) {
        background: #f8fafc;
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
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        background: #fff;
        cursor: pointer;
        font-weight: 600;
        color: #0f172a;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }

    /* flatpickr customization */
    :global(.flatpickr-calendar) {
        box-shadow:
            0 10px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 5px;
    }

    :global(.flatpickr-day.selected) {
        background: #2563eb !important;
        border-color: #2563eb !important;
    }

    :global(.flatpickr-day:hover) {
        background: #f1f5f9 !important;
    }
</style>
