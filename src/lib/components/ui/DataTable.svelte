<script lang="ts">
import type { Snippet } from 'svelte'
import type { HTMLTableAttributes } from 'svelte/elements'

type Props = Omit<HTMLTableAttributes, 'class' | 'children'> & {
    children: Snippet
    caption: string
    class?: string
    scrollClass?: string
    regionId?: string
}

let {
    children,
    caption,
    class: className = '',
    scrollClass = '',
    regionId,
    ...attributes
}: Props = $props()
</script>

<!-- svelte-ignore a11y_no_noninteractive_tabindex (Keyboard users focus the table region to scroll it.) -->
<div
    id={regionId}
    class={`ui-table-scroll ${scrollClass}`}
    tabindex="0"
    role="region"
    aria-label={`${caption} – vieritettävä taulukko`}
>
    <table {...attributes} class={`ui-table ${className}`}>
        <caption class="sr-only">{caption}</caption>
        {@render children()}
    </table>
</div>
