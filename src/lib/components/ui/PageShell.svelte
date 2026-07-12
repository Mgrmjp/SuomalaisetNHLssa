<script>
// @ts-nocheck
const { children, width = 'wide', compact = false } = $props()
</script>

<div class="page-shell dashboard-bg" class:page-shell--compact={compact} data-width={width}>
    {@render children()}
</div>

<style>
    .page-shell {
        position: relative;
        z-index: 1;
        width: min(100%, var(--page-shell-max, 80rem));
        min-height: 100vh;
        margin-inline: auto;
        padding: var(--space-9) var(--page-gutter) var(--space-10);
    }

    .page-shell[data-width="dashboard"] {
        --page-shell-max: var(--rail-max);
    }

    .page-shell[data-width="content"] {
        --page-shell-max: 48rem;
    }

    .page-shell[data-width="medium"] {
        --page-shell-max: 64rem;
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
