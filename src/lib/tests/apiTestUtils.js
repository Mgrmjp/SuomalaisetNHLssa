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

export function createMockResponse(data, status = 200) {
    return {
        status,
        ok: status >= 200 && status < 300,
        json: async () => data,
    }
}

export async function measureResponseTime(fn) {
    const start = performance.now()
    const result = await fn()
    const end = performance.now()
    return { result, duration: end - start }
}

export const mockFinnishPlayers = []

export function assertValidPlayer(player) {
    expect(player).toHaveProperty('name')
    expect(player).toHaveProperty('nationality', 'FIN')
}

export function assertValidGameData(data) {
    expect(data).toBeDefined()
}

export const mockGameData = {}
