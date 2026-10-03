<script lang="ts">
import './LoadingSpinner.css'

let { message = '', announce = true }: { message?: string; announce?: boolean } = $props()
</script>

<div class="loading-spinner" role={announce ? 'status' : undefined} aria-label={announce ? message || 'Ladataan…' : undefined}>
    <div class="loading-spinner__dots" aria-hidden="true">
        <span class="loading-spinner__dot loading-spinner__dot--1"></span>
        <span class="loading-spinner__dot loading-spinner__dot--2"></span>
        <span class="loading-spinner__dot loading-spinner__dot--3"></span>
    </div>
    {#if message}<p class="loading-spinner__message">{message}</p>{/if}
</div>
