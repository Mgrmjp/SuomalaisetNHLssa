// @ts-nocheck
import { readFileSync } from 'node:fs'
import { join } from 'node:path'

export const prerender = true

function loadCupData() {
    const file = join(process.cwd(), 'static/data/stanley-cup-winners.json')
    return JSON.parse(readFileSync(file, 'utf-8'))
}

function prepareWinners(winners) {
    return winners
        .map((winner) => ({
            ...winner,
            wins: winner.years.length,
            validation: { verified: true, hasCup: true, source: 'local' },
        }))
        .sort((a, b) => {
            if (b.wins !== a.wins) return b.wins - a.wins
            return a.years[0].year - b.years[0].year
        })
}

/** @type {import('./$types').PageServerLoad} */
export function load() {
    const data = loadCupData()

    return {
        winners: prepareWinners(data.winners),
        lastUpdated: data.lastUpdated,
    }
}
