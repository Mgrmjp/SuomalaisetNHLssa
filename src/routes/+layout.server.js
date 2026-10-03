import { redirect } from '@sveltejs/kit'
import { base } from '$app/paths'
import { isProspectsPath, PROSPECTS_ENABLED } from '$lib/config/features.js'

/** @type {import('./$types').LayoutServerLoad} */
export function load({ url }) {
    if (!PROSPECTS_ENABLED && isProspectsPath(url.pathname.slice(base.length))) {
        redirect(307, `${base}/`)
    }
}
