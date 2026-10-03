<script lang="ts">
import type { Snippet } from 'svelte'

let {
    children,
    label,
    class: className = '',
    scrollable = false,
}: {
    children: Snippet
    label: string
    class?: string
    scrollable?: boolean
} = $props()
</script>

<div
    class={`segmented-control ${className}`}
    class:segmented-control--scrollable={scrollable}
    role="group"
    aria-label={label}
>
    {@render children()}
</div>

<style>
    .segmented-control--scrollable {
        flex-wrap: nowrap;
        min-width: 0;
        max-width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    }
    .segmented-control--scrollable::-webkit-scrollbar { display: none; }
</style>
