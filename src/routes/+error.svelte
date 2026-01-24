<script>
    import { base } from "$app/paths";
    import Snowfall from "$lib/components/ui/Snowfall.svelte";
    import { page } from "$app/stores";
    import { onMount } from "svelte";

    let status = $page.status || 404;
    let message = "Sivua ei löytynyt";
    let randomTrivia = "";

    const TRIVIA_FACTS = [
        "Jari Kurri teki 601 maalia 1251 NHL-ottelussa - keskimäärin 0.48 maalia per ottelu.",
        "Suomi on voittanut jääkiekon MM-kultaa neljästi: 1995, 2011, 2019 ja 2022.",
        "Teemu Selänne on NHL:n kaikkien aikojen paras suomalainen pistemies 1457 tehopisteellä.",
        "Teemu Selänne pitää hallussaan NHL:n tulakkaiden maaliennätystä (76 maalia kaudella 1992-93).",
        "Esa Tikkanen voitti urallaan viisi Stanley Cup -mestaruutta.",
        "Miikka Kiprusoff voitti Vezina Trophyn NHL:n parhaana maalivahtina kaudella 2005-06.",
        "Aleksander Barkov oli ensimmäinen suomalainen NHL-joukkueen kapteeni, joka johdatti joukkueensa Stanley Cup -mestaruuteen (2024).",
        "Suomi voitti ensimmäisen olympiakultansa jääkiekossa Pekingissä 2022.",
        "Saku Koivu toimi Montreal Canadiensin kapteenina 10 vuotta (1999-2009), ollen seuran ensimmäinen eurooppalainen kapteeni.",
        "Pekka Rinne on ainoa suomalaismaalivahti, joka on tehnyt maalin NHL-ottelussa.",
        "Tuukka Rask on Boston Bruinsin seurahistorian voitokkain maalivahti.",
    ];

    if (status === 404) {
        message = "Sivua ei löytynyt";
    } else if (status === 500) {
        message = "Palvelinvirhe";
    }

    onMount(() => {
        randomTrivia = TRIVIA_FACTS[Math.floor(Math.random() * TRIVIA_FACTS.length)];
    });
</script>

<svelte:head>
    <title>{status} - {message} | Suomalaiset NHL:ssä</title>
</svelte:head>

<div class="min-h-screen bg-slate-50 relative overflow-hidden flex items-center justify-center">
    <Snowfall count={12} />

    <div class="max-w-2xl mx-auto px-4 py-16 text-center relative z-10">
        <!-- Animated Puck -->
        <div class="mb-8 flex justify-center">
            <div class="relative">
                <div
                    class="w-32 h-32 rounded-full bg-gradient-to-br from-gray-800 to-gray-900 shadow-2xl flex items-center justify-center animate-bounce"
                >
                    <div
                        class="w-24 h-24 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center border-4 border-gray-600"
                    >
                        <span class="text-5xl font-bold text-white">{status}</span>
                    </div>
                </div>
                <div
                    class="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-20 h-4 bg-black/20 rounded-full blur-sm"
                ></div>
            </div>
        </div>

        <!-- Error Message -->
        <h1 class="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            {message}
        </h1>
        <p class="text-lg text-slate-600 mb-8 max-w-md mx-auto">
            {#if status === 404}
                Peli on keskeytetty - etsimääsi sivua ei löytynyt. Kenties pelaaja on vaihdossa tai
                sivu on siirretty.
            {:else}
                Jään pinta on epätasainen - jotain odottamatonta tapahtui. Yritä uudelleen hetken
                kuluttua.
            {/if}
        </p>

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <a
                href={base + "/"}
                class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
            >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                    />
                </svg>
                Etusivulle
            </a>
            <a
                href={base + "/pelaajat"}
                class="inline-flex items-center gap-2 px-6 py-3 bg-white hover:bg-gray-50 text-slate-700 font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200 border border-slate-200"
            >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                </svg>
                Pelaajiin
            </a>
        </div>

        <!-- Fun Hockey Facts -->
        <div
            class="mt-12 p-6 bg-white rounded-2xl shadow-lg border border-slate-100 max-w-md mx-auto"
        >
            <p class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Tiesitkö?
            </p>
            <p class="text-slate-700">
                {randomTrivia}
            </p>
        </div>
    </div>
</div>

<style>
    @keyframes bounce {
        0%,
        100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    .animate-bounce {
        animation: bounce 2s infinite;
    }
</style>
