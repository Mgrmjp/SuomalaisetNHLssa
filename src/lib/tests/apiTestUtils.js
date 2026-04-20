// @ts-nocheck
/**
 * API Test Utilities
 * Shared test utilities for API testing
 */

export function setupApiTestEnvironment() {
    const originalConsole = { ...console }
    vi.stubGlobal('console', {
        ...console,
        error: vi.fn(),
        warn: vi.fn(),
    })
    return originalConsole
}

export function createMockFetch(data) {
    return async () => createMockResponse(data)
}

export function createMockResponse(data, init = 200) {
    const status = typeof init === 'number' ? init : init.status || 200
    const headerValues = {
        'Cache-Control': 'public, max-age=300',
        ...(typeof init === 'object' ? init.headers || {} : {}),
    }

    return {
        status,
        ok: status >= 200 && status < 300,
        headers: {
            get(name) {
                return headerValues[name] || headerValues[name.toLowerCase()] || null
            },
        },
        json: async () => data,
    }
}

export async function measureResponseTime(fn) {
    const start = performance.now()
    const result = await fn()
    const end = performance.now()
    return { result, duration: end - start }
}

export const mockFinnishPlayers = [
    {
        id: 8477476,
        name: 'Artturi Lehkonen',
        nationality: 'FIN',
        position: 'L',
        team: 'COL',
        team_full: 'Colorado Avalanche',
    },
    {
        id: 8478420,
        name: 'Mikko Rantanen',
        nationality: 'FIN',
        position: 'R',
        team: 'DAL',
        team_full: 'Dallas Stars',
    },
    {
        id: 8477493,
        name: 'Aleksander Barkov',
        nationality: 'FIN',
        position: 'C',
        team: 'FLA',
        team_full: 'Florida Panthers',
    },
]

export function assertValidPlayer(player) {
    expect(player).toBeDefined()
    expect(player.name).toBeTruthy()
    expect(player.team).toBeTruthy()
    expect(player.position).toBeTruthy()

    if ('nationality' in player) {
        expect(['FIN', 'FI'].includes(player.nationality?.toUpperCase())).toBe(true)
    }
}

export function assertValidGameData(data) {
    expect(Array.isArray(data)).toBe(true)
    for (const player of data) {
        assertValidPlayer(player)
    }
}

export const mockGameData = [
    {
        player_id: 8477476,
        game_id: 2025020001,
        name: 'Artturi Lehkonen',
        team: 'COL',
        team_full: 'Colorado Avalanche',
        position: 'L',
        opponent: 'DAL',
        opponent_full: 'Dallas Stars',
        goals: 1,
        assists: 2,
        points: 3,
        game_score: '4-2',
        game_result: 'W',
    },
    {
        player_id: 8478420,
        game_id: 2025020002,
        name: 'Mikko Rantanen',
        team: 'DAL',
        team_full: 'Dallas Stars',
        position: 'R',
        opponent: 'COL',
        opponent_full: 'Colorado Avalanche',
        goals: 0,
        assists: 2,
        points: 2,
        game_score: '3-2',
        game_result: 'W',
    },
    {
        player_id: 8475179,
        game_id: 2025020003,
        name: 'Sebastian Aho',
        team: 'CAR',
        team_full: 'Carolina Hurricanes',
        position: 'C',
        opponent: 'NYI',
        opponent_full: 'New York Islanders',
        goals: 1,
        assists: 1,
        points: 2,
        game_score: '5-3',
        game_result: 'W',
    },
]
