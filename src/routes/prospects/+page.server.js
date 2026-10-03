import { redirect } from '@sveltejs/kit'
import { base } from '$app/paths'
import { PROSPECTS_ENABLED } from '$lib/config/features.js'

export function load() {
    redirect(PROSPECTS_ENABLED ? 301 : 307, PROSPECTS_ENABLED ? `${base}/lupaukset/` : `${base}/`)
}
