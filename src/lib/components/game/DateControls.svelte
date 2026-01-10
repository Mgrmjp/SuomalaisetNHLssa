<script>
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

    function _toggleCalendar() {
        showCalendarView.update((v) => !v);
    }
</script>

<div class="date-controls w-full max-w-4xl mx-auto space-y-4">
    <div
        class="date-controls__card w-full bg-white border border-gray-200 rounded-xl shadow-lg p-4 md:p-5"
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
                            class="date-controls__toggle-btn flex-1 sm:flex-initial p-2.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 bg-gray-50 rounded-lg transition-all duration-200 border border-gray-100 flex items-center justify-center min-h-[44px]"
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
</style>
