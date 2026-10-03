<script lang="ts">
import type { Snippet } from 'svelte'

let {
    children,
    class: className = '',
}: {
    children: Snippet
    class?: string
} = $props()
</script>

<footer class={`view-metadata ${className}`}>
    {@render children()}
</footer>
