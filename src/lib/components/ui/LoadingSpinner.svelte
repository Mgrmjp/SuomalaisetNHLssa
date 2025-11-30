<script>
import './LoadingSpinner.css'

/** @type {string} */
export let message = 'Loading...'
/** @type {string} */
export let size = 'medium' // 'small' | 'medium' | 'large'
/** @type {boolean} */
export let showProgress = false
/** @type {number} */
export let progress = 0

$: sizeClasses = size === 'small' ? 'p-4 gap-3' : size === 'large' ? 'p-12 gap-6' : 'p-8 gap-6'
$: spinnerSize = size === 'small' ? 'w-8 h-8' : size === 'large' ? 'w-16 h-16' : 'w-12 h-12'
$: progressPercentage = Math.min(100, Math.max(0, progress))
</script>

<div class="flex flex-col items-center justify-center {sizeClasses} text-center bg-white rounded-lg border border-gray-200 shadow-md" role="status" aria-label={message}>
  <div class="relative {spinnerSize}">
    <div class="absolute inset-0 border-4 border-transparent border-t-gray-400 border-r-gray-400 rounded-full animate-spin"></div>
    <div class="absolute inset-0 border-4 border-transparent border-l-white border-b-white rounded-full animate-spin spinner-ring-reverse"></div>
    <div class="absolute inset-0 border-2 border-gray-300 rounded-full animate-spin spinner-ring-delayed"></div>
  </div>

  <div class="flex flex-col gap-3 max-w-xs">
    <p class="text-lg font-medium text-gray-900">{message}</p>

    {#if showProgress}
      <div class="relative">
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            class="bg-blue-500 h-2 rounded-full progress-bar"
            style="width: {progressPercentage}%"
            role="progressbar"
            aria-valuenow={progressPercentage}
            aria-valuemin="0"
            aria-valuemax="100"
          ></div>
        </div>
        <span class="text-sm text-gray-600 mt-1">{Math.round(progressPercentage)}%</span>
      </div>
    {/if}

    <p class="text-sm text-gray-500">
      <small>Finding Finnish NHL players and their performance data...</small>
    </p>
  </div>
</div>
