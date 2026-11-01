import { redirect } from '@sveltejs/kit'
import { base } from '$app/paths'
import { TRANSFERS_ENABLED } from '$lib/config/features.js'
import { loadOffseasonMovesFromDisk } from '$lib/server/offseasonMoves.js'

export const prerender = true

export async function load() {
    if (!TRANSFERS_ENABLED) redirect(307, `${base}/`)
    return { offseasonMoves: await loadOffseasonMovesFromDisk() }
}
