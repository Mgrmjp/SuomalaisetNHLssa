// @ts-nocheck
import { describe, expect, it } from 'vitest'
import {
    dailyPlayerPoints,
    didParticipate,
    getDailyHighlights,
    sortDailyPlayers,
} from '../utils/dailyPlayers.js'

const player = (fields = {}) => ({ playerId: 1, game_id: 42, position: 'C', ...fields })

describe('daily player selection', () => {
    it('includes a scoreless skater who played but excludes scratched and scheduled players', () => {
        expect(didParticipate(player({ time_on_ice: '12:30', points: 0 }))).toBe(true)
        expect(didParticipate(player({ time_on_ice: '00:00', points: 0 }))).toBe(false)
        expect(didParticipate(player({ game_status: 'OFF', points: 0 }))).toBe(false)
        expect(didParticipate(player({ game_status: 'OFF', points: 0, shots: 1 }))).toBe(true)
        expect(didParticipate(player({ game_status: 'FUT', time_on_ice: '00:00' }))).toBe(false)
        const scheduled = { findGameById: () => ({ gameState: 'FUT' }) }
        expect(didParticipate(player({}), scheduled)).toBe(false)
        const live = { findGameById: () => ({ gameState: 'LIVE' }) }
        expect(didParticipate(player({}), live)).toBe(false)
        expect(didParticipate(player({ time_on_ice: '1:30' }), live)).toBe(true)
    })

    it('derives points from goals and assists if the total is missing', () => {
        expect(dailyPlayerPoints(player({ goals: 1, assists: 2 }))).toBe(3)
        expect(dailyPlayerPoints(player({ points: 0, goals: 0, assists: 0 }))).toBe(0)
    })

    it('includes goalies with actual participation and excludes backups', () => {
        expect(didParticipate(player({ position: 'G', shots_against: 20 }))).toBe(true)
        expect(
            didParticipate(player({ position: 'G', time_on_ice: '00:00', shots_against: 0 }))
        ).toBe(false)
    })

    it('sorts by points, goals, assists, ice time or name without mutating the input', () => {
        const players = [
            player({ name: 'Aho', points: 1, goals: 0, assists: 1, time_on_ice: '20:01' }),
            player({ name: 'Barkov', points: 2, goals: 2, assists: 0, time_on_ice: '9:59' }),
        ]
        const names = (sort) => sortDailyPlayers(players, sort).map((p) => p.name)
        expect(names('points')).toEqual(['Barkov', 'Aho'])
        expect(names('goals')).toEqual(['Barkov', 'Aho'])
        expect(names('assists')).toEqual(['Aho', 'Barkov'])
        expect(names('time')).toEqual(['Aho', 'Barkov'])
        expect(names('name')).toEqual(['Aho', 'Barkov'])
        expect(players.map((p) => p.name)).toEqual(['Aho', 'Barkov'])
    })
})

describe('daily highlights', () => {
    it('recognizes multi-goal games and finished shutouts without highlighting ordinary performances', () => {
        const players = [
            player({ name: 'Hat Trick', goals: 3 }),
            player({ name: 'Two Goals', goals: 2 }),
            player({
                name: 'Shutout',
                position: 'G',
                shots_against: 25,
                goals_against: 0,
                game_status: 'OFF',
            }),
            player({
                name: 'Live Goalie',
                game_result: 'W',
                position: 'G',
                shots_against: 25,
                goals_against: 0,
                game_status: 'LIVE',
            }),
            player({ name: 'One Goal', goals: 1 }),
            player({ name: 'Two Assists', goals: 0, points: 2 }),
        ]
        expect(getDailyHighlights(players).map((item) => item.name)).toEqual([
            'Hat Trick',
            'Shutout',
            'Two Assists',
        ])
        const highlight = getDailyHighlights([
            player({ name: 'Two Goals', goals: 2, playerId: 7, game_id: 8 }),
        ])[0]
        expect(highlight).toMatchObject({ text: '2 maalia', playerId: 7, gameId: 8 })
    })
})

it('does not call a live game a shutout even if a result is present', () => {
    const games = { findGameById: () => ({ gameState: 'LIVE' }) }
    const goalie = player({
        name: 'Goalie',
        position: 'G',
        shots_against: 25,
        goals_against: 0,
        game_result: 'W',
    })
    expect(getDailyHighlights([goalie], games)).toEqual([])
})
