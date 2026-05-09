import { describe, expect, it } from 'vitest'

import { formatGameScore } from '$lib/utils/gameFormatHelpers.mjs'

/**
 * @param {{ gameId: number, awayTeam: string, homeTeam: string, awayScore: number, homeScore: number, isOT: boolean, isSO: boolean }} game
 */
function gamesData(game) {
    return {
        /** @param {string|number} gameId */
        findGameById: (gameId) => (gameId === game.gameId ? game : null),
    }
}

describe('game format helpers', () => {
    it('keeps completed scores relative to the Finnish player team', () => {
        const player = {
            team: 'EDM',
            opponent: 'LAK',
            game_id: 2025030246,
            game_score: '4-2',
            game_result: 'W',
        }

        const game = {
            gameId: 2025030246,
            awayTeam: 'LAK',
            homeTeam: 'EDM',
            awayScore: 2,
            homeScore: 4,
            isOT: false,
            isSO: false,
        }

        expect(formatGameScore(player, gamesData(game))).toBe('4-2')
    })

    it('uses game data as a fallback when player-relative score is missing', () => {
        const player = {
            team: 'EDM',
            opponent: 'LAK',
            game_id: 2025030246,
            game_result: 'W',
        }

        const game = {
            gameId: 2025030246,
            awayTeam: 'LAK',
            homeTeam: 'EDM',
            awayScore: 2,
            homeScore: 4,
            isOT: false,
            isSO: false,
        }

        expect(formatGameScore(player, gamesData(game))).toBe('4-2')
    })
})
