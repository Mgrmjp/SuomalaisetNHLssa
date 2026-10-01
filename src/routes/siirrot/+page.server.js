import { loadOffseasonMovesFromDisk } from '$lib/server/offseasonMoves.js'

export const prerender = true

export async function load() {
    return { offseasonMoves: await loadOffseasonMovesFromDisk() }
}
