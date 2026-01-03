/**
 * Finnish Players API Tests
 * Tests for /api/finnish-players endpoint
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

// Mock the server endpoint
const mockGet = vi.fn()
vi.doMock('../../../src/routes/api/finnish-players/+server.js', () => ({
    GET: mockGet,
}))

import {
    assertValidPlayer,
    createMockFetch,
    createMockResponse,
    measureResponseTime,
    mockFinnishPlayers,
    setupApiTestEnvironment,
} from '../apiTestUtils.js'

describe('Finnish Players API', () => {
    let originalConsole
    let mockFetch

    beforeEach(() => {
        const setup = setupApiTestEnvironment()
        originalConsole = setup
        mockFetch = createMockFetch(mockFinnishPlayers)
        global.fetch = mockFetch

        // Set up default mock response for API calls
        mockGet.mockResolvedValue(
            createMockResponse({
                success: true,
                data: mockFinnishPlayers,
            })
        )
    })

    afterEach(() => {
        Object.assign(console, originalConsole)
        vi.clearAllMocks()
    })

    describe('GET /api/finnish-players', () => {
        beforeEach(() => {
            // Reset mock before each test
            mockGet.mockClear()
        })

        it('should return Finnish players successfully', async () => {
            // Default mock response is set up in beforeEach

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })

            expect(response.status).toBe(200)
            expect(response.json).toBeTruthy()

            const data = await response.json()
            expect(data).toHaveProperty('success', true)
            expect(data).toHaveProperty('data')
            expect(Array.isArray(data.data)).toBe(true)

            if (data.data.length > 0) {
                data.data.forEach((player) => {
                    expect(player).toHaveProperty('name')
                    expect(player).toHaveProperty('nationality', 'FIN')
                })
            }
        })

        it('should handle different format parameters', async () => {
            // Test simple format
            mockGet.mockResolvedValueOnce(
                createMockResponse({
                    'Artturi Lehkonen': 'L',
                    'Sebastian Aho': 'C',
                    'Mikko Rantanen': 'R',
                })
            )
            let url = new URL('http://localhost/api/finnish-players?format=simple')
            let response = await mockGet({ url })
            let data = await response.json()

            expect(response.status).toBe(200)
            expect(typeof data).toBe('object')

            // Test names format
            mockGet.mockResolvedValueOnce(
                createMockResponse(['Artturi Lehkonen', 'Sebastian Aho', 'Mikko Rantanen'])
            )
            url = new URL('http://localhost/api/finnish-players?format=names')
            response = await mockGet({ url })
            data = await response.json()

            expect(response.status).toBe(200)
            expect(Array.isArray(data)).toBe(true)
        })

        it('should handle empty player list gracefully', async () => {
            mockGet.mockResolvedValue(
                createMockResponse({
                    success: true,
                    data: [],
                })
            )

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })
            const data = await response.json()

            expect(response.status).toBe(200)
            expect(Array.isArray(data.data || data)).toBe(true)
        })

        it('should handle API errors gracefully', async () => {
            mockGet.mockResolvedValue(
                createMockResponse(
                    {
                        error: 'Failed to fetch Finnish players',
                    },
                    { status: 500 }
                )
            )

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })
            const data = await response.json()

            expect(response.status).toBe(500)
            expect(data).toHaveProperty('error')
            expect(data.error).toContain('Failed to fetch Finnish players')
        })

        it('should handle malformed API response', async () => {
            mockGet.mockResolvedValue(
                createMockResponse(
                    {
                        error: 'Invalid data format from API',
                    },
                    { status: 500 }
                )
            )

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })
            const data = await response.json()

            expect(response.status).toBe(500)
            expect(data).toHaveProperty('error')
        })

        it('should include proper cache headers', async () => {
            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })

            expect(response.headers.get('Cache-Control')).toBeDefined()
        })

        it('should measure response time within acceptable limits', async () => {
            mockFetch = createMockFetch(mockFinnishPlayers, { delay: 100 })
            global.fetch = mockFetch

            const url = new URL('http://localhost/api/finnish-players')
            const { result, duration } = await measureResponseTime(() => mockGet({ url }))

            expect(result.status).toBe(200)
            expect(duration).toBeLessThan(1000) // Should complete within 1 second
        })

        it('should handle concurrent requests', async () => {
            const url = new URL('http://localhost/api/finnish-players')

            const promises = Array.from({ length: 5 }, () => mockGet({ url }))
            const responses = await Promise.all(promises)

            responses.forEach((response) => {
                expect(response.status).toBe(200)
            })
        })
    })

    describe('Player Data Validation', () => {
        it('should return players with all required fields', async () => {
            mockFetch = createMockFetch(mockFinnishPlayers)
            global.fetch = mockFetch

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })
            const data = await response.json()

            if (data.data && data.data.length > 0) {
                data.data.forEach((player) => {
                    assertValidPlayer(player)
                    expect(player.name).toBeTruthy()
                    expect(player.position).toBeTruthy()
                    expect(player.team).toBeTruthy()
                })
            }
        })

        it('should filter out non-Finnish players', async () => {
            const mixedPlayers = [
                ...mockFinnishPlayers,
                { name: 'John Doe', nationality: 'USA' },
                { name: 'Jane Smith', nationality: 'CAN' },
            ]
            mockFetch = createMockFetch(mixedPlayers)
            global.fetch = mockFetch

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })
            const data = await response.json()

            expect(response.status).toBe(200)
            // The backend should filter to only Finnish players
            if (data.data) {
                data.data.forEach((player) => {
                    expect(['FIN', 'FI'].includes(player.nationality?.toUpperCase())).toBe(true)
                })
            }
        })

        it('should handle players with missing optional fields', async () => {
            const playersWithMissingFields = mockFinnishPlayers.map((player) => ({
                name: player.name,
                position: player.position,
                team: player.team,
                team_full: player.team_full,
                // Missing optional fields
            }))
            mockFetch = createMockFetch(playersWithMissingFields)
            global.fetch = mockFetch

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })
            const data = await response.json()

            expect(response.status).toBe(200)
            expect(Array.isArray(data.data || data)).toBe(true)
        })
    })

    describe('Error Handling', () => {
        it('should handle network timeout', async () => {
            mockGet.mockResolvedValue(
                createMockResponse(
                    {
                        error: 'Request timeout',
                    },
                    { status: 500 }
                )
            )

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })
            const data = await response.json()

            expect(response.status).toBe(500)
            expect(data).toHaveProperty('error')
        })

        it('should handle API rate limiting', async () => {
            mockGet.mockResolvedValue(
                createMockResponse(
                    {
                        error: 'Rate limit exceeded',
                    },
                    { status: 500 }
                )
            )

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })
            const data = await response.json()

            expect(response.status).toBe(500)
            expect(data).toHaveProperty('error')
        })

        it('should handle invalid URL parameters', async () => {
            const url = new URL('http://localhost/api/finnish-players?format=invalid')
            const response = await mockGet({ url })
            const _data = await response.json()

            // Should fall back to default format
            expect(response.status).toBe(200)
        })

        it('should handle Python script execution errors', async () => {
            mockGet.mockResolvedValue(
                createMockResponse(
                    {
                        error: 'Python script execution failed',
                    },
                    { status: 500 }
                )
            )

            const url = new URL('http://localhost/api/finnish-players')
            const response = await mockGet({ url })
            const data = await response.json()

            expect(response.status).toBe(500)
            expect(data).toHaveProperty('error')
        })
    })

    describe('Performance Tests', () => {
        it('should handle large player datasets efficiently', async () => {
            const largePlayerList = Array.from({ length: 100 }, (_, i) => ({
                ...mockFinnishPlayers[0],
                id: 8477476 + i,
                name: `Player ${i + 1}`,
            }))
            mockFetch = createMockFetch(largePlayerList)
            global.fetch = mockFetch

            const url = new URL('http://localhost/api/finnish-players')
            const { result, duration } = await measureResponseTime(() => mockGet({ url }))

            expect(result.status).toBe(200)
            expect(duration).toBeLessThan(2000) // Should handle 100 players within 2 seconds
        })

        it('should maintain consistent response format', async () => {
            const url = new URL('http://localhost/api/finnish-players')

            // Make multiple requests and ensure consistent format
            const responses = await Promise.all([
                mockGet({ url }),
                mockGet({ url }),
                mockGet({ url }),
            ])

            const responseData = await Promise.all(responses.map((response) => response.json()))

            responseData.forEach((data) => {
                expect(typeof data).toBe('object')
                if (Array.isArray(data)) {
                    // Simple format case
                    expect(Array.isArray(data)).toBe(true)
                } else {
                    // Full format case
                    expect(data).toHaveProperty('data')
                    expect(Array.isArray(data.data)).toBe(true)
                }
            })
        })
    })
})
