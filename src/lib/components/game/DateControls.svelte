<script>
// @ts-nocheck

import { Calendar, ChevronLeft, ChevronRight, X } from 'lucide-svelte'
import { tick } from 'svelte'
import {
    availableDates,
    currentDateReadOnly,
    latestPrepopulatedDate,
    selectedDate,
    setDate,
    showCalendarView,
} from '$lib/stores/gameData.js'
import MonthView from './MonthView.svelte'

let controlsElement = $state(null)
let pickerButton = $state(null)
let closeButton = $state(null)

// Convert reactive statements to $derived
const currentDateValue = $derived($selectedDate || formatLocalDate($currentDateReadOnly))
const todayIso = $derived(formatLocalDate($currentDateReadOnly))

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
    }
}

function _goToNextDay() {
    const currentDateObj = new Date(`${currentDateValue}T00:00:00`)
    const availableDateObjects = $availableDates.map((d) => new Date(`${d}T00:00:00`))

    // Find the next available date
    const nextDates = availableDateObjects
        .filter((d) => d.getTime() > currentDateObj.getTime() && formatLocalDate(d) <= maxDate)
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

function _closeCalendar() {
    showCalendarView.set(false)
    pickerButton?.focus()
}

async function _toggleCalendar() {
    if ($showCalendarView) {
        _closeCalendar()
        return
    }
    showCalendarView.set(true)
    await tick()
    closeButton?.focus()
}

function _dismissOutside(event) {
    if ($showCalendarView && controlsElement && !controlsElement.contains(event.target)) {
        // Keep focus on the outside control the visitor chose.
        showCalendarView.set(false)
    }
}

function _handleEscape(event) {
    if ($showCalendarView && event.key === 'Escape') {
        event.preventDefault()
        _closeCalendar()
    }
}
</script>

<svelte:window
    onpointerdown={_dismissOutside}
    onfocusin={_dismissOutside}
    onkeydown={_handleEscape}
/>

<div class="date-controls" bind:this={controlsElement}>
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
                <ChevronLeft aria-hidden="true" />
            </button>

            <button
                type="button"
                onclick={_toggleCalendar}
                bind:this={pickerButton}
                class="date-controls__picker-input picker-input"
                aria-label={$showCalendarView ? 'Sulje kalenteri' : 'Avaa kalenteri'}
                aria-expanded={$showCalendarView}
                aria-haspopup="dialog"
                aria-controls={$showCalendarView ? 'date-controls-calendar' : undefined}
            >
                <span>
                    {#if currentDateValue}
                        {_formatDotted(currentDateValue)}
                    {:else}
                        Valitse päivämäärä
                    {/if}
                </span>
                {#if $showCalendarView}
                    <X aria-hidden="true" />
                {:else}
                    <Calendar aria-hidden="true" />
                {/if}
            </button>

            <button type="button" onclick={_goToToday} class="date-controls__today-btn">
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
                <ChevronRight aria-hidden="true" />
            </button>
        </div>

        {#if $showCalendarView}
            <div
                id="date-controls-calendar"
                class="date-controls__calendar"
                role="dialog"
                aria-labelledby="date-controls-calendar-title"
            >
                <div class="date-controls__calendar-header">
                    <span id="date-controls-calendar-title">Valitse päivämäärä</span>
                    <button
                        type="button"
                        class="date-controls__close"
                        bind:this={closeButton}
                        onclick={_closeCalendar}
                        aria-label="Sulje kalenteri"
                    >
                        Sulje <X aria-hidden="true" />
                    </button>
                </div>
                <MonthView onSelect={_closeCalendar} />
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
    transition:
        background 0.15s ease,
        transform 0.15s ease;
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
    transition:
        background 0.15s ease,
        color 0.15s ease;
}

.nav-btn :global(svg) {
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
    position: absolute;
    top: calc(100% + 0.5rem);
    right: 0;
    z-index: 20;
    width: min(22.5rem, calc(100vw - 2rem));
    max-height: min(34rem, calc(100dvh - 10rem));
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: 0.5rem;
    border: var(--card-border);
    border-radius: var(--toolbar-radius, 14px);
    background: var(--card-bg);
    box-shadow: 0 12px 32px rgba(31, 83, 141, 0.22);
}

.date-controls__calendar-header {
    position: sticky;
    top: -0.5rem;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.25rem 0.25rem 0.5rem;
    background: var(--card-bg);
    color: var(--color-ink);
    font-size: 0.8rem;
    font-weight: 700;
}

.date-controls__close {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.35rem;
    min-height: 2.5rem;
    padding: 0.4rem 0.6rem;
    border: var(--card-border);
    background: var(--accent-ice);
    color: var(--accent);
    font: inherit;
    cursor: pointer;
}

.date-controls__close :global(svg) {
    width: 1rem;
    height: 1rem;
}
.date-controls__close:hover {
    background: var(--accent-tint);
}
.date-controls .date-controls__calendar :global(.calendar-month) {
    max-width: none;
    padding: 0.25rem;
    border: 0;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
}

@media (max-width: 480px) {
    .date-controls__card {
        padding: 0.75rem;
    }

    .date-controls__label {
        margin-left: 2.9rem;
        font-size: 0.64rem;
    }

    .date-controls__navigation-row {
        grid-template-columns: 2.35rem minmax(0, 1fr) auto 2.35rem;
        gap: 0.3rem;
    }

    .nav-btn {
        width: 2.35rem;
        height: 2.35rem;
    }

    :global(.picker-input),
    .date-controls__today-btn {
        min-height: 2.35rem;
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
