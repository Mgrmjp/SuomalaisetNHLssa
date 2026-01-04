<script>
    import flatpickr from "flatpickr";
    import { onDestroy, onMount } from "svelte";
    import "flatpickr/dist/flatpickr.css";
    import { Finnish } from "flatpickr/dist/l10n/fi.js";
    import {
        availableDates,
        currentDateReadOnly,
        latestPrepopulatedDate,
        selectedDate,
        setDate,
        showCalendarView,
    } from "$lib/stores/gameData.js";
    import MonthView from "./MonthView.svelte";

    // availableDates is now a derived store, so we need to use $availableDates

    $: currentDateValue = $selectedDate || formatLocalDate($currentDateReadOnly);
    $: pickerValue = currentDateValue ? new Date(`${currentDateValue}T00:00:00`) : new Date();

    function _goToPreviousDay() {
        const currentDateObj = new Date(`${currentDateValue}T00:00:00`);
        const availableDateObjects = $availableDates.map((d) => new Date(`${d}T00:00:00`));

        // Find the previous available date
        const previousDates = availableDateObjects
            .filter((d) => d.getTime() < currentDateObj.getTime())
            .sort((a, b) => b.getTime() - a.getTime());

        if (previousDates.length > 0 && previousDates[0]) {
            setDate(formatLocalDate(previousDates[0]));
        }
    }

    function _goToToday() {
        const today = formatLocalDate($currentDateReadOnly);

        // Find the nearest available date (today or most recent past date with games)
        const todayDate = new Date(`${today}T00:00:00`);
        const sortedDates = $availableDates
            .map((d) => new Date(`${d}T00:00:00`))
            .sort((a, b) => b.getTime() - a.getTime());

        // Find the most recent date with games (today or earlier)
        let nearestDate = sortedDates.find((d) => d <= todayDate);

        // If no past dates found, use the earliest available date
        if (!nearestDate && sortedDates.length > 0) {
            nearestDate = sortedDates[sortedDates.length - 1];
        }

        if (nearestDate) {
            setDate(formatLocalDate(nearestDate));
        }
    }

    function _goToNextDay() {
        const currentDateObj = new Date(`${currentDateValue}T00:00:00`);
        const today = formatLocalDate($currentDateReadOnly);
        const availableDateObjects = $availableDates.map((d) => new Date(`${d}T00:00:00`));

        // Find the next available date (but not past today)
        const nextDates = availableDateObjects
            .filter((d) => d > currentDateObj && formatLocalDate(d) <= today)
            .sort((a, b) => a.getTime() - b.getTime());

        if (nextDates.length > 0 && nextDates[0]) {
            setDate(formatLocalDate(nextDates[0]));
        }
    }

    /** @param {Date | string} date */
    function formatLocalDate(date) {
        const d = typeof date === "string" ? new Date(`${date}T00:00:00`) : date;
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, "0");
        const day = String(d.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
    }

    $: todayIso = formatLocalDate(new Date());

    /** @param {string} a
     * @param {string} b */
    function minDateString(a, b) {
        const aDate = new Date(`${a}T00:00:00`);
        const bDate = new Date(`${b}T00:00:00`);
        return aDate <= bDate ? a : b;
    }

    $: maxDate = $latestPrepopulatedDate
        ? minDateString(todayIso, $latestPrepopulatedDate)
        : todayIso;

    // Check if at first or last available date
    $: isPrevDisabled = $availableDates.length > 0 && currentDateValue === $availableDates[0];
    $: isNextDisabled = $availableDates.length > 0 && currentDateValue === maxDate;

    /** @param {string} date */
    function _formatDotted(date) {
        return new Date(`${date}T00:00:00`).toLocaleDateString("fi-FI", {
            day: "numeric",
            month: "numeric",
            year: "numeric",
        });
    }

    /** @type {any} */
    let pickerInstance;
    /** @type {any} */
    let inputElement;

    onMount(() => {
        pickerInstance = flatpickr(inputElement, {
            locale: Finnish,
            dateFormat: "d.m.Y",
            defaultDate: pickerValue,
            enable: $availableDates.map((d) => new Date(`${d}T00:00:00`)),
            onChange: (selectedDates) => {
                if (selectedDates[0]) {
                    setDate(formatLocalDate(selectedDates[0]));
                }
            },
        });
    });

    onDestroy(() => {
        if (pickerInstance) pickerInstance.destroy();
    });

    // Update flatpickr when available dates change
    $: if (pickerInstance && $availableDates.length > 0) {
        pickerInstance.set(
            "enable",
            $availableDates.map((d) => new Date(`${d}T00:00:00`)),
        );
    }

    // Sync picker instance with reactive pickerValue
    $: if (pickerInstance && pickerValue) {
        pickerInstance.setDate(pickerValue, false);
    }

    function _toggleCalendar() {
        showCalendarView.update((v) => !v);
    }
</script>

<div class="date-controls w-full max-w-4xl mx-auto space-y-4">
    <div
        class="date-controls__card w-full bg-white border border-gray-200 rounded-xl shadow-lg p-4 md:p-5"
    >
        <div class="flex items-center gap-3 md:gap-4 flex-wrap">
            <button
                type="button"
                onclick={_goToPreviousDay}
                class="date-controls__nav-btn nav-btn"
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
                    <div class="date-controls__selected-info">
                        <div class="date-controls__label text-sm font-semibold text-blue-800">
                            Valittu päivämäärä
                        </div>
                        <div class="date-controls__value text-xl font-bold text-gray-900">
                            {currentDateValue ? _formatDotted(currentDateValue) : "-"}
                        </div>
                    </div>
                    <div class="date-controls__actions flex gap-2">
                        <button
                            type="button"
                            onclick={_toggleCalendar}
                            class="date-controls__toggle-btn p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 bg-gray-50 rounded-lg transition-all duration-200 border border-gray-100 flex items-center justify-center"
                            title="Näytä kalenteri"
                        >
                            <svg
                                class="w-5 h-5"
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
                            class="date-controls__today-btn px-4 py-2 text-sm font-semibold text-white rounded-lg gradient-button-primary gradient-button-primary--hover:scale cursor-pointer shadow-sm"
                        >
                            Tänään
                        </button>
                    </div>
                </div>

                <div class="date-controls__picker-wrapper relative">
                    <input
                        bind:this={inputElement}
                        id="game-date-picker"
                        type="text"
                        class="date-controls__picker-input picker-input w-full"
                        placeholder="Valitse päivämäärä"
                        readonly
                    />
                    <div
                        class="date-controls__picker-icon absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400"
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
                onclick={_goToNextDay}
                class="date-controls__nav-btn date-controls__nav-btn--next nav-btn"
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

        {#if $showCalendarView}
            <div class="mt-4 animate-in fade-in slide-in-from-top-4 duration-300">
                <MonthView />
            </div>
        {/if}
    </div>
</div>
```

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
    }

    /* flatpickr customization */
    :global(.flatpickr-calendar) {
        box-shadow:
            0 20px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
        border: 1px solid #f3f4f6 !important;
        border-radius: 16px !important;
        padding: 8px !important;
        font-family: inherit !important;
        width: fit-content !important;
        min-width: 300px !important;
    }

    /* Fix year display artifacts */
    :global(.flatpickr-current-month .numInputWrapper span.arrowUp),
    :global(.flatpickr-current-month .numInputWrapper span.arrowDown) {
        display: none !important;
    }

    :global(.flatpickr-current-month input.cur-year) {
        padding: 0 0 0 0.5ch !important;
        margin: 0 !important;
        background: transparent !important;
    }

    :global(.flatpickr-current-month input.cur-year::-webkit-inner-spin-button),
    :global(.flatpickr-current-month input.cur-year::-webkit-outer-spin-button) {
        -webkit-appearance: none !important;
        margin: 0 !important;
    }

    /* Fix arrow hover color */
    :global(.flatpickr-prev-month:hover svg),
    :global(.flatpickr-next-month:hover svg) {
        fill: #2563eb !important; /* blue-600 */
    }

    :global(.flatpickr-months) {
        padding-top: 5px !important;
        padding-bottom: 5px !important;
    }

    :global(.flatpickr-month) {
        height: 40px !important;
    }

    :global(.flatpickr-current-month) {
        font-size: 110% !important;
        font-weight: 700 !important;
    }

    :global(.flatpickr-day) {
        border-radius: 9999px !important; /* rounded-full */
        margin-top: 2px !important;
        transition: all 0.2s ease !important;
    }

    :global(.flatpickr-day.selected),
    :global(.flatpickr-day.startRange),
    :global(.flatpickr-day.endRange),
    :global(.flatpickr-day.selected.inRange),
    :global(.flatpickr-day.startRange.inRange),
    :global(.flatpickr-day.endRange.inRange),
    :global(.flatpickr-day.selected:focus),
    :global(.flatpickr-day.startRange:focus),
    :global(.flatpickr-day.endRange:focus),
    :global(.flatpickr-day.selected:hover),
    :global(.flatpickr-day.startRange:hover),
    :global(.flatpickr-day.endRange:hover),
    :global(.flatpickr-day.selected.prevMonthDay),
    :global(.flatpickr-day.startRange.prevMonthDay),
    :global(.flatpickr-day.endRange.prevMonthDay),
    :global(.flatpickr-day.selected.nextMonthDay),
    :global(.flatpickr-day.startRange.nextMonthDay),
    :global(.flatpickr-day.endRange.nextMonthDay) {
        background: #2563eb !important; /* blue-600 */
        border-color: #2563eb !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3) !important;
    }

    :global(.flatpickr-day:hover) {
        background: #f3f4f6 !important; /* gray-100 */
        transform: scale(1.05);
    }

    :global(.flatpickr-day.selected:hover) {
        transform: scale(1.05);
        background: #1d4ed8 !important; /* blue-700 */
        border-color: #1d4ed8 !important;
    }
</style>
