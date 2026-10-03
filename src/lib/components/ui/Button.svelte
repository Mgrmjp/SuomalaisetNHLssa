<script lang="ts">
import type { Snippet } from 'svelte'
import type { HTMLButtonAttributes } from 'svelte/elements'

type Props = Omit<HTMLButtonAttributes, 'class' | 'children'> & {
    children: Snippet
    class?: string
    variant?: 'default' | 'primary'
    selected?: boolean
}

let {
    children,
    class: className = '',
    variant = 'default',
    selected,
    type = 'button',
    'aria-pressed': pressed,
    ...attributes
}: Props = $props()
</script>

<button
    {...attributes}
    {type}
    class={`ui-control ${className}`}
    class:ui-control--selected={selected || variant === 'primary'}
    aria-pressed={selected ?? pressed}
>
    {@render children()}
</button>
