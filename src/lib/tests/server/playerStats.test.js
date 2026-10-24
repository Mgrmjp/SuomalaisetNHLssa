import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
    buildStatsApiUrl,
    fetchStats,
    formatSeasonId,
    getCurrentSeasonId,
    getStatsUpdatedAt,
    mergeRosterInfo,
} from '$lib/server/playerStats.js'
import { calculateAge, shiftMonthPreservingDay } from '$lib/utils/dateUtils.js'

describe('player stats server helpers', () => {
    it('calculates NHL season IDs around the October rollover', () => {
        expect(getCurrentSeasonId(new Date('2026-05-01T12:00:00Z'))).toBe('20252026')
        expect(getCurrentSeasonId(new Date('2026-10-01T12:00:00Z'))).toBe('20262027')
    })

    it('formats compact season IDs for display', () => {
        expect(formatSeasonId('20252026')).toBe('2025-26')
    })

    it('builds NHL stats URLs from explicit options', () => {
        const url = buildStatsApiUrl({
            statType: 'skater',
            seasonId: '20252026',
            gameTypeId: 3,
            sortProperty: 'points',
            limit: 500,
        })

        expect(url).toContain('/stats/rest/en/skater/summary')
        expect(url).toContain('seasonId%3D20252026')
        expect(url).toContain('gameTypeId%3D3')
        expect(url).toContain('%22property%22%3A%22points%22')
    })

    it('rejects a successful HTTP response with no stats array', async () => {
        const fetch = async () =>
            /** @type {any} */ ({ ok: true, json: async () => ({ message: 'bad response' }) })
        await expect(
            fetchStats(fetch, {
                statType: 'skater',
                seasonId: '20262027',
                sortProperty: 'points',
            })
        ).rejects.toThrow('Invalid skater stats response')
    })

    it('returns augmented copies without mutating source stats', () => {
        const stats = [{ playerId: 1, skaterFullName: 'Example Player' }]
        const roster = {
            1: {
                birthDate: '2000-05-15',
                heightInches: 72,
                weightLbs: 190,
            },
        }

        const [player] = mergeRosterInfo(stats, roster, new Date('2026-05-01T12:00:00Z'))

        expect(player).toMatchObject({
            playerId: 1,
            birthDate: '2000-05-15',
            age: 25,
            heightInches: 72,
            weightLbs: 190,
        })
        expect(stats[0]).not.toHaveProperty('birthDate')
    })

    it('uses the last collection time from season metadata', () => {
        const metadata = JSON.parse(
            readFileSync(join(process.cwd(), 'static/data/player-stats/metadata.json'), 'utf8')
        )
        expect(getStatsUpdatedAt(metadata.seasonId, ['skaters'])).toBe(metadata.updatedAt)
    })

    it('calculates age around birthdays and moves between short months', () => {
        expect(calculateAge('2000-12-01', new Date(2026, 9, 24))).toBe(25)
        expect(calculateAge('2000-10-24', new Date(2026, 9, 24))).toBe(26)
        expect(shiftMonthPreservingDay(new Date(2026, 2, 31), -1).getDate()).toBe(28)
        expect(shiftMonthPreservingDay(new Date(2026, 0, 31), 1).getMonth()).toBe(1)
    })
})
