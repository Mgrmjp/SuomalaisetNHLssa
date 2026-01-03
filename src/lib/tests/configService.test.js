/**
 * Configuration Service Tests
 *
 * Tests for the centralized configuration service that manages
 * environment variables and provides validated configuration values.
 */

import {
    getApiConfig,
    getBusinessConfig,
    getConfig,
    getConfigHealth,
    getPlayerApiUrl,
    getTeamLogoUrl,
    getUiConfig,
    initializeConfig,
    isFinnishNationalityCode,
    reloadConfig,
} from '$lib/services/configService.js'

describe('Configuration Service', () => {
    beforeEach(async () => {
        // Reset configuration before each test
        await reloadConfig()
    })

    describe('Initialization', () => {
        test('should initialize configuration successfully', async () => {
            const config = await initializeConfig()

            expect(config).toBeDefined()
            expect(config.api).toBeDefined()
            expect(config.business).toBeDefined()
            expect(config.ui).toBeDefined()
        })

        test('should provide consistent configuration across multiple calls', async () => {
            const config1 = await initializeConfig()
            const config2 = await initializeConfig()

            expect(config1).toBe(config2)
        })

        test('should handle configuration access gracefully', async () => {
            // The configuration service auto-initializes, so accessing config
            // should work without throwing an error
            await reloadConfig()

            expect(() => {
                const config = getConfig()
                expect(config).toBeDefined()
            }).not.toThrow()
        })
    })

    describe('API Configuration', () => {
        beforeEach(async () => {
            await initializeConfig()
        })

        test('should provide valid API configuration', () => {
            const apiConfig = getApiConfig()

            expect(apiConfig.baseUrl).toBe('https://api-web.nhle.com')
            expect(apiConfig.version).toBe('v1')
            expect(apiConfig.userAgent).toBe('Finnish-NHL-Tracker/4.0-Automatic')
            expect(apiConfig.requestTimeout).toBe(10000)
            expect(apiConfig.maxRetries).toBe(3)
            expect(apiConfig.retryDelay).toBe(2000)
            expect(apiConfig.batchSize).toBe(10)
            expect(apiConfig.apiDelay).toBe(500)
        })

        test('should generate valid player API URLs', () => {
            const testPlayerId = 8478401 // Connor McDavid
            const expectedUrl = 'https://api-web.nhle.com/v1/player/8478401/landing'

            const actualUrl = getPlayerApiUrl(testPlayerId)
            expect(actualUrl).toBe(expectedUrl)
        })

        test('should handle different player IDs correctly', () => {
            const testCases = [
                { id: 8478401, expected: 'https://api-web.nhle.com/v1/player/8478401/landing' },
                { id: 8478452, expected: 'https://api-web.nhle.com/v1/player/8478452/landing' },
                { id: 8471675, expected: 'https://api-web.nhle.com/v1/player/8471675/landing' },
            ]

            testCases.forEach(({ id, expected }) => {
                expect(getPlayerApiUrl(id)).toBe(expected)
            })
        })
    })

    describe('Business Configuration', () => {
        beforeEach(async () => {
            await initializeConfig()
        })

        test('should provide valid business configuration', () => {
            const businessConfig = getBusinessConfig()

            expect(businessConfig.finnishNationalityCodes).toContain('FIN')
            expect(businessConfig.finnishNationalityCodes).toContain('FINLAND')
            expect(businessConfig.earliestNhlDate).toBe('2010-10-01')
            expect(businessConfig.defaultSeasonStartDate).toBe('2025-10-01')
            expect(businessConfig.playerCacheTtl).toBe(21600000) // 6 hours
        })

        test('should correctly identify Finnish nationality codes', () => {
            expect(isFinnishNationalityCode('FIN')).toBe(true)
            expect(isFinnishNationalityCode('FINLAND')).toBe(true)
            expect(isFinnishNationalityCode('fin')).toBe(true) // Case insensitive
            expect(isFinnishNationalityCode('finland')).toBe(true) // Case insensitive
            expect(isFinnishNationalityCode('USA')).toBe(false)
            expect(isFinnishNationalityCode('CAN')).toBe(false)
            expect(isFinnishNationalityCode('')).toBe(false)
            expect(isFinnishNationalityCode(null)).toBe(false)
            expect(isFinnishNationalityCode(undefined)).toBe(false)
        })
    })

    describe('UI Configuration', () => {
        beforeEach(async () => {
            await initializeConfig()
        })

        test('should provide valid UI configuration', () => {
            const uiConfig = getUiConfig()

            expect(uiConfig.teamLogoCdnBaseUrl).toBe(
                'https://cdn.nhl.com/images/logos/teams-current-primary-light'
            )
        })

        test('should generate valid team logo URLs', () => {
            const testCases = [
                {
                    team: 'TOR',
                    expected:
                        'https://cdn.nhl.com/images/logos/teams-current-primary-light/tor.svg',
                },
                {
                    team: 'MTL',
                    expected:
                        'https://cdn.nhl.com/images/logos/teams-current-primary-light/mtl.svg',
                },
                {
                    team: 'EDM',
                    expected:
                        'https://cdn.nhl.com/images/logos/teams-current-primary-light/edm.svg',
                },
            ]

            testCases.forEach(({ team, expected }) => {
                expect(getTeamLogoUrl(team)).toBe(expected)
            })
        })
    })

    describe('Configuration Health', () => {
        beforeEach(async () => {
            await initializeConfig()
        })

        test('should report healthy configuration', () => {
            const health = getConfigHealth()

            expect(health.isHealthy).toBe(true)
            expect(health.isInitialized).toBe(true)
            expect(health.hasConfigCache).toBe(true)
            expect(health.errors).toHaveLength(0)
            expect(health.lastValidation).toBeDefined()
        })

        test('should provide detailed health information', () => {
            const health = getConfigHealth()

            expect(health).toHaveProperty('isHealthy')
            expect(health).toHaveProperty('isInitialized')
            expect(health).toHaveProperty('hasConfigCache')
            expect(health).toHaveProperty('lastValidation')
            expect(health).toHaveProperty('errors')
            expect(health).toHaveProperty('warnings')
        })
    })

    describe('Configuration Reload', () => {
        test('should reload configuration successfully', async () => {
            await initializeConfig()
            const originalConfig = getConfig()

            // Reload configuration
            const newConfig = await reloadConfig()

            expect(newConfig).toBeDefined()
            expect(newConfig).not.toBe(originalConfig) // Should be a new object
        })
    })

    describe('Configuration Validation', () => {
        test('should handle missing environment variables gracefully', async () => {
            // The configuration service should provide fallbacks
            // when environment variables are missing
            const config = await initializeConfig()

            // Verify fallbacks are working
            expect(config.api.baseUrl).toBeTruthy()
            expect(config.business.finnishNationalityCodes.length).toBeGreaterThan(0)
            expect(config.ui.teamLogoCdnBaseUrl).toBeTruthy()
        })
    })

    describe('Error Handling', () => {
        test('should handle invalid configuration values gracefully', async () => {
            // The configuration service should validate and correct invalid values
            const config = await initializeConfig()

            // All numeric values should be valid numbers
            expect(typeof config.api.requestTimeout).toBe('number')
            expect(config.api.requestTimeout).toBeGreaterThan(0)

            expect(typeof config.business.playerCacheTtl).toBe('number')
            expect(config.business.playerCacheTtl).toBeGreaterThan(0)

            // All string values should be non-empty
            expect(typeof config.api.baseUrl).toBe('string')
            expect(config.api.baseUrl.trim().length).toBeGreaterThan(0)

            expect(typeof config.business.earliestNhlDate).toBe('string')
            expect(config.business.earliestNhlDate.trim().length).toBeGreaterThan(0)
        })
    })
})
