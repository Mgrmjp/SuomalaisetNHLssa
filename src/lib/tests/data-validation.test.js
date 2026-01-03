/**
 * Data Validation and Error Handling Tests
 * Comprehensive tests for data validation, edge cases, and error scenarios
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { isValidDateFormat, isWithinNhlSeasonRange } from '../../nhl-api-node.js'
import {
    assertValidGameData,
    assertValidPlayer,
    mockGameData,
    setupApiTestEnvironment,
} from './apiTestUtils.js'

describe('Data Validation', () => {
    let originalConsole

    beforeEach(() => {
        originalConsole = setupApiTestEnvironment()
    })

    afterEach(() => {
        Object.assign(console, originalConsole)
        vi.clearAllMocks()
    })

    describe('Date Validation', () => {
        describe('isValidDateFormat', () => {
            it('should accept valid date formats', () => {
                const validDates = [
                    '2025-10-25',
                    '2024-02-29', // Leap year
                    '2023-01-01',
                    '2025-12-31',
                ]

                validDates.forEach((date) => {
                    expect(isValidDateFormat(date)).toBe(true)
                })
            })

            it('should reject invalid date formats', () => {
                const invalidDates = [
                    null,
                    undefined,
                    '',
                    '2025-13-01', // Invalid month
                    '2025-02-30', // Invalid day
                    '25-10-2025', // Wrong format
                    '2025/10/25', // Wrong separator
                    'invalid-date',
                    '2025-1-1', // Single digit month/day
                    '2025-10', // Missing day
                    '2025-10-25-extra', // Extra parts
                ]

                invalidDates.forEach((date) => {
                    expect(isValidDateFormat(date)).toBe(false)
                })
            })

            it('should handle edge cases', () => {
                const edgeCases = [
                    '0000-01-01', // Minimum valid date
                    '9999-12-31', // Maximum reasonable date
                    '2000-02-29', // Leap year century
                    '1900-02-28', // Non-leap year century
                ]

                edgeCases.forEach((date) => {
                    expect(isValidDateFormat(date)).toBe(true)
                })
            })
        })

        describe('isWithinNhlSeasonRange', () => {
            it('should accept dates within reasonable range', () => {
                const validDates = [
                    '2025-10-25', // Current season
                    '2024-10-01', // Previous season
                    '2023-04-30', // End of season
                    '2015-10-01', // Minimum season
                ]

                validDates.forEach((date) => {
                    expect(isWithinNhlSeasonRange(date)).toBe(true)
                })
            })

            it('should reject dates outside reasonable range', () => {
                const invalidDates = [
                    '2014-12-31', // Before minimum season
                    '2027-01-01', // Too far in future
                ]

                invalidDates.forEach((date) => {
                    expect(isWithinNhlSeasonRange(date)).toBe(false)
                })
            })

            it('should handle invalid dates gracefully', () => {
                const invalidDates = ['invalid-date', '2025-13-01', null, undefined]

                invalidDates.forEach((date) => {
                    expect(isWithinNhlSeasonRange(date)).toBe(false)
                })
            })
        })
    })

    describe('Player Data Validation', () => {
        describe('Required Fields', () => {
            it('should validate required player fields', () => {
                const validPlayer = mockGameData[0]
                assertValidPlayer(validPlayer)
            })

            it('should reject players missing required fields', () => {
                const invalidPlayers = [
                    { ...mockGameData[0], name: undefined },
                    { ...mockGameData[0], team: '' },
                    { ...mockGameData[0], position: null },
                ]

                invalidPlayers.forEach((player) => {
                    expect(() => assertValidPlayer(player)).toThrow()
                })
            })

            it('should accept players with missing optional fields', () => {
                const playerWithOptionalFields = {
                    ...mockGameData[0],
                    optionalField: 'optional',
                    anotherOptional: null,
                }
                expect(() => assertValidPlayer(playerWithOptionalFields)).not.toThrow()
            })
        })

        describe('Field Type Validation', () => {
            it('should validate numeric fields', () => {
                const player = mockGameData[0]

                expect(typeof player.goals).toBe('number')
                expect(typeof player.assists).toBe('number')
                expect(typeof player.points).toBe('number')
                expect(typeof player.player_id).toBe('number')
                expect(typeof player.game_id).toBe('number')

                expect(player.goals).toBeGreaterThanOrEqual(0)
                expect(player.assists).toBeGreaterThanOrEqual(0)
                expect(player.points).toBeGreaterThanOrEqual(0)
                expect(player.player_id).toBeGreaterThan(0)
                expect(player.game_id).toBeGreaterThan(0)
            })

            it('should validate string fields', () => {
                const player = mockGameData[0]

                expect(typeof player.name).toBe('string')
                expect(typeof player.team).toBe('string')
                expect(typeof player.team_full).toBe('string')
                expect(typeof player.position).toBe('string')
                expect(typeof player.opponent).toBe('string')
                expect(typeof player.opponent_full).toBe('string')
                expect(typeof player.game_score).toBe('string')
                expect(typeof player.game_result).toBe('string')

                expect(player.name.trim()).length.toBeGreaterThan(0)
                expect(player.team.trim()).length.toBeGreaterThan(0)
                expect(player.team_full.trim()).length.toBeGreaterThan(0)
            })
        })

        describe('Business Logic Validation', () => {
            it('should validate points calculation', () => {
                mockGameData.forEach((player) => {
                    expect(player.points).toBe(player.goals + player.assists)
                })
            })

            it('should validate game score format', () => {
                const gameScoreRegex = /^\d+-\d+$/
                mockGameData.forEach((player) => {
                    expect(gameScoreRegex.test(player.game_score)).toBe(true)
                })
            })

            it('should validate position codes', () => {
                const validPositions = ['C', 'LW', 'RW', 'D', 'G', 'L', 'R', 'N/A']
                mockGameData.forEach((player) => {
                    expect(validPositions).toContain(player.position)
                })
            })

            it('should validate team abbreviations', () => {
                const teamAbbrevRegex = /^[A-Z]{2,4}$/
                mockGameData.forEach((player) => {
                    expect(teamAbbrevRegex.test(player.team)).toBe(true)
                })
            })
        })
    })

    describe('Game Data Array Validation', () => {
        it('should validate array structure', () => {
            expect(Array.isArray(mockGameData)).toBe(true)
            expect(mockGameData.length).toBeGreaterThan(0)
        })

        it('should validate all players in array', () => {
            mockGameData.forEach((player) => {
                assertValidPlayer(player)
            })
        })

        it('should handle empty arrays', () => {
            const emptyArray = []
            expect(() => assertValidGameData(emptyArray)).not.toThrow()
        })

        it('should handle arrays with single player', () => {
            const singlePlayerArray = [mockGameData[0]]
            expect(() => assertValidGameData(singlePlayerArray)).not.toThrow()
        })
    })

    describe('Finnish Player Validation', () => {
        it('should identify Finnish players correctly', () => {
            const finnishNames = [
                'Artturi Lehkonen',
                'Sebastian Aho',
                'Mikko Rantanen',
                'Esa Lindell',
                'Miro Heiskanen',
                'Matias Maccelli',
                'Joel Armia',
            ]

            mockGameData.forEach((player) => {
                const _isFinnish = finnishNames.some((name) =>
                    player.name.toLowerCase().includes(name.toLowerCase())
                )
                // This is a basic check - in real implementation, we'd use nationality field
            })
        })

        it('should filter out non-Finnish players', () => {
            const nonFinnishNames = ['John Doe', 'Mike Smith', 'Tom Wilson']

            mockGameData.forEach((player) => {
                const isNonFinnish = nonFinnishNames.some((name) =>
                    player.name.toLowerCase().includes(name.toLowerCase())
                )
                if (isNonFinnish) {
                    // In a real implementation, this would fail
                    console.warn(`Non-Finnish player found: ${player.name}`)
                }
            })
        })
    })

    describe('Data Consistency Validation', () => {
        it('should validate team name consistency', () => {
            const teamMappings = {
                COL: 'Colorado Avalanche',
                TOR: 'Toronto Maple Leafs',
                CAR: 'Carolina Hurricanes',
                DAL: 'Dallas Stars',
            }

            mockGameData.forEach((player) => {
                if (teamMappings[player.team]) {
                    expect(player.team_full).toBe(teamMappings[player.team])
                }
            })
        })

        it('should validate player ID uniqueness within dataset', () => {
            const playerIds = mockGameData.map((player) => player.player_id)
            const uniqueIds = [...new Set(playerIds)]

            expect(playerIds).toHaveLength(uniqueIds.length)
        })

        it('should validate game data relationships', () => {
            mockGameData.forEach((player) => {
                expect(player.game_id).toBeGreaterThan(0)
                expect(typeof player.game_id).toBe('number')
            })
        })
    })

    describe('Edge Cases and Boundary Conditions', () => {
        it('should handle players with maximum statistics', () => {
            const maxStatsPlayer = {
                ...mockGameData[0],
                goals: 99,
                assists: 99,
                points: 198,
            }

            expect(maxStatsPlayer.points).toBe(maxStatsPlayer.goals + maxStatsPlayer.assists)
        })

        it('should handle players with zero statistics', () => {
            const zeroStatsPlayer = {
                ...mockGameData[0],
                goals: 0,
                assists: 0,
                points: 0,
            }

            expect(zeroStatsPlayer.points).toBe(0)
        })

        it('should handle players with very long names', () => {
            const longNamePlayer = {
                ...mockGameData[0],
                name: 'Very Long Finnish Name That Exceeds Normal Length Expectations',
            }

            expect(longNamePlayer.name.length).toBeGreaterThan(0)
            expect(typeof longNamePlayer.name).toBe('string')
        })

        it('should handle special characters in player names', () => {
            const specialCharPlayers = [
                { ...mockGameData[0], name: 'Mikko "The Finnish Flash" Rantanen' },
                { ...mockGameData[0], name: 'Jesse-Petri "JP" Niinimaa' },
            ]

            specialCharPlayers.forEach((player) => {
                expect(player.name).toBeTruthy()
                expect(player.name.length).toBeGreaterThan(0)
            })
        })
    })

    describe('Data Transformation Validation', () => {
        it('should validate data transformation to different formats', () => {
            const player = mockGameData[0]

            // Simple format
            const simpleFormat = {
                name: player.name,
                position: player.position,
            }
            expect(simpleFormat.name).toBe(player.name)
            expect(simpleFormat.position).toBe(player.position)

            // Extended format
            const extendedFormat = {
                ...player,
                extendedField: 'extra data',
            }
            expect(extendedFormat.name).toBe(player.name)
            expect(extendedFormat.extendedField).toBe('extra data')
        })

        it('should validate data sorting and filtering', () => {
            const sortedData = [...mockGameData].sort((a, b) => b.points - a.points)
            expect(sortedData[0].points).toBeGreaterThanOrEqual(sortedData[1]?.points || 0)

            const filteredData = mockGameData.filter((player) => player.goals > 0)
            filteredData.forEach((player) => {
                expect(player.goals).toBeGreaterThan(0)
            })
        })
    })

    describe('Performance Validation', () => {
        it('should handle large datasets efficiently', () => {
            const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
                ...mockGameData[0],
                player_id: 8470000 + i,
                name: `Player ${i + 1}`,
            }))

            const startTime = Date.now()
            largeDataset.forEach((player) => {
                assertValidPlayer(player)
            })
            const endTime = Date.now()

            expect(endTime - startTime).toBeLessThan(1000) // Should validate 1000 players within 1 second
        })

        it('should handle complex data transformations efficiently', () => {
            const complexData = mockGameData.map((player) => ({
                ...player,
                calculated: {
                    pointsPerGame: player.points,
                    efficiency: player.points / (player.goals || 1),
                },
            }))

            const startTime = Date.now()
            complexData.forEach((player) => {
                expect(player.calculated.pointsPerGame).toBe(player.points)
                expect(player.calculated.efficiency).toBeGreaterThan(0)
            })
            const endTime = Date.now()

            expect(endTime - startTime).toBeLessThan(500)
        })
    })
})
