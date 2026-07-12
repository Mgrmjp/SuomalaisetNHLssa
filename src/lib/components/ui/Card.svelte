<script>
// @ts-nocheck
const { children, padding = 'normal', accent = false, interactive = false } = $props()
</script>

<div
    class="card"
    class:card--accent={accent}
    class:card--interactive={interactive}
    data-padding={padding}
>
    {@render children()}
</div>

<style>
    .card {
        position: relative;
        min-width: 0;
        max-width: 100%;
        overflow: hidden;
        background: var(--card-bg);
        border: var(--card-border);
    }

    .card[data-padding="normal"] {
        padding: var(--card-padding-y) var(--card-padding-x);
    }

    .card[data-padding="compact"] {
        padding: var(--space-4);
    }

    .card[data-padding="none"] {
        padding: 0;
    }

    .card--accent::before {
        content: "";
        position: absolute;
        inset: 0 0 auto;
        height: 3px;
        background: var(--card-accent);
    }

    .card--interactive {
        transition: border-color 0.16s ease, background-color 0.16s ease;
    }

    .card--interactive:hover {
        border-color: rgba(0, 53, 128, 0.2);
        background: rgba(255, 255, 255, 0.74);
    }
</style>
