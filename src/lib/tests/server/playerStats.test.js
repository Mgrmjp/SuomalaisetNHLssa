import { describe, expect, it } from 'vitest'
import {
    buildStatsApiUrl,
    formatSeasonId,
    getCurrentSeasonId,
    mergeRosterInfo,
} from '$lib/server/playerStats.js'

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
            age: 26,
            heightInches: 72,
            weightLbs: 190,
        })
        expect(stats[0]).not.toHaveProperty('birthDate')
    })
})
