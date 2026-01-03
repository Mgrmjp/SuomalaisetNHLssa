<script>
import './LoadingSpinner.css'

/** @type {string} */
export const message = ''
</script>

<div class="loading-spinner" role="status" aria-label={message || 'Ladataan...'}>
  <div class="loading-spinner__dots">
    <span class="loading-spinner__dot loading-spinner__dot--1"></span>
    <span class="loading-spinner__dot loading-spinner__dot--2"></span>
    <span class="loading-spinner__dot loading-spinner__dot--3"></span>
  </div>
  {#if message}
    <p class="loading-spinner__message">{message}</p>
  {/if}
</div>
