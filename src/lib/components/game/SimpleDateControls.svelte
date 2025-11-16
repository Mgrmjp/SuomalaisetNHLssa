<script>
	import Datepicker from 'flowbite-svelte/Datepicker.svelte'
	import { setDate, selectedDate, currentDateReadOnly } from '$lib/stores/gameData.js'
	import { getRelativeFinnishDate } from '$lib/utils/dateUtils.js'

	$: currentDateValue = $selectedDate || formatLocalDate($currentDateReadOnly)
	$: pickerValue = currentDateValue ? new Date(`${currentDateValue}T00:00:00`) : null

function goToPreviousDay() {
	const previousDay = new Date(currentDateValue)
	previousDay.setDate(previousDay.getDate() - 1)

	if (previousDay >= new Date(minDate)) {
		setDate(formatLocalDate(previousDay))
	}
}

function goToToday() {
	const today = formatLocalDate($currentDateReadOnly)
	setDate(today)
}

function goToNextDay() {
	const nextDay = new Date(currentDateValue)
	nextDay.setDate(nextDay.getDate() + 1)
	const today = formatLocalDate($currentDateReadOnly)

	if (formatLocalDate(nextDay) <= today) {
		setDate(formatLocalDate(nextDay))
	}
}

function formatLocalDate(date) {
	const d = typeof date === 'string' ? new Date(`${date}T00:00:00`) : date
	const year = d.getFullYear()
	const month = String(d.getMonth() + 1).padStart(2, '0')
	const day = String(d.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

	$: todayIso = formatLocalDate(new Date())
	$: displayDate = formatDotted(currentDateValue)
	$: maxDate = todayIso
	$: minDate = '2020-10-01'
	$: isPrevDisabled = new Date(currentDateValue) <= new Date(minDate)
	$: isNextDisabled = new Date(currentDateValue) >= new Date(maxDate)
	$: relativeLabel = getRelativeFinnishDate(currentDateValue, new Date(`${maxDate}T00:00:00`))

	function formatDotted(date) {
		return new Date(`${date}T00:00:00`).toLocaleDateString('fi-FI', {
			day: 'numeric',
			month: 'numeric',
			year: 'numeric'
		})
	}

	function handleSelect(date) {
		if (date instanceof Date && !Number.isNaN(date.valueOf())) {
			setDate(formatLocalDate(date))
		}
	}
</script>

<div class="date-controls w-full max-w-3xl mx-auto space-y-4">
	<div class="date-controls__card w-full bg-white border border-gray-200 rounded-xl shadow-lg p-4 md:p-5">
		<div class="flex items-center gap-3 md:gap-4 flex-wrap">
			<button
				type="button"
				on:click={goToPreviousDay}
				class="nav-btn"
				disabled={isPrevDisabled}
				aria-label="Edellinen päivä"
				title="Edellinen päivä"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
				</svg>
			</button>

			<div class="flex-1 flex flex-col gap-3">
				<div class="flex flex-wrap items-center justify-between gap-3">
					<div>
						<div class="text-sm font-semibold text-blue-800">Valittu päivämäärä</div>
						<div class="text-xl font-bold text-gray-900">{formatDotted(currentDateValue)}</div>
					</div>
					{#if relativeLabel}
						<span class="px-2 py-1 text-xs font-semibold text-blue-900 bg-white/80 border border-blue-300 rounded-full">{relativeLabel}</span>
					{/if}
					<button
						type="button"
						on:click={goToToday}
						class="px-4 py-2 text-sm font-semibold text-white rounded-lg gradient-button-primary gradient-button-primary--hover:scale cursor-pointer shadow-sm"
					>
						Tänään
					</button>
				</div>

				<label class="sr-only" for="game-date-picker">Valitse päivämäärä</label>
				<Datepicker
					id="game-date-picker"
					locale="fi-FI"
					translationLocale="fi-FI"
					firstDayOfWeek={1}
					bind:value={pickerValue}
					availableFrom={new Date(`${minDate}T00:00:00`)}
					availableTo={new Date(`${maxDate}T00:00:00`)}
					dateFormat={{ day: '2-digit', month: '2-digit', year: 'numeric' }}
					placeholder="Valitse päivämäärä"
					inputClass="picker-input"
					onselect={handleSelect}
				/>
			</div>

			<button
				type="button"
				on:click={goToNextDay}
				class="nav-btn"
				disabled={isNextDisabled}
				aria-label="Seuraava päivä"
				title="Seuraava päivä"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
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

	:global(.picker-input:focus) {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.4);
	}

	/* Flowbite calendar day colors */
	:global(.datepicker .day) {
		color: #0f172a;
	}

	:global(.datepicker .day:hover:not([aria-disabled='true'])) {
		background-color: #f3f4f6;
		color: #0f172a;
	}

	/* Match the card's light background when a day is selected */
	:global(.datepicker .day.selected),
	:global(.datepicker .day[aria-selected='true']) {
		background-color: #2563eb;
		color: #fff;
		border-color: #2563eb;
	}

	:global(.datepicker .day.selected:hover),
	:global(.datepicker .day[aria-selected='true']:hover) {
		background-color: #1d4ed8;
		color: #fff;
	}

	/* Fallback if the day isn't nested under .datepicker in the DOM */
	:global(button.day[aria-selected='true']) {
		background-color: #2563eb;
		color: #fff;
		border-color: #2563eb;
	}

	:global(button.day[aria-selected='true']:hover) {
		background-color: #1d4ed8;
		color: #fff;
	}

	/* Higher specificity than Flowbite utilities without !important */
	.date-controls :global(button.day[aria-selected='true']) {
		background-color: #2563eb;
		color: #fff;
		border-color: #2563eb;
		box-shadow: inset 0 0 0 1px #2563eb;
	}

	.date-controls :global(button.day[aria-selected='true']:hover) {
		background-color: #1d4ed8;
		color: #fff;
	}

	:global(.datepicker) {
		position: relative;
		z-index: 15;
	}

	:global(.datepicker-dropdown) {
		z-index: 25;
	}
</style>
