// @ts-nocheck
import { describe, expect, it } from 'vitest'

import {
    extractTeamFromHeadshot,
    normalizeRosterData,
    normalizeRosterPlayer,
} from '$lib/utils/rosterNormalization.js'

describe('extractTeamFromHeadshot', () => {
    it('reads the team segment from NHL mugshot URLs', () => {
        expect(
            extractTeamFromHeadshot('https://assets.nhle.com/mugs/nhl/20252026/CAR/8477476.png')
        ).toBe('CAR')
    })

    it('returns empty for unknown or missing URLs', () => {
        expect(extractTeamFromHeadshot('')).toBe('')
        expect(extractTeamFromHeadshot(null)).toBe('')
        expect(extractTeamFromHeadshot('https://example.com/photo.png')).toBe('')
    })
})

describe('normalizeRosterPlayer', () => {
    it('maps cache aliases onto canonical fields', () => {
        const player = normalizeRosterPlayer({
            playerId: 8477476,
            name: 'Sebastian Aho',
            position: 'C',
            teamAbbrev: 'CAR',
            sweaterNumber: 20,
            shootsCatches: 'L',
            heightInches: 71,
            weightLbs: 182,
            birthDate: '1997-07-26',
            birthCity: { default: 'Rauma' },
            birthCountry: 'FIN',
            draftYear: 2015,
            draftRound: 2,
            draftOverall: 35,
            isRookie: false,
            isActive: true,
        })

        expect(player).toMatchObject({
            id: 8477476,
            team: 'CAR',
            team_abbrev: 'CAR',
            jersey_number: 20,
            shoots_catches: 'L',
            height: 71,
            weight: 182,
            birth_city: 'Rauma',
            draft_round: 2,
            is_rookie: false,
            is_active: true,
        })
    })

    it('preserves explicit false and numeric zero values', () => {
        const player = normalizeRosterPlayer({
            playerId: 1,
            isRookie: false,
            isActive: false,
            draftRound: 0,
            gamesPlayed: 0,
        })

        expect(player.is_rookie).toBe(false)
        expect(player.is_active).toBe(false)
        expect(player.draft_round).toBe(0)
        expect(player.games_played).toBe(0)
    })

    it('treats players as active unless a flag explicitly says otherwise', () => {
        expect(normalizeRosterPlayer({ playerId: 1 }).is_active).toBe(true)
        expect(normalizeRosterPlayer({ playerId: 1, is_active: false }).is_active).toBe(false)
        expect(normalizeRosterPlayer({ playerId: 1, isActive: false }).is_active).toBe(false)
    })

    it('infers the team from the headshot when no team field exists', () => {
        const player = normalizeRosterPlayer({
            playerId: 2,
            headshot: 'https://assets.nhle.com/mugs/nhl/20252026/SEA/2.png',
        })

        expect(player.team).toBe('SEA')
        expect(player.team_abbrev).toBe('SEA')
    })

    it('supports snake_case aliases from legacy snapshots', () => {
        const player = normalizeRosterPlayer({
            id: 3,
            team: 'TOR',
            jersey_number: 36,
            birth_date: '1998-01-01',
            draft_round: 7,
            is_rookie: true,
            games_played: 12,
        })

        expect(player).toMatchObject({
            id: 3,
            team: 'TOR',
            team_abbrev: 'TOR',
            jersey_number: 36,
            birth_date: '1998-01-01',
            draft_round: 7,
            is_rookie: true,
            games_played: 12,
        })
    })

    it('keeps the raw name so consumers can apply their own display logic', () => {
        expect(normalizeRosterPlayer({ playerId: 4, name: 'Mikael Granlund' }).name).toBe(
            'Mikael Granlund'
        )
    })
})

describe('normalizeRosterData', () => {
    it('normalizes object payloads keyed by player ID', () => {
        const players = normalizeRosterData({
            1: { playerId: 1, name: 'A', teamAbbrev: 'CAR' },
            2: { playerId: 2, name: 'B', teamAbbrev: 'DAL' },
        })

        expect(players.map((player) => player.id)).toEqual([1, 2])
        expect(players.map((player) => player.team)).toEqual(['CAR', 'DAL'])
    })

    it('normalizes legacy array payloads', () => {
        const players = normalizeRosterData([{ id: 1, name: 'A', team: 'CAR', is_active: false }])

        expect(players).toHaveLength(1)
        expect(players[0]).toMatchObject({ id: 1, team: 'CAR', is_active: false })
    })
})
