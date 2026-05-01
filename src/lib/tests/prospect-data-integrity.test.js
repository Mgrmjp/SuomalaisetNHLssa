import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

/**
 * @typedef {object} Prospect
 * @property {string} id
 * @property {string} name
 * @property {string=} position
 * @property {string=} headshot
 * @property {string=} birthDate
 * @property {string[]=} sources
 */

/**
 * @typedef {object} GoalieSummary
 * @property {number} playerId
 * @property {string} goalieFullName
 * @property {string} teamAbbrevs
 * @property {number} savePct
 * @property {number} goalsAgainstAverage
 */

/** @type {Prospect[]} */
const prospects = JSON.parse(
    readFileSync(join(process.cwd(), 'static/data/finnish_prospects.json'), 'utf8')
)

/** @type {GoalieSummary[]} */
const goalies = JSON.parse(
    readFileSync(join(process.cwd(), 'static/data/player-stats/goalies-20252026.json'), 'utf8')
)

describe('Prospect data integrity', () => {
    it('keeps Otto Salin separate from Otto Kivenmaki league data', () => {
        const ottoSalin = prospects.find((player) => player.id === '8483509')
        const ottoKivenmaki = prospects.find((player) => player.id === '8481047')

        expect(ottoSalin?.name).toBe('Otto Salin')
        expect(ottoSalin?.position).not.toBe('G')
        expect(ottoSalin?.headshot).not.toContain('31165561')
        expect(ottoSalin?.sources).not.toContain('league_file:league_prospects_official')

        expect(ottoKivenmaki?.name).toBe('Otto Kivenmaki')
        expect(ottoKivenmaki?.birthDate).toBe('2000-03-24')
    })

    it('has NHL goalie summary fields used by the prospects page', () => {
        const nikkeKokko = goalies.find((goalie) => goalie.playerId === 8483668)

        expect(nikkeKokko?.goalieFullName).toBe('Nikke Kokko')
        expect(nikkeKokko?.teamAbbrevs).toBe('SEA')
        expect(nikkeKokko?.savePct).toBeGreaterThan(0)
        expect(nikkeKokko?.goalsAgainstAverage).toBeGreaterThan(0)
    })
})
