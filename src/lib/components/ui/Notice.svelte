<script lang="ts">
import { Info } from 'lucide-svelte'
import type { Snippet } from 'svelte'

let {
    children,
    actions,
    variant = 'info',
    class: className = '',
}: {
    children: Snippet
    actions?: Snippet
    variant?: 'info' | 'warning' | 'error' | 'recovery'
    class?: string
} = $props()
</script>

<div
    class={`ui-notice ${className}`}
    class:ui-notice--warning={variant === 'warning'}
    class:ui-notice--error={variant === 'error'}
    class:ui-notice--recovery={variant === 'recovery'}
    role={variant === 'error' ? 'alert' : 'status'}
>
    {#if variant === 'recovery'}
        <div class="ui-notice__message">
            <Info size={16} aria-hidden="true" />
            <div class="ui-notice__copy">{@render children()}</div>
        </div>
    {:else}
        {@render children()}
    {/if}
    {#if actions}<div class="ui-notice__actions">{@render actions()}</div>{/if}
</div>
