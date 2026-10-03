<script lang="ts">
import type { Snippet } from 'svelte'
import LoadingSpinner from './LoadingSpinner.svelte'

let {
    title,
    message,
    busy = false,
    children,
    actions,
    class: className = '',
}: {
    title?: string
    message?: string
    busy?: boolean
    children?: Snippet
    actions?: Snippet
    class?: string
} = $props()
</script>

<div class={`ui-state ${className}`} role={busy ? 'status' : undefined}>
    {#if title}<h2 class="section-title">{title}</h2>{/if}
    {#if busy}
        <LoadingSpinner message={message || 'Ladataan…'} announce={false} />
    {:else if message}
        <p>{message}</p>
    {/if}
    {@render children?.()}
    {@render actions?.()}
</div>
