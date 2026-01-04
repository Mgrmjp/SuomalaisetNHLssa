<script>
    import {
        availableDates,
        currentDateReadOnly,
        formatDate,
        selectedDate,
        setDate,
        showCalendarView,
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
    function _selectDate(dateStr) {
        setDate(dateStr);
        showCalendarView.set(false);
    }

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

<div class="bg-white rounded-xl shadow-medium p-3 border border-gray-100">
    <div class="flex items-center justify-between mb-3">
        <button
            class="p-1 rounded bg-finnish-blue-500 text-white hover:bg-finnish-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 text-xs"
            onclick={() => _navigateMonth("prev")}
            disabled={currentMonth.getMonth() === $currentDateReadOnly.getMonth() &&
                currentMonth.getFullYear() === $currentDateReadOnly.getFullYear()}
        >
            «
        </button>
        <h2 class="text-base font-bold text-gray-900">{_getMonthYearDisplay()}</h2>
        <button
            class="p-1 rounded bg-finnish-blue-500 text-white hover:bg-finnish-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 text-xs"
            onclick={() => _navigateMonth("next")}
            disabled={currentMonth.getMonth() === $currentDateReadOnly.getMonth() &&
                currentMonth.getFullYear() === $currentDateReadOnly.getFullYear()}
        >
            »
        </button>
    </div>

    <div class="space-y-1">
        <div
            class="grid grid-cols-7 gap-0.5 text-center text-[10px] font-bold text-gray-500 mb-1 uppercase tracking-wider"
        >
            <div>Ma</div>
            <div>Ti</div>
            <div>Ke</div>
            <div>To</div>
            <div>Pe</div>
            <div>La</div>
            <div>Su</div>
        </div>

        <div class="grid grid-cols-7 gap-0.5">
            {#each calendarDays as day}
                <button
                    class="relative aspect-square p-0.5 rounded-lg text-center transition-all duration-200 text-xs font-semibold flex flex-col items-center justify-center"
                    class:opacity-20={!day.isCurrentMonth}
                    class:bg-finnish-blue-500={day.isToday && !day.isSelected}
                    class:bg-finnish-blue-800={day.isSelected}
                    class:text-white={day.isToday || day.isSelected}
                    class:shadow-lg={day.isSelected}
                    class:scale-105={day.isSelected}
                    class:z-10={day.isSelected}
                    class:bg-gray-50={!day.isToday && !day.isSelected}
                    class:hover:bg-gray-100={!day.isFuture && !day.isSelected}
                    class:cursor-not-allowed={day.isFuture}
                    disabled={day.isFuture}
                    onclick={() => _selectDate(day.dateStr)}
                    title={day.hasData ? "Pelejä tänä päivänä" : "Ei pelejä"}
                >
                    <span>{day.date.getDate()}</span>
                    {#if day.hasData && day.isCurrentMonth}
                        <div
                            class="w-1 h-1 rounded-full mt-0.5"
                            class:bg-finnish-blue-400={!day.isSelected && !day.isToday}
                            class:bg-white={day.isSelected || day.isToday}
                        ></div>
                    {/if}
                </button>
            {/each}
        </div>
    </div>

    <div class="mt-3 pt-2 border-t border-gray-100">
        <div class="flex items-center space-x-2 text-[10px] text-gray-500">
            <div class="w-1.5 h-1.5 rounded-full bg-finnish-blue-400"></div>
            <span>= Pelipäivä</span>
        </div>
    </div>
</div>
