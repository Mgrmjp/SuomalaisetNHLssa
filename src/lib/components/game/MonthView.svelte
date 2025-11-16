<script>
import {
    formatDate,
    setDate,
    selectedDate,
    currentDateReadOnly,
    availableDates,
} from '$lib/stores/gameData.js'

// Generate calendar days for the current selected date's month
$: calendarDays = generateCalendarDays($selectedDate || formatDate($currentDateReadOnly))
$: currentMonth = $selectedDate ? new Date(`${$selectedDate}T00:00:00`) : $currentDateReadOnly

// Get the month and year display string
function _getMonthYearDisplay() {
    return currentMonth.toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric',
    })
}

// Navigate between months
function _navigateMonth(direction) {
    const newMonth = new Date(currentMonth)
    if (direction === 'prev') {
        newMonth.setMonth(newMonth.getMonth() - 1)
    } else {
        newMonth.setMonth(newMonth.getMonth() + 1)
        // Don't go beyond current date
        if (newMonth > $currentDateReadOnly) return
    }

    // Keep the same day of month if possible, otherwise go to last day of month
    const originalDay = currentMonth.getDate()
    const daysInNewMonth = new Date(newMonth.getFullYear(), newMonth.getMonth() + 1, 0).getDate()
    newMonth.setDate(Math.min(originalDay, daysInNewMonth))

    // Update the selected date
    setDate(formatDate(newMonth))
}

// Select a specific date
function _selectDate(dateStr) {
    setDate(dateStr)
}

function generateCalendarDays(selectedDateStr) {
    const date = new Date(`${selectedDateStr}T00:00:00`)
    const year = date.getFullYear()
    const month = date.getMonth()

    // First day of month
    const firstDay = new Date(year, month, 1)
    // Last day of month
    const lastDay = new Date(year, month + 1, 0)

    // Start from Sunday of the first week
    const startDate = new Date(firstDay)
    startDate.setDate(startDate.getDate() - firstDay.getDay())

    // End on Saturday of the last week
    const endDate = new Date(lastDay)
    endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()))

    const days = []
    const current = new Date(startDate)

    while (current <= endDate) {
        const dateStr = formatDate(current)
        const hasData = $availableDates.includes(dateStr)
        
        // Test data for demonstration (remove in production)
        const testData = {
            '2024-10-25': 3,
            '2024-10-24': 1,
            '2024-10-22': 5,
            '2024-10-20': 2,
            '2024-10-18': 4,
            '2024-10-15': 1,
            '2024-10-12': 3,
        }
        let finnishScorers = testData[dateStr] || 0

        days.push({
            date: new Date(current),
            dateStr,
            isCurrentMonth: current.getMonth() === month,
            isToday: formatDate(current) === formatDate($currentDateReadOnly),
            isSelected: formatDate(current) === selectedDateStr,
            hasData: hasData || finnishScorers > 0,
            isFuture: current > $currentDateReadOnly,
            finnishScorers: finnishScorers,
        })
        current.setDate(current.getDate() + 1)
    }

    return days
}
</script>

<div class="bg-white rounded-xl shadow-medium p-3 border border-gray-100">
  <div class="flex items-center justify-between mb-3">
    <button 
      class="p-1 rounded bg-finnish-blue-500 text-white hover:bg-finnish-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 text-xs"
      on:click={() => _navigateMonth('prev')}
      disabled={currentMonth.getMonth() === $currentDateReadOnly.getMonth() && currentMonth.getFullYear() === $currentDateReadOnly.getFullYear()}
    >
      «
    </button>
    <h2 class="text-base font-bold text-gray-900">{_getMonthYearDisplay()}</h2>
    <button 
      class="p-1 rounded bg-finnish-blue-500 text-white hover:bg-finnish-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 text-xs"
      on:click={() => _navigateMonth('next')}
      disabled={currentMonth.getMonth() === $currentDateReadOnly.getMonth() && currentMonth.getFullYear() === $currentDateReadOnly.getFullYear()}
    >
      »
    </button>
  </div>
  
  <div class="space-y-1">
    <div class="grid grid-cols-7 gap-0.5 text-center text-xs font-semibold text-gray-600 mb-1">
      <div>S</div>
      <div>M</div>
      <div>T</div>
      <div>W</div>
      <div>T</div>
      <div>F</div>
      <div>S</div>
    </div>
    
    <div class="grid grid-cols-7 gap-0.5">
      {#each calendarDays as day}
        <button
          class="relative aspect-square p-0.5 rounded text-center transition-all duration-200 text-xs font-semibold"
          class:opacity-30={!day.isCurrentMonth}
          class:bg-finnish-blue-500={day.isToday && !day.isSelected}
          class:text-white={day.isToday}
          class:bg-gradient-to-br={day.isSelected}
          class:from-finnish-blue-500={day.isToday && day.isSelected}
          class:to-finnish-gold-500={day.isToday && day.isSelected}
          class:ring-2={day.isToday && day.isSelected}
          class:ring-white={day.isToday && day.isSelected}
          class:from-finnish-gold-400={day.isSelected && !day.isToday}
          class:to-finnish-gold-600={day.isSelected && !day.isToday}
          class:shadow-md={day.isSelected}
          class:ring-finnish-gold-500={day.isSelected && !day.isToday}
          class:bg-gray-50={!day.isToday && !day.isSelected}
          class:hover:bg-gray-100={!day.isFuture}
          class:cursor-not-allowed={day.isFuture}
          disabled={day.isFuture}
          on:click={() => _selectDate(day.dateStr)}
          title={day.hasData ? "Has player data" : "No data"}
        >
          <span class="text-xs">{day.date.getDate()}</span>
          {#if day.finnishScorers > 0 && day.isCurrentMonth}
            <div class="absolute bottom-0 left-1/2 -translate-x-1/2 bg-finnish-blue-500 text-white text-[8px] rounded-full w-4 h-4 flex items-center justify-center font-bold">
              {day.finnishScorers}
            </div>
          {/if}
        </button>
      {/each}
    </div>
  </div>
  
  <div class="mt-3 pt-2 border-t border-gray-200">
    <h3 class="text-xs font-semibold text-gray-700 mb-1">Tietoja</h3>
    <div class="flex items-center space-x-2 text-xs text-gray-600 mb-1">
      <div class="bg-finnish-blue-500 text-white text-[8px] rounded-full w-4 h-4 flex items-center justify-center font-bold">1</div>
      <span>= Suomalaisia pistemiehiä</span>
    </div>
    <div class="text-xs text-gray-500">
      Numero näyttää suomalaisten pelaajien määrän
    </div>
  </div>
</div>