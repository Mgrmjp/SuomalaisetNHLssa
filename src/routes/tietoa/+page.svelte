<script>
// @ts-nocheck
import { ChevronLeft } from 'lucide-svelte'

import { onMount } from 'svelte'
import { base } from '$app/paths'
import Card from '$lib/components/ui/Card.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'

function initKofi() {
    const container = document.getElementById('kofi-widget-container')
    if (typeof kofiwidget2 !== 'undefined' && container && container.innerHTML === '') {
        // Shim document.write to capture the widget's output
        const originalWrite = document.write
        const originalWriteln = document.writeln

        document.write = (content) => {
            container.innerHTML += content
        }
        document.writeln = (content) => {
            container.innerHTML += `${content}\n`
        }

        try {
            kofiwidget2.init('Support me on Ko-fi', '#3b82f6', 'Z8Z16PHF0')
            kofiwidget2.draw()
        } finally {
            // Always restore original functions
            document.write = originalWrite
            document.writeln = originalWriteln
        }
    }
}

onMount(() => {
    initKofi()
})
</script>

<svelte:head>
    <title>Tietoa - Suomi NHL | Suomalaiset NHL-pelaajat</title>
    <meta
        name="description"
        content="Tietoa Suomi NHL -sivustosta. Seuraa suomalaisten jääkiekkoilijoiden NHL-tilastoja, pistepörssiä ja otteluita päivittäin."
    />
    <meta property="og:title" content="Tietoa - Suomi NHL | Suomalaiset NHL-pelaajat" />
    <meta
        property="og:description"
        content="Tietoa Suomi NHL -sivustosta. Seuraa suomalaisten jääkiekkoilijoiden NHL-tilastoja, pistepörssiä ja otteluita päivittäin."
    />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/tietoa" />

    <!-- FAQPage Schema -->
    {@html `<script type="application/ld+json">${JSON.stringify({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: [
            {
                "@type": "Question",
                name: "Mistä saan tietoa suomalaisten NHL-pelaajien tilastoista?",
                acceptedAnswer: {
                    "@type": "Answer",
                    text: "Suomi NHL -sivusto seuraa päivittäin suomalaisten NHL-pelaajien ottelutilastoja, mukaan lukien maalit, syötöt, pisteet ja jääajat. Kaikki tiedot päivittyvät automaattisesti NHL:n virallisista lähteistä."
                }
            },
            {
                "@type": "Question",
                name: "Kuinka monta suomalaista pelaa NHL:ssä?",
                acceptedAnswer: {
                    "@type": "Answer",
                    text: "Suomi on yksi jääkiekon suurimmista NHL-maista. Tällä hetkellä NHL:ssä pelaa noin 30-35 suomalaista pelaajaa. Seuraa ajantasaisia tilastoja suomalaisetnhlssa.fi-sivustolta."
                }
            },
            {
                "@type": "Question",
                name: "Miten voin tukea sivustoa?",
                acceptedAnswer: {
                    "@type": "Answer",
                    text: "Voit tukea sivustoa lahjoittamalla Ko-fi-palvelun kautta tai klikkaamalla affiliate-linkkejä. Kaikki tuet menevät sivuston ylläpitokustannuksiin."
                }
            },
            {
                "@type": "Question",
                name: "Kuinka usein sivusto päivittyy?",
                acceptedAnswer: {
                    "@type": "Answer",
                    text: "Sivusto päivittyy automaattisesti kun uutta pelitietoa on saatavilla NHL:n virallisista lähteistä."
                }
            },
            {
                "@type": "Question",
                name: "Mistä tiedot tulevat?",
                acceptedAnswer: {
                    "@type": "Answer",
                    text: "Pelaajatiedot haetaan NHL:n virallisista lähteistä (NHL.com API)."
                }
            }
        ]
    })}</script>`}

    <script src="https://storage.ko-fi.com/cdn/widget/Widget_2.js" on:load={initKofi}></script>
</svelte:head>

<PageShell width="content" compact>
    <div class="info-page">
        <a href={base + "/"} class="back-link">
            <ChevronLeft size={16} aria-hidden="true" />
            Takaisin etusivulle
        </a>

        <PageHeader
            title="Tietoa Suomi NHL -sivustosta"
            subtitle="Suomalaisten NHL-tilastot selkeästi samassa paikassa."
            align="left"
            size="compact"
        />

        <div class="info-sections">
            <section class="info-section">
                <Card>
                    <h2>Sivustosta</h2>
                    <p>
                        Suomi NHL -sivusto seuraa suomalaisten NHL-pelaajien ottelutilastoja
                        päivittäin. Voit valita minkä tahansa päivän ja nähdä kyseisenä iltana
                        pelanneiden suomalaisten pelaajien maalit, syötöt, pisteet ja jääajat.
                        Sivusto tarjoaa ajantasaisen näkymän siihen, miten suomalaiset
                        jääkiekkoilijat menestyvät NHL-liigassa.
                    </p>
                </Card>
            </section>

            <section class="info-section">
                <Card>
                    <h2>Tietolähteet</h2>
                    <p>
                        Pelaajatiedot haetaan NHL:n virallisista lähteistä (NHL.com API). Sivusto
                        päivittyy automaattisesti kun uutta pelitietoa on saatavilla. Kaikki
                        suomalaisten NHL-tilastot päivittyvät reaaliajassa otteluiden päätyttyä.
                    </p>
                </Card>
            </section>

            <section class="info-section">
                <Card>
                    <h2>Mainosilmoitus</h2>
                    <div class="info-copy">
                        <p>
                            Tämä sivusto sisältää affiliate-mainoksia ja yhteistyölinkkejä. Sivusto
                            voi saada provission, jos käyttäjä klikkaa mainosta tai linkkiä ja tekee
                            oston.
                        </p>
                        <p>Mainokset näkyvät mm. seuraavien mainosverkostojen kautta:</p>
                        <ul>
                            <li>Adtraction</li>
                            <li>Muut affiliate-verkostot</li>
                        </ul>
                        <p class="disclosure-note">
                            Affiliate-yhteistyöt eivät vaikuta sivuston sisältöön tai näytettäviin
                            tilastoihin.
                        </p>
                    </div>
                </Card>
            </section>

            <section class="info-section support-section">
                <Card>
                    <h2>Tue sivustoa</h2>
                    <div id="kofi-widget-container"></div>
                </Card>
            </section>
        </div>

        <footer class="info-footer">
            <p>&copy; {new Date().getFullYear()} Suomalaiset NHL-pelaajat</p>
        </footer>
    </div>
</PageShell>

<style>
    .info-page {
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

    .back-link:focus-visible {
        outline: 3px solid var(--accent-glow);
        outline-offset: 3px;
    }

    .info-sections {
        display: grid;
        gap: var(--space-4);
    }

    .info-section :global(.card) {
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    h2 {
        margin: 0 0 var(--space-3);
        color: var(--color-ink);
        font-size: 1.2rem;
        font-weight: 700;
        line-height: 1.3;
    }

    p {
        margin: 0;
        color: #344054;
        line-height: 1.7;
    }

    .info-copy {
        display: grid;
        gap: var(--space-2);
    }

    ul {
        margin: 0 0 0 var(--space-6);
        color: #475467;
        list-style: disc;
    }

    li + li {
        margin-top: var(--space-1);
    }

    .disclosure-note {
        margin-top: var(--space-1);
        color: var(--color-muted);
        font-size: 0.875rem;
    }

    .support-section {
        text-align: center;
    }

    #kofi-widget-container {
        display: flex;
        justify-content: center;
        min-height: 2.75rem;
    }

    #kofi-widget-container :global(*) {
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    .info-footer {
        padding: var(--space-6) 0;
        text-align: center;
        font-size: 0.875rem;
    }

    .info-footer p {
        color: var(--color-muted);
    }
</style>
