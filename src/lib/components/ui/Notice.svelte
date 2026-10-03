<script lang="ts">
import type { Snippet } from 'svelte'

let {
    children,
    variant = 'info',
    class: className = '',
}: {
    children: Snippet
    variant?: 'info' | 'warning' | 'error'
    class?: string
} = $props()
</script>

<div
    class={`ui-notice ${className}`}
    class:ui-notice--warning={variant === 'warning'}
    class:ui-notice--error={variant === 'error'}
    role={variant === 'error' ? 'alert' : 'status'}
>
    {@render children()}
</div>
