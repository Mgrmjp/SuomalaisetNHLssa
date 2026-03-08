<script>
import { base } from '$app/paths'

/** @type {{ data: { slug: string, content: string } }} */
const { data } = $props()
</script>

<svelte:head>
    <title>Scouting Report - {data.slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</title>
    <meta name="description" content="Yksityiskohtainen scouting-raportti pelaajasta." />
</svelte:head>

<div class="min-h-screen bg-slate-50">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <!-- Back links -->
        <div class="mb-8 flex items-center gap-4">
            <a 
                href="{base}/scouting"
                class="inline-flex items-center text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
                Scouting Reports
            </a>
            <span class="text-slate-300">/</span>
            <a 
                href="{base}/lupaukset"
                class="inline-flex items-center text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
                Lupaukset
            </a>
        </div>

        <!-- Content -->
        <article class="bg-white rounded-xl shadow-sm border border-slate-200 p-8 md:p-12">
            <div class="prose prose-slate max-w-none">
                {@html data.content}
            </div>
        </article>

        <!-- Navigation -->
        <div class="mt-8 flex justify-between">
            <a 
                href="{base}/scouting"
                class="inline-flex items-center text-slate-600 hover:text-slate-900 transition-colors"
            >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
                Kaikki raportit
            </a>
        </div>
    </div>
</div>


