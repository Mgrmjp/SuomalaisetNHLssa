<script>
    // biome-ignore lint/correctness/noUnusedImports: used in template
    import {
        formatDate,
        setDate,
        showCalendarView,
        selectedDate,
        currentDateReadOnly,
        availableDates,
    } from "$lib/stores/gameData.js";

    // Generate calendar days for the current selected date's month
    $: calendarDays = generateCalendarDays($selectedDate || formatDate($currentDateReadOnly));
    $: currentMonth = $selectedDate ? new Date(`${$selectedDate}T00:00:00`) : $currentDateReadOnly;

    // Get the month and year display string
    function _getMonthYearDisplay() {
        return currentMonth.toLocaleDateString("fi-FI", {
            month: "long",
            year: "numeric",
        });
    }

    // Navigate between months
    /** @param {'prev' | 'next'} direction */
    function _navigateMonth(direction) {
        const newMonth = new Date(currentMonth);
        if (direction === "prev") {
            newMonth.setMonth(newMonth.getMonth() - 1);
        } else {
            newMonth.setMonth(newMonth.getMonth() + 1);
            // Don't go beyond current date
            if (newMonth > $currentDateReadOnly) return;
        }

        // Keep the same day of month if possible, otherwise go to last day of month
        const originalDay = currentMonth.getDate();
        const daysInNewMonth = new Date(
            newMonth.getFullYear(),
            newMonth.getMonth() + 1,
            0,
        ).getDate();
        newMonth.setDate(Math.min(originalDay, daysInNewMonth));

        // Update the selected date
        setDate(formatDate(newMonth));
    }

    // Select a specific date
    /** @param {string} dateStr */
    function _selectDate(dateStr) {
        setDate(dateStr);
        showCalendarView.set(false);
    }

    /** @param {string} selectedDateStr */
    function generateCalendarDays(selectedDateStr) {
        const date = new Date(`${selectedDateStr}T00:00:00`);
        const year = date.getFullYear();
        const month = date.getMonth();

        // First day of month
        const firstDay = new Date(year, month, 1);
        // Last day of month
        const lastDay = new Date(year, month + 1, 0);

        // Start from Monday of the first week
        const startDate = new Date(firstDay);
        const dayOfWeek = firstDay.getDay(); // 0-6 (Sun-Sat)
        const diff = (dayOfWeek + 6) % 7; // distance from Monday (0=Mon, 6=Sun)
        startDate.setDate(startDate.getDate() - diff);

        // End on Sunday of the last week
        const endDate = new Date(lastDay);
        const endDayOfWeek = lastDay.getDay();
        const endDiff = (7 - endDayOfWeek) % 7; // distance to Sunday
        endDate.setDate(endDate.getDate() + endDiff);

        const days = [];
        const current = new Date(startDate);

        while (current <= endDate) {
            const dateStr = formatDate(current);
            const hasData = $availableDates.includes(dateStr);

            days.push({
                date: new Date(current),
                dateStr,
                isCurrentMonth: current.getMonth() === month,
                isToday: formatDate(current) === formatDate($currentDateReadOnly),
                isSelected: formatDate(current) === selectedDateStr,
                hasData: hasData,
                isFuture: current > $currentDateReadOnly,
            });
            current.setDate(current.getDate() + 1);
        }

        return days;
    }
</script>

<div class="calendar-month bg-white rounded-2xl shadow-xl p-3 sm:p-4 border border-gray-100">
    <div class="calendar-month__header flex items-center justify-between mb-4">
        <button
            class="calendar-month__nav-btn calendar-month__nav-btn--prev w-8 h-8 flex items-center justify-center rounded-full bg-blue-50 text-blue-600 hover:bg-blue-100 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 active:scale-95"
            onclick={() => _navigateMonth("prev")}
            disabled={currentMonth.getMonth() === $currentDateReadOnly.getMonth() &&
                currentMonth.getFullYear() === $currentDateReadOnly.getFullYear()}
            data-dashlane-label="true"
            aria-label="Edellinen kuukausi"
        >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                ><path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2.5"
                    d="M15 19l-7-7 7-7"
                /></svg
            >
        </button>
        <h2 class="calendar-month__title text-lg font-bold text-gray-900 tracking-tight">
            {_getMonthYearDisplay()}
        </h2>
        <button
            class="calendar-month__nav-btn calendar-month__nav-btn--next w-8 h-8 flex items-center justify-center rounded-full bg-blue-50 text-blue-600 hover:bg-blue-100 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 active:scale-95"
            onclick={() => _navigateMonth("next")}
            disabled={currentMonth.getMonth() === $currentDateReadOnly.getMonth() &&
                currentMonth.getFullYear() === $currentDateReadOnly.getFullYear()}
            data-dashlane-label="true"
            aria-label="Seuraava kuukausi"
        >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                ><path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2.5"
                    d="M9 5l7 7-7 7"
                /></svg
            >
        </button>
    </div>

    <div class="calendar-month__body space-y-2">
        <div
            class="calendar-month__grid-labels grid grid-cols-7 text-center text-[10px] font-bold text-gray-400 mb-2 uppercase tracking-wide"
        >
            <div>Ma</div>
            <div>Ti</div>
            <div>Ke</div>
            <div>To</div>
            <div>Pe</div>
            <div>La</div>
            <div>Su</div>
        </div>

        <div class="calendar-month__grid-days grid grid-cols-7 gap-0.5 sm:gap-1">
            {#each calendarDays as day}
                <button
                    class="calendar-month__day relative aspect-square rounded-full text-center transition-all duration-200 text-xs font-medium flex flex-col items-center justify-center border-2 border-transparent"
                    class:calendar-month__day--other-month={!day.isCurrentMonth}
                    class:calendar-month__day--today={day.isToday}
                    class:calendar-month__day--selected={day.isSelected}
                    class:opacity-30={!day.isCurrentMonth && !day.isSelected}
                    class:bg-blue-50={day.isToday && !day.isSelected}
                    class:text-blue-600={day.isToday && !day.isSelected}
                    class:bg-blue-600={day.isSelected}
                    class:text-white={day.isSelected}
                    class:shadow-md={day.isSelected}
                    class:hover:scale-110={!day.isFuture && !day.isSelected}
                    class:active:scale-95={!day.isFuture}
                    class:hover:bg-gray-50={!day.isToday && !day.isSelected && !day.isFuture}
                    class:cursor-not-allowed={day.isFuture}
                    disabled={day.isFuture}
                    onclick={() => _selectDate(day.dateStr)}
                    title={day.hasData ? "Pelejä tänä päivänä" : "Ei pelejä"}
                >
                    <span
                        class="calendar-month__day-number relative z-10"
                        class:font-bold={day.isToday || day.isSelected}
                    >
                        {day.date.getDate()}
                    </span>
                    {#if day.hasData}
                        <div
                            class="calendar-month__day-dot w-1 h-1 rounded-full mt-0.5"
                            class:bg-blue-400={!day.isSelected && !day.isToday}
                            class:bg-white={day.isSelected}
                        ></div>
                    {/if}
                </button>
            {/each}
        </div>
    </div>

    <div class="calendar-month__legend mt-4 pt-3 border-t border-gray-100">
        <div
            class="calendar-month__legend-item flex items-center space-x-2 text-[11px] text-gray-500 font-medium"
        >
            <div class="calendar-month__legend-dot w-2 h-2 rounded-full bg-blue-400"></div>
            <span class="calendar-month__legend-text">Pelipäivä</span>
        </div>
    </div>
</div>
