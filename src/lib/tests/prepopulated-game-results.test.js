import fs from 'node:fs'
import path from 'node:path'

import { describe, expect, it } from 'vitest'

const gamesDir = path.resolve(process.cwd(), 'static/data/prepopulated/games')
const validPersistedStates = new Set(['OFF', 'FINAL', 'FUT', 'PRE'])
// Realtime polling intentionally saves snapshots while games are in progress.
// An in-progress state is only stale once the scheduled start is in the past by
// more than this grace period (games last ~3h; the daily update finalizes them).
const inProgressStates = new Set(['LIVE', 'CRIT'])
const inProgressGraceMs = 24 * 60 * 60 * 1000

/**
 * @param {{gameState?: string, startTime?: string}} game
 * @returns {boolean}
 */
function isStaleState(game) {
    const state = game.gameState ?? ''
    if (validPersistedStates.has(state)) return false
    if (inProgressStates.has(state)) {
        const startedMs = Date.parse(game.startTime || '')
        return Number.isNaN(startedMs) || Date.now() - startedMs > inProgressGraceMs
    }
    return true
}

function readGameFiles() {
    return fs
        .readdirSync(gamesDir)
        .filter((file) => file.endsWith('.json'))
        .map((file) => ({
            file,
            data: JSON.parse(fs.readFileSync(path.join(gamesDir, file), 'utf8')),
        }))
}

describe('prepopulated game results', () => {
    it('does not persist stale in-progress game states', () => {
        const staleGames = []

        for (const { file, data } of readGameFiles()) {
            for (const game of data.games || []) {
                if (isStaleState(game)) {
                    staleGames.push(`${file}: ${game.gameId} ${game.gameState}`)
                }
            }
        }

        expect(staleGames).toEqual([])
    })

    it('keeps player scores aligned with final game summaries', () => {
        const mismatches = []

        for (const { file, data } of readGameFiles()) {
            const gamesById = new Map(
                (data.games || []).map((/** @type {{ gameId: number }} */ game) => [
                    game.gameId,
                    game,
                ])
            )

            for (const player of data.players || []) {
                const game = gamesById.get(player.game_id)
                if (!game || !player.game_score) continue

                let expectedScore = null
                if (player.team === game.homeTeam) {
                    expectedScore = `${game.homeScore}-${game.awayScore}`
                } else if (player.team === game.awayTeam) {
                    expectedScore = `${game.awayScore}-${game.homeScore}`
                }

                if (expectedScore && player.game_score !== expectedScore) {
                    mismatches.push(
                        `${file}: ${player.name} ${player.game_score} !== ${expectedScore}`
                    )
                }
            }
        }

        expect(mismatches).toEqual([])
    })
})
