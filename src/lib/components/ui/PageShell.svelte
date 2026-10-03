<script>
// @ts-nocheck
import NavTabs from './NavTabs.svelte'

const { children, width = 'wide', compact = false, navigation = true } = $props()
</script>

<div class="page-shell dashboard-bg" class:page-shell--compact={compact} data-width={width}>
    {#if navigation}<div class="page-shell__navigation"><NavTabs /></div>{/if}
    {@render children()}
</div>

<style>
    .page-shell {
        position: relative;
        z-index: 1;
        width: min(calc(100% - 2 * var(--page-gutter)), var(--page-shell-max, var(--rail-max)));
        min-height: 100vh;
        margin-inline: auto;
        padding: var(--space-6) 0 var(--space-10);
    }

    .page-shell[data-width="dashboard"] {
        --page-shell-max: var(--rail-max);
    }

    .page-shell__navigation { margin-bottom: var(--space-6); }

    .page-shell[data-width="content"] {
        --page-shell-max: 56rem;
    }

    .page-shell[data-width="medium"] {
        --page-shell-max: 72rem;
    }

    .page-shell--compact {
        padding-block-start: var(--space-7);
    }

    @media (max-width: 640px) {
        .page-shell {
            padding-block: var(--space-7) var(--space-9);
        }
    }
</style>
