// @ts-nocheck
import { afterEach, describe, expect, it, vi } from 'vitest'
import {
    adaptStandingsSnapshot,
    isStandingsStale,
    StandingsService,
} from '../services/standingsService.js'

function snapshot() {
    const standings = []
    for (const [divisionIndex, division] of ['A', 'M', 'C', 'P'].entries()) {
        for (let index = 0; index < 8; index++)
            standings.push({
                teamAbbrev: { default: `T${divisionIndex}${index}` },
                teamName: { default: `Team ${divisionIndex}${index}` },
                seasonId: 20262027,
                date: '2026-10-03',
                conferenceAbbrev: divisionIndex < 2 ? 'E' : 'W',
                divisionAbbrev: division,
                gamesPlayed: 0,
                wins: 0,
                losses: 0,
                otLosses: 0,
                points: 0,
                goalFor: 0,
                goalAgainst: 0,
                divisionSequence: index + 1,
                conferenceSequence: (divisionIndex % 2) * 8 + index + 1,
                leagueSequence: divisionIndex * 8 + index + 1,
            })
    }
    return {
        seasonId: 20262027,
        sourceDate: '2026-10-03',
        fetchedAt: '2026-10-03T08:00:00Z',
        standings,
    }
}
afterEach(() => vi.unstubAllGlobals())

describe('official standings snapshot', () => {
    it('uses official ranks even when local points would suggest another order', () => {
        const data = snapshot()
        data.standings.reverse()
        const lower = data.standings.find((row) => row.teamAbbrev.default === 'T07')
        Object.assign(lower, { gamesPlayed: 10, wins: 10, points: 20, pointPctg: 1 })
        const { conferences, metadata } = adaptStandingsSnapshot(data)
        expect(conferences.eastern.atlantic.map((team) => team.team)).toEqual([
            'T00',
            'T01',
            'T02',
            'T03',
            'T04',
            'T05',
            'T06',
            'T07',
        ])
        expect(metadata.wildCards.eastern).toEqual(['T03', 'T04'])
        expect(metadata.seasonId).toBe(20262027)
    })
    it('rejects inconsistent records and invalid percentages', () => {
        for (const change of [
            { points: 4 },
            { gamesPlayed: 2 },
            { pointPctg: '90%' },
            { pointPctg: 2 },
        ]) {
            const data = snapshot()
            Object.assign(data.standings[0], change)
            expect(() => adaptStandingsSnapshot(data)).toThrow()
        }
        expect(adaptStandingsSnapshot(snapshot()).conferences.eastern.atlantic[0].last10).toBeNull()
    })
    it('keeps unplayed teams without inventing percentages or special-teams statistics', () => {
        const { conferences } = adaptStandingsSnapshot(snapshot())
        const team = conferences.eastern.atlantic[0]
        expect(team.pointsPercentage).toBeNull()
        expect(team.streak).toBe('')
        expect(team.last10).toBeNull()
        expect(team).not.toHaveProperty('penaltyKillPercentage')
    })
    it('rejects partial, duplicate and mixed-season snapshots', () => {
        const partial = snapshot()
        partial.standings.pop()
        expect(() => adaptStandingsSnapshot(partial)).toThrow()
        const duplicate = snapshot()
        duplicate.standings[1].teamAbbrev = duplicate.standings[0].teamAbbrev
        expect(() => adaptStandingsSnapshot(duplicate)).toThrow()
        const mixed = snapshot()
        mixed.standings[0].seasonId = 20252026
        expect(() => adaptStandingsSnapshot(mixed)).toThrow()
    })
    it('rejects invalid rankings and metadata', () => {
        const data = snapshot()
        data.standings[1].divisionSequence = 1
        expect(() => adaptStandingsSnapshot(data)).toThrow()
        const invalid = snapshot()
        invalid.fetchedAt = 'invalid'
        expect(() => adaptStandingsSnapshot(invalid)).toThrow()
    })
    it('marks snapshots stale after three hours, not based on their hockey date', () => {
        const metadata = snapshot()
        expect(isStandingsStale(metadata, Date.parse('2026-10-03T10:59:00Z'))).toBe(false)
        expect(isStandingsStale(metadata, Date.parse('2026-10-03T11:01:00Z'))).toBe(true)
    })
    it('reloads the deployed snapshot with cache bypass and never fetches game history', async () => {
        const fetcher = vi.fn().mockResolvedValue({ ok: true, json: async () => snapshot() })
        vi.stubGlobal('fetch', fetcher)
        await new StandingsService().loadLatest({ force: true })
        expect(fetcher).toHaveBeenCalledOnce()
        expect(fetcher.mock.calls[0][0]).toMatch(/\/data\/standings.json\?refresh=/)
        expect(fetcher.mock.calls[0][1]).toEqual({ cache: 'no-store' })
    })
})
