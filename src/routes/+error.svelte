<script>
// @ts-nocheck

import { ChevronLeft, Home, Users } from 'lucide-svelte'
import { onMount } from 'svelte'
import { base } from '$app/paths'
import { page } from '$app/stores'
import Card from '$lib/components/ui/Card.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'

const status = page.status || 404
let _message = 'Sivua ei löytynyt'
let _randomTrivia = ''

const TRIVIA_FACTS = [
    'Jari Kurri teki 601 maalia 1251 NHL-ottelussa - keskimäärin 0.48 maalia per ottelu.',
    'Suomi on voittanut jääkiekon MM-kultaa neljästi: 1995, 2011, 2019 ja 2022.',
    'Teemu Selänne on NHL:n kaikkien aikojen paras suomalainen pistemies 1457 tehopisteellä.',
    'Teemu Selänne pitää hallussaan NHL:n tulakkaiden maaliennätystä (76 maalia kaudella 1992-93).',
    'Esa Tikkanen voitti urallaan viisi Stanley Cup -mestaruutta.',
    'Miikka Kiprusoff voitti Vezina Trophyn NHL:n parhaana maalivahtina kaudella 2005-06.',
    'Aleksander Barkov oli ensimmäinen suomalainen NHL-joukkueen kapteeni, joka johdatti joukkueensa Stanley Cup -mestaruuteen (2024).',
    'Suomi voitti ensimmäisen olympiakultansa jääkiekossa Pekingissä 2022.',
    'Saku Koivu toimi Montreal Canadiensin kapteenina 10 vuotta (1999-2009), ollen seuran ensimmäinen eurooppalainen kapteeni.',
    'Pekka Rinne on ainoa suomalaismaalivahti, joka on tehnyt maalin NHL-ottelussa.',
    'Tuukka Rask on Boston Bruinsin seurahistorian voitokkain maalivahti.',
]

if (status === 404) {
    _message = 'Sivua ei löytynyt'
} else if (status === 500) {
    _message = 'Palvelinvirhe'
}

onMount(() => {
    _randomTrivia = TRIVIA_FACTS[Math.floor(Math.random() * TRIVIA_FACTS.length)]
})
</script>

<svelte:head>
    <title>{status} - {_message} | Suomalaiset NHL:ssä</title>
</svelte:head>

<PageShell width="content" compact>
    <div class="error-page">
        <a href={base + "/"} class="back-link">
            <ChevronLeft size={16} aria-hidden="true" />
            Takaisin etusivulle
        </a>

        <PageHeader
            title={_message}
            subtitle={status === 404
                ? 'Peli on keskeytetty - etsimääsi sivua ei löytynyt. Kenties pelaaja on vaihdossa tai sivu on siirretty.'
                : 'Jään pinta on epätasainen - jotain odottamatonta tapahtui. Yritä uudelleen hetken kuluttua.'}
            align="left"
            size="compact"
        />

        <div class="error-surface">
            <Card accent>
                <div class="error-code" aria-hidden="true">{status}</div>

                <div class="error-actions">
                    <a href={base + "/"} class="error-action error-action--primary">
                        <Home size={20} aria-hidden="true" />
                        Etusivulle
                    </a>
                    <a href={base + "/pelaajat"} class="error-action error-action--secondary">
                        <Users size={20} aria-hidden="true" />
                        Pelaajiin
                    </a>
                </div>

                <div class="trivia">
                    <p class="trivia__label">Tiesitkö?</p>
                    <p>{_randomTrivia}</p>
                </div>
            </Card>
        </div>
    </div>
</PageShell>

<style>
    .error-page {
        display: grid;
        gap: var(--space-6);
    }

    .back-link {
        display: inline-flex;
        width: fit-content;
        align-items: center;
        gap: var(--space-2);
        color: var(--color-muted);
        font-size: 0.875rem;
        font-weight: 600;
        text-decoration: none;
        transition: color 0.16s ease;
    }

    .back-link:hover {
        color: var(--accent);
    }

    .back-link:focus-visible,
    .error-action:focus-visible {
        outline: 3px solid var(--accent-glow);
        outline-offset: 3px;
    }

    .error-surface :global(.card) {
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    .error-code {
        width: fit-content;
        margin-bottom: var(--space-6);
        padding: var(--space-3) var(--space-4);
        border: 1px solid var(--color-panel-border);
        border-radius: 0;
        background: var(--accent-ice);
        box-shadow: none;
        color: var(--accent);
        font-family: var(--font-display);
        font-size: clamp(2rem, 6vw, 3.5rem);
        font-weight: 800;
        line-height: 1;
    }

    .error-actions {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-3);
    }

    .error-action {
        display: inline-flex;
        min-height: 2.75rem;
        align-items: center;
        justify-content: center;
        gap: var(--space-2);
        padding: 0.65rem 1rem;
        border: 1px solid var(--accent);
        border-radius: 0;
        box-shadow: none;
        font-size: 0.9rem;
        font-weight: 700;
        text-decoration: none;
        transition: background-color 0.16s ease, color 0.16s ease;
    }

    .error-action--primary {
        background: var(--accent);
        color: #fff;
    }

    .error-action--primary:hover {
        background: var(--accent-strong);
    }

    .error-action--secondary {
        background: transparent;
        color: var(--accent);
    }

    .error-action--secondary:hover {
        background: var(--accent-ice);
    }

    .trivia {
        margin-top: var(--space-7);
        padding-top: var(--space-5);
        border-top: 1px solid var(--color-panel-border);
    }

    .trivia p {
        margin: 0;
        color: #344054;
        line-height: 1.65;
    }

    .trivia .trivia__label {
        margin-bottom: var(--space-2);
        color: var(--color-muted);
        font-size: var(--eyebrow-size);
        font-weight: var(--eyebrow-weight);
        letter-spacing: var(--eyebrow-track);
        text-transform: uppercase;
    }

    @media (max-width: 480px) {
        .error-actions {
            display: grid;
        }

        .error-action {
            width: 100%;
        }
    }
</style>
