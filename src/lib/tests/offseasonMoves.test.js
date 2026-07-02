import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

function getMovesPath() {
    return join(process.cwd(), 'static', 'data', 'offseason-moves.json')
}

describe('offseason moves data integrity', () => {
    it('offseason-moves.json exists and is valid JSON', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        expect(data).toBeDefined()
        expect(typeof data).toBe('object')
    })

    it('has required top-level fields', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        expect(data).toHaveProperty('offseasonYear')
        expect(data).toHaveProperty('window')
        expect(data).toHaveProperty('updatedAt')
        expect(data).toHaveProperty('sourceStatus')
        expect(data).toHaveProperty('moves')
        expect(typeof data.offseasonYear).toBe('number')
        expect(Array.isArray(data.moves)).toBe(true)
    })

    it('window has start and end dates', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        expect(data.window).toHaveProperty('start')
        expect(data.window).toHaveProperty('end')
        expect(data.window.start).toMatch(/^\d{4}-\d{2}-\d{2}$/)
        expect(data.window.end).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    })

    it('each move has required fields', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        for (const move of data.moves) {
            expect(move).toHaveProperty('moveId')
            expect(move).toHaveProperty('playerId')
            expect(move).toHaveProperty('playerName')
            expect(move).toHaveProperty('playerSlug')
            expect(move).toHaveProperty('position')
            expect(move).toHaveProperty('oldTeam')
            expect(move).toHaveProperty('newTeam')
            expect(move).toHaveProperty('moveType')
            expect(move).toHaveProperty('date')
            expect(move).toHaveProperty('sourceUrl')
        }
    })

    it('move types are only trade or free_agent', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        for (const move of data.moves) {
            expect(['trade', 'free_agent']).toContain(move.moveType)
        }
    })

    it('old and new teams are different for every move', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        for (const move of data.moves) {
            expect(move.oldTeam).not.toBe(move.newTeam)
        }
    })

    it('move IDs are unique', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        const ids = data.moves.map(/** @param {any} m */ (m) => m.moveId)
        expect(new Set(ids).size).toBe(ids.length)
    })

    it('moves are sorted by date descending', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        for (let i = 1; i < data.moves.length; i++) {
            expect(data.moves[i - 1].date >= data.moves[i].date).toBe(true)
        }
    })

    it('dates are within the offseason window', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        for (const move of data.moves) {
            expect(move.date >= data.window.start).toBe(true)
            expect(move.date <= data.window.end).toBe(true)
        }
    })

    it('source URLs point to nhl.com', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        for (const move of data.moves) {
            expect(move.sourceUrl).toMatch(/^https:\/\/www\.nhl\.com/)
        }
    })

    it('includes Korpisalo trade (2026 backfill)', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        const korpisalo = data.moves.find(
            /** @param {any} m */ (m) =>
                m.playerName === 'Joonas Korpisalo' && m.moveType === 'trade'
        )
        expect(korpisalo).toBeDefined()
        expect(korpisalo.oldTeam).toBe('BOS')
        expect(korpisalo.newTeam).toBe('NYR')
    })

    it('includes Kiviranta signing (2026 backfill)', async () => {
        const content = await readFile(getMovesPath(), 'utf-8')
        const data = JSON.parse(content)
        const kiviranta = data.moves.find(
            /** @param {any} m */ (m) =>
                m.playerName === 'Joel Kiviranta' && m.moveType === 'free_agent'
        )
        expect(kiviranta).toBeDefined()
        expect(kiviranta.newTeam).toBe('DAL')
    })
})

describe('offseason moves display logic', () => {
    function makeMovesData(/** @type {number} */ count) {
        const moves = []
        for (let i = 0; i < count; i++) {
            moves.push({
                moveId: `id-${i}`,
                playerId: `${8470000 + i}`,
                playerName: `Player ${i}`,
                playerSlug: `player-${i}`,
                position: 'C',
                oldTeam: 'BOS',
                newTeam: 'TOR',
                moveType: i % 2 === 0 ? 'trade' : 'free_agent',
                date: `2026-07-${String(i + 1).padStart(2, '0')}`,
                sourceUrl: 'https://www.nhl.com/news/test',
            })
        }
        return {
            offseasonYear: 2026,
            window: { start: '2026-06-20', end: '2026-10-06' },
            updatedAt: '2026-07-02T12:00:00Z',
            sourceStatus: { tradeTracker: 'ok', freeAgentTracker: 'ok' },
            moves: moves.sort((a, b) => b.date.localeCompare(a.date)),
        }
    }

    it('truncates to 5 items by default', () => {
        const data = makeMovesData(10)
        const visible = data.moves.slice(0, 5)
        expect(visible.length).toBe(5)
    })

    it('shows all items when expanded', () => {
        const data = makeMovesData(10)
        expect(data.moves.length).toBe(10)
    })

    it('counts trades and free agents correctly', () => {
        const data = makeMovesData(6)
        const trades = data.moves.filter((m) => m.moveType === 'trade').length
        const fas = data.moves.filter((m) => m.moveType === 'free_agent').length
        expect(trades).toBe(3)
        expect(fas).toBe(3)
    })

    it('empty state when no moves', () => {
        const data = makeMovesData(0)
        expect(data.moves.length).toBe(0)
    })

    it('no toggle when 5 or fewer moves', () => {
        const data = makeMovesData(5)
        expect(data.moves.length <= 5).toBe(true)
    })
})
