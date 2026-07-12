<script>
import { ChevronLeft } from 'lucide-svelte'
import { base } from '$app/paths'

const {
    title,
    subtitle = '',
    size = 'standard',
    align = 'center',
    showLogo = true,
    backHref = '',
    backLabel = 'Takaisin',
    children,
} = $props()
</script>

<header class="page-header" class:page-header--left={align === 'left'} data-size={size}>
    {#if backHref}
        <a class="page-header__back" href={backHref}>
            <ChevronLeft aria-hidden="true" size={16} strokeWidth={2} />
            <span>{backLabel}</span>
        </a>
    {/if}
    {#if showLogo}
        <a href={base + "/"} class="page-header__logo-link" aria-label="Palaa etusivulle">
            <img
                src={base + "/logo.svg"}
                alt=""
                class="page-header__logo"
                width="64"
                height="64"
            />
        </a>
    {/if}
    <h1>{title}</h1>
    {#if subtitle}
        <p>{subtitle}</p>
    {/if}
    {#if children}
        <div class="page-header__actions">{@render children()}</div>
    {/if}
</header>

<style>
    .page-header {
        width: 100%;
        min-width: 0;
        max-width: 48rem;
        margin: 0 auto var(--space-9);
        overflow-wrap: anywhere;
        text-align: center;
    }

    .page-header--left {
        margin-inline: 0;
        text-align: left;
    }

    .page-header__logo-link {
        display: inline-block;
        margin-bottom: var(--space-5);
    }

    .page-header__back {
        display: flex;
        align-items: center;
        gap: var(--space-1);
        margin-bottom: var(--space-5);
        color: var(--color-muted);
        font-size: 0.875rem;
        font-weight: 700;
        text-decoration: none;
        width: fit-content;
        margin-inline: auto;
    }

    .page-header__back:hover {
        color: var(--accent);
    }

    .page-header--left .page-header__back {
        margin-inline: 0;
    }

    .page-header__back:focus-visible {
        outline: 3px solid var(--accent-glow);
        outline-offset: 3px;
    }

    .page-header__logo-link:focus-visible {
        outline: 3px solid var(--accent-glow);
        outline-offset: 3px;
    }

    .page-header__logo {
        display: block;
        width: 4rem;
        height: 4rem;
        transition: transform 0.2s ease;
    }

    .page-header__logo-link:hover .page-header__logo {
        transform: translateY(-1px);
    }

    h1 {
        margin: 0;
        color: var(--color-ink);
        font-size: clamp(2rem, 4vw, 3rem);
        font-weight: 800;
        line-height: 1.08;
    }

    [data-size="hero"] h1 {
        font-size: clamp(2.5rem, 5.2vw, 3.8rem);
        line-height: 1;
    }

    [data-size="compact"] h1 {
        font-size: clamp(1.75rem, 3vw, 2.25rem);
    }

    p {
        max-width: 42rem;
        margin: var(--space-4) auto 0;
        color: var(--color-muted);
        font-size: 1.05rem;
        line-height: 1.6;
    }

    .page-header--left p {
        margin-inline: 0;
    }

    .page-header__actions {
        margin-top: var(--space-6);
    }

    @media (max-width: 640px) {
        .page-header {
            margin-bottom: var(--space-7);
        }

        h1,
        [data-size="hero"] h1 {
            font-size: 2.25rem;
        }

        [data-size="compact"] h1 {
            font-size: 1.75rem;
        }

        p {
            font-size: 0.95rem;
        }
    }
</style>
