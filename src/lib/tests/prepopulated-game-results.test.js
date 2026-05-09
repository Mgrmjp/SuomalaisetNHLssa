import fs from 'node:fs'
import path from 'node:path'

import { describe, expect, it } from 'vitest'

const gamesDir = path.resolve(process.cwd(), 'static/data/prepopulated/games')
const validPersistedStates = new Set(['OFF', 'FINAL', 'FUT', 'PRE'])

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
                if (!validPersistedStates.has(game.gameState)) {
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
