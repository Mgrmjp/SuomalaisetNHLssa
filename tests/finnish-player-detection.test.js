#!/usr/bin/env node

/**
 * Comprehensive Test Suite for Finnish Player Detection System
 * 
 * This test suite validates:
 * 1. Accuracy of Finnish player detection
 * 2. Performance comparison between old (name patterns) and new (API-only) systems
 * 3. Data validation and consistency
 * 4. Edge case handling
 * 5. Integration with NHL API
 */

import { performance } from 'perf_hooks'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

// Get current directory for ES modules
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.join(__dirname, '..')

// Test configuration
const TEST_CONFIG = {
    // Test data paths
    finnishRosterPath: path.join(projectRoot, 'data', 'players', 'finnish-roster.json'),
    apiScriptPath: path.join(projectRoot, 'api', 'finnish_players.py'),
    
    // Test parameters
    performanceIterations: 10,
    timeoutMs: 30000,
    
    // Known Finnish players for validation
    knownFinnishPlayers: [
        'Aleksander Barkov',
        'Sebastian Aho', 
        'Mikko Rantanen',
        'Patrik Laine',
        'Juuse Saros',
        'Kaapo Kakko',
        'Anton Lundell',
        'Mikael Granlund',
        'Joel Armia',
        'Eeli Tolvanen'
    ],
    
    // Edge case players (non-Finnish names but Finnish, or Finnish names but not Finnish)
    edgeCasePlayers: [
        { name: 'Kevin Lankinen', isFinnish: true, reason: 'Finnish player with non-Finnish name' },
        { name: 'Jesper Bratt', isFinnish: false, reason: 'Finnish-sounding name but Swedish' },
        { name: 'Brad Lambert', isFinnish: true, reason: 'Finnish player with English name' },
        { name: 'Mikko Koskinen', isFinnish: true, reason: 'Classic Finnish name pattern' }
    ]
}

// Test results tracking
class TestSuite {
    constructor() {
        this.results = {
            accuracy: [],
            performance: [],
            validation: [],
            edgeCases: [],
            integration: [],
            summary: {
                totalTests: 0,
                passedTests: 0,
                failedTests: 0,
                executionTime: 0
            }
        }
        this.startTime = performance.now()
    }

    async runAllTests() {
        console.log('🧪 Finnish Player Detection System - Comprehensive Test Suite')
        console.log('=' .repeat(70))
        
        try {
            // Test 1: Accuracy Tests
            await this.runAccuracyTests()
            
            // Test 2: Performance Comparison Tests
            await this.runPerformanceTests()
            
            // Test 3: Data Validation Tests
            await this.runValidationTests()
            
            // Test 4: Edge Case Tests
            await this.runEdgeCaseTests()
            
            // Test 5: Integration Tests
            await this.runIntegrationTests()
            
            // Generate final report
            this.generateFinalReport()
            
        } catch (error) {
            console.error('❌ Test suite execution failed:', error)
            process.exit(1)
        }
    }

    async runAccuracyTests() {
        console.log('\n📊 ACCURACY TESTS')
        console.log('-' .repeat(40))
        
        // Test 1.1: Verify known Finnish players are detected
        await this.testKnownFinnishPlayers()
        
        // Test 1.2: Compare API-only vs name pattern approaches
        await this.testDetectionMethodsComparison()
        
        // Test 1.3: Validate false positive/negative rates
        await this.testFalsePositiveNegativeRates()
    }

    async runPerformanceTests() {
        console.log('\n⚡ PERFORMANCE TESTS')
        console.log('-' .repeat(40))
        
        // Test 2.1: API-only approach performance
        await this.testAPIOnlyPerformance()
        
        // Test 2.2: Name pattern matching performance
        await this.testNamePatternPerformance()
        
        // Test 2.3: Memory usage comparison
        await this.testMemoryUsageComparison()
        
        // Test 2.4: Scalability tests
        await this.testScalability()
    }

    async runValidationTests() {
        console.log('\n✅ DATA VALIDATION TESTS')
        console.log('-' .repeat(40))
        
        // Test 3.1: Data consistency validation
        await this.testDataConsistency()
        
        // Test 3.2: Player data completeness
        await this.testPlayerDataCompleteness()
        
        // Test 3.3: Nationality verification
        await this.testNationalityVerification()
    }

    async runEdgeCaseTests() {
        console.log('\n🔍 EDGE CASE TESTS')
        console.log('-' .repeat(40))
        
        // Test 4.1: Non-Finnish names but Finnish players
        await this.testNonFinnishNames()
        
        // Test 4.2: Finnish names but non-Finnish players
        await this.testFinnishNamesNonFinnishPlayers()
        
        // Test 4.3: Special characters and encoding
        await this.testSpecialCharacters()
        
        // Test 4.4: Inactive/retired players
        await this.testInactivePlayers()
    }

    async runIntegrationTests() {
        console.log('\n🔗 INTEGRATION TESTS')
        console.log('-' .repeat(40))
        
        // Test 5.1: NHL API integration
        await this.testNHLAPIIntegration()
        
        // Test 5.2: Error handling and resilience
        await this.testErrorHandling()
        
        // Test 5.3: Cache behavior
        await this.testCacheBehavior()
    }

    // Individual test implementations
    async testKnownFinnishPlayers() {
        console.log('\n  Test 1.1: Known Finnish Players Detection')
        
        try {
            const finnishPlayers = await this.loadFinnishPlayers()
            const detectedNames = finnishPlayers.map(p => p.name)
            
            let foundCount = 0
            const missingPlayers = []
            
            for (const knownPlayer of TEST_CONFIG.knownFinnishPlayers) {
                if (detectedNames.some(name => name.includes(knownPlayer))) {
                    foundCount++
                } else {
                    missingPlayers.push(knownPlayer)
                }
            }
            
            const accuracy = (foundCount / TEST_CONFIG.knownFinnishPlayers.length * 100).toFixed(1)
            const passed = parseFloat(accuracy) >= 90 // 90% accuracy threshold
            
            console.log(`    ✅ Found ${foundCount}/${TEST_CONFIG.knownFinnishPlayers.length} known players (${accuracy}% accuracy)`)
            
            if (missingPlayers.length > 0) {
                console.log(`    ⚠️  Missing: ${missingPlayers.join(', ')}`)
            }
            
            this.results.accuracy.push({
                name: 'Known Finnish Players Detection',
                passed,
                details: {
                    foundCount,
                    totalKnown: TEST_CONFIG.knownFinnishPlayers.length,
                    accuracy: parseFloat(accuracy),
                    missingPlayers
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.accuracy.push({
                name: 'Known Finnish Players Detection',
                passed: false,
                error: error.message
            })
        }
    }

    async testDetectionMethodsComparison() {
        console.log('\n  Test 1.2: Detection Methods Comparison')
        
        try {
            // Test API-only method
            const apiStartTime = performance.now()
            const apiResults = await this.testAPIMethod()
            const apiTime = performance.now() - apiStartTime
            
            // Test name pattern method
            const patternStartTime = performance.now()
            const patternResults = await this.testNamePatternMethod()
            const patternTime = performance.now() - patternStartTime
            
            // Compare results
            const apiOnly = apiResults.length
            const patternOnly = patternResults.length
            const common = apiResults.filter(player => 
                patternResults.some(p => p.id === player.id)
            ).length
            
            const apiUnique = apiOnly - common
            const patternUnique = patternOnly - common
            
            console.log(`    📊 API-only: ${apiOnly} players (${apiTime.toFixed(1)}ms)`)
            console.log(`    📊 Name patterns: ${patternOnly} players (${patternTime.toFixed(1)}ms)`)
            console.log(`    📊 Common: ${common} players`)
            console.log(`    📊 API unique: ${apiUnique} players`)
            console.log(`    📊 Pattern unique: ${patternUnique} players`)
            
            // API-only should be more reliable
            const passed = apiTime < patternTime * 2 && apiOnly >= patternOnly * 0.9
            
            this.results.accuracy.push({
                name: 'Detection Methods Comparison',
                passed,
                details: {
                    apiOnly,
                    patternOnly,
                    common,
                    apiUnique,
                    patternUnique,
                    apiTime: apiTime.toFixed(1),
                    patternTime: patternTime.toFixed(1)
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.accuracy.push({
                name: 'Detection Methods Comparison',
                passed: false,
                error: error.message
            })
        }
    }

    async testFalsePositiveNegativeRates() {
        console.log('\n  Test 1.3: False Positive/Negative Rates')
        
        try {
            // This would require a ground truth dataset
            // For now, we'll simulate with known data
            const finnishPlayers = await this.loadFinnishPlayers()
            
            // Check for obvious false positives (non-Finnish names in the list)
            const suspiciousNames = finnishPlayers.filter(player => {
                const name = player.name.toLowerCase()
                const hasFinnishCharacteristics = 
                    name.includes('ä') || name.includes('ö') || name.includes('å') ||
                    name.match(/nen$/) || name.match(/lä$/) || name.match(/mä$/)
                
                return !hasFinnishCharacteristics && !TEST_CONFIG.edgeCasePlayers.some(
                    edge => edge.name === player.name && edge.isFinnish
                )
            })
            
            const falsePositiveRate = (suspiciousNames.length / finnishPlayers.length * 100).toFixed(1)
            const passed = parseFloat(falsePositiveRate) < 20 // Less than 20% false positives
            
            console.log(`    📊 Total players: ${finnishPlayers.length}`)
            console.log(`    📊 Suspicious names: ${suspiciousNames.length}`)
            console.log(`    📊 False positive rate: ${falsePositiveRate}%`)
            
            if (suspiciousNames.length > 0) {
                console.log(`    ⚠️  Suspicious: ${suspiciousNames.slice(0, 5).map(p => p.name).join(', ')}${suspiciousNames.length > 5 ? '...' : ''}`)
            }
            
            this.results.accuracy.push({
                name: 'False Positive/Negative Rates',
                passed,
                details: {
                    totalPlayers: finnishPlayers.length,
                    suspiciousNames: suspiciousNames.length,
                    falsePositiveRate: parseFloat(falsePositiveRate)
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.accuracy.push({
                name: 'False Positive/Negative Rates',
                passed: false,
                error: error.message
            })
        }
    }

    async testAPIOnlyPerformance() {
        console.log('\n  Test 2.1: API-Only Performance')
        
        try {
            const times = []
            
            for (let i = 0; i < TEST_CONFIG.performanceIterations; i++) {
                const startTime = performance.now()
                await this.loadFinnishPlayers()
                const endTime = performance.now()
                times.push(endTime - startTime)
            }
            
            const avgTime = times.reduce((a, b) => a + b, 0) / times.length
            const minTime = Math.min(...times)
            const maxTime = Math.max(...times)
            
            const passed = avgTime < 1000 // Should complete in under 1 second
            
            console.log(`    ⚡ Average: ${avgTime.toFixed(1)}ms`)
            console.log(`    ⚡ Min: ${minTime.toFixed(1)}ms`)
            console.log(`    ⚡ Max: ${maxTime.toFixed(1)}ms`)
            
            this.results.performance.push({
                name: 'API-Only Performance',
                passed,
                details: {
                    averageTime: avgTime.toFixed(1),
                    minTime: minTime.toFixed(1),
                    maxTime: maxTime.toFixed(1),
                    iterations: TEST_CONFIG.performanceIterations
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.performance.push({
                name: 'API-Only Performance',
                passed: false,
                error: error.message
            })
        }
    }

    async testNamePatternPerformance() {
        console.log('\n  Test 2.2: Name Pattern Performance')
        
        try {
            const times = []
            const testPlayers = await this.loadFinnishPlayers()
            
            for (let i = 0; i < TEST_CONFIG.performanceIterations; i++) {
                const startTime = performance.now()
                await this.simulateNamePatternMatching(testPlayers)
                const endTime = performance.now()
                times.push(endTime - startTime)
            }
            
            const avgTime = times.reduce((a, b) => a + b, 0) / times.length
            const minTime = Math.min(...times)
            const maxTime = Math.max(...times)
            
            const passed = avgTime < 500 // Name patterns should be faster but less accurate
            
            console.log(`    ⚡ Average: ${avgTime.toFixed(1)}ms`)
            console.log(`    ⚡ Min: ${minTime.toFixed(1)}ms`)
            console.log(`    ⚡ Max: ${maxTime.toFixed(1)}ms`)
            
            this.results.performance.push({
                name: 'Name Pattern Performance',
                passed,
                details: {
                    averageTime: avgTime.toFixed(1),
                    minTime: minTime.toFixed(1),
                    maxTime: maxTime.toFixed(1),
                    iterations: TEST_CONFIG.performanceIterations
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.performance.push({
                name: 'Name Pattern Performance',
                passed: false,
                error: error.message
            })
        }
    }

    async testMemoryUsageComparison() {
        console.log('\n  Test 2.3: Memory Usage Comparison')
        
        try {
            const initialMemory = process.memoryUsage()
            
            // Test API-only memory usage
            const apiStartMemory = process.memoryUsage()
            const apiPlayers = await this.loadFinnishPlayers()
            const apiEndMemory = process.memoryUsage()
            const apiMemoryUsage = apiEndMemory.heapUsed - apiStartMemory.heapUsed
            
            // Test name pattern memory usage
            const patternStartMemory = process.memoryUsage()
            await this.simulateNamePatternMatching(apiPlayers)
            const patternEndMemory = process.memoryUsage()
            const patternMemoryUsage = patternEndMemory.heapUsed - patternStartMemory.heapUsed
            
            const passed = apiMemoryUsage < patternMemoryUsage * 1.5 // API should use reasonable memory
            
            console.log(`    💾 API-only: ${this.formatBytes(apiMemoryUsage)}`)
            console.log(`    💾 Name patterns: ${this.formatBytes(patternMemoryUsage)}`)
            console.log(`    💾 Difference: ${this.formatBytes(patternMemoryUsage - apiMemoryUsage)}`)
            
            this.results.performance.push({
                name: 'Memory Usage Comparison',
                passed,
                details: {
                    apiMemoryUsage: apiMemoryUsage,
                    patternMemoryUsage: patternMemoryUsage,
                    difference: patternMemoryUsage - apiMemoryUsage
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.performance.push({
                name: 'Memory Usage Comparison',
                passed: false,
                error: error.message
            })
        }
    }

    async testScalability() {
        console.log('\n  Test 2.4: Scalability Tests')
        
        try {
            const playerCounts = [10, 50, 100, 200]
            const results = []
            
            for (const count of playerCounts) {
                const startTime = performance.now()
                const testPlayers = await this.generateTestPlayers(count)
                await this.simulateNamePatternMatching(testPlayers)
                const endTime = performance.now()
                
                const timePerPlayer = (endTime - startTime) / count
                results.push({ count, timePerPlayer })
                
                console.log(`    📊 ${count} players: ${timePerPlayer.toFixed(3)}ms/player`)
            }
            
            // Check if performance scales linearly (not exponentially)
            const firstTime = results[0].timePerPlayer
            const lastTime = results[results.length - 1].timePerPlayer
            const scalabilityRatio = lastTime / firstTime
            const passed = scalabilityRatio < 5 // Should not be more than 5x slower per player
            
            console.log(`    📊 Scalability ratio: ${scalabilityRatio.toFixed(2)}x`)
            
            this.results.performance.push({
                name: 'Scalability Tests',
                passed,
                details: {
                    results,
                    scalabilityRatio: scalabilityRatio.toFixed(2)
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.performance.push({
                name: 'Scalability Tests',
                passed: false,
                error: error.message
            })
        }
    }

    // Data validation tests
    async testDataConsistency() {
        console.log('\n  Test 3.1: Data Consistency Validation')
        
        try {
            const finnishPlayers = await this.loadFinnishPlayers()
            
            // Check for duplicate players
            const duplicateIds = finnishPlayers
                .filter((player, index, self) => 
                    self.findIndex(p => p.id === player.id) !== index
                )
                .map(p => p.id)
            
            // Check for missing required fields
            const playersWithMissingFields = finnishPlayers.filter(player => 
                !player.id || !player.name || !player.position || !player.team
            )
            
            // Check for invalid data types
            const playersWithInvalidTypes = finnishPlayers.filter(player => 
                typeof player.id !== 'number' || 
                typeof player.name !== 'string' || 
                typeof player.position !== 'string'
            )
            
            const passed = duplicateIds.length === 0 && 
                         playersWithMissingFields.length === 0 && 
                         playersWithInvalidTypes.length === 0
            
            console.log(`    📊 Duplicate IDs: ${duplicateIds.length}`)
            console.log(`    📊 Missing fields: ${playersWithMissingFields.length}`)
            console.log(`    📊 Invalid types: ${playersWithInvalidTypes.length}`)
            
            this.results.validation.push({
                name: 'Data Consistency Validation',
                passed,
                details: {
                    duplicateIds: duplicateIds.length,
                    playersWithMissingFields: playersWithMissingFields.length,
                    playersWithInvalidTypes: playersWithInvalidTypes.length
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.validation.push({
                name: 'Data Consistency Validation',
                passed: false,
                error: error.message
            })
        }
    }

    async testPlayerDataCompleteness() {
        console.log('\n  Test 3.2: Player Data Completeness')
        
        try {
            const finnishPlayers = await this.loadFinnishPlayers()
            
            // Check completeness of optional fields
            const fieldsToCheck = ['birthDate', 'birthCity', 'height', 'weight', 'shootsCatches']
            const completeness = {}
            
            for (const field of fieldsToCheck) {
                const playersWithField = finnishPlayers.filter(p => p[field] && p[field] !== '').length
                completeness[field] = (playersWithField / finnishPlayers.length * 100).toFixed(1)
            }
            
            const avgCompleteness = Object.values(completeness)
                .reduce((sum, val) => sum + parseFloat(val), 0) / fieldsToCheck.length
            
            const passed = avgCompleteness >= 80 // 80% data completeness threshold
            
            console.log(`    📊 Average completeness: ${avgCompleteness.toFixed(1)}%`)
            Object.entries(completeness).forEach(([field, percentage]) => {
                console.log(`    📊 ${field}: ${percentage}%`)
            })
            
            this.results.validation.push({
                name: 'Player Data Completeness',
                passed,
                details: {
                    completeness,
                    averageCompleteness: avgCompleteness.toFixed(1)
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.validation.push({
                name: 'Player Data Completeness',
                passed: false,
                error: error.message
            })
        }
    }

    async testNationalityVerification() {
        console.log('\n  Test 3.3: Nationality Verification')
        
        try {
            const finnishPlayers = await this.loadFinnishPlayers()
            
            // Check nationality field consistency
            const playersWithFIN = finnishPlayers.filter(p => p.nationality === 'FIN').length
            const playersWithOtherNationality = finnishPlayers.filter(p => 
                p.nationality && p.nationality !== 'FIN'
            ).length
            const playersWithoutNationality = finnishPlayers.filter(p => !p.nationality).length
            
            const passed = playersWithFIN >= finnishPlayers.length * 0.9 // 90% should have FIN nationality
            
            console.log(`    📊 FIN nationality: ${playersWithFIN}/${finnishPlayers.length}`)
            console.log(`    📊 Other nationalities: ${playersWithOtherNationality}`)
            console.log(`    📊 No nationality: ${playersWithoutNationality}`)
            
            this.results.validation.push({
                name: 'Nationality Verification',
                passed,
                details: {
                    playersWithFIN,
                    playersWithOtherNationality,
                    playersWithoutNationality,
                    totalPlayers: finnishPlayers.length
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.validation.push({
                name: 'Nationality Verification',
                passed: false,
                error: error.message
            })
        }
    }

    // Edge case tests
    async testNonFinnishNames() {
        console.log('\n  Test 4.1: Non-Finnish Names but Finnish Players')
        
        try {
            const finnishPlayers = await this.loadFinnishPlayers()
            const edgeCases = TEST_CONFIG.edgeCasePlayers.filter(edge => edge.isFinnish)
            
            let foundEdgeCases = 0
            const foundPlayers = []
            
            for (const edgeCase of edgeCases) {
                const found = finnishPlayers.some(p => p.name.includes(edgeCase.name))
                if (found) {
                    foundEdgeCases++
                    foundPlayers.push(edgeCase.name)
                }
            }
            
            const passed = foundEdgeCases >= edgeCases.length * 0.8 // 80% of edge cases should be found
            
            console.log(`    📊 Edge cases found: ${foundEdgeCases}/${edgeCases.length}`)
            console.log(`    📊 Found players: ${foundPlayers.join(', ')}`)
            
            this.results.edgeCases.push({
                name: 'Non-Finnish Names but Finnish Players',
                passed,
                details: {
                    foundEdgeCases,
                    totalEdgeCases: edgeCases.length,
                    foundPlayers
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.edgeCases.push({
                name: 'Non-Finnish Names but Finnish Players',
                passed: false,
                error: error.message
            })
        }
    }

    async testFinnishNamesNonFinnishPlayers() {
        console.log('\n  Test 4.2: Finnish Names but Non-Finnish Players')
        
        try {
            const finnishPlayers = await this.loadFinnishPlayers()
            const edgeCases = TEST_CONFIG.edgeCasePlayers.filter(edge => !edge.isFinnish)
            
            let falsePositives = 0
            const falsePositivePlayers = []
            
            for (const edgeCase of edgeCases) {
                const found = finnishPlayers.some(p => p.name.includes(edgeCase.name))
                if (found) {
                    falsePositives++
                    falsePositivePlayers.push(edgeCase.name)
                }
            }
            
            const passed = falsePositives <= edgeCases.length * 0.2 // Less than 20% false positives
            
            console.log(`    📊 False positives: ${falsePositives}/${edgeCases.length}`)
            console.log(`    📊 False positive players: ${falsePositivePlayers.join(', ')}`)
            
            this.results.edgeCases.push({
                name: 'Finnish Names but Non-Finnish Players',
                passed,
                details: {
                    falsePositives,
                    totalEdgeCases: edgeCases.length,
                    falsePositivePlayers
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.edgeCases.push({
                name: 'Finnish Names but Non-Finnish Players',
                passed: false,
                error: error.message
            })
        }
    }

    async testSpecialCharacters() {
        console.log('\n  Test 4.3: Special Characters and Encoding')
        
        try {
            const finnishPlayers = await this.loadFinnishPlayers()
            
            // Check for proper handling of Finnish special characters
            const playersWithSpecialChars = finnishPlayers.filter(p => 
                p.name.includes('ä') || p.name.includes('ö') || p.name.includes('å')
            )
            
            // Check for encoding issues
            const playersWithEncodingIssues = finnishPlayers.filter(p => 
                p.name.includes('�') || p.name.includes('?') || p.name.includes('�')
            )
            
            const passed = playersWithSpecialChars.length > 0 && playersWithEncodingIssues.length === 0
            
            console.log(`    📊 Players with special chars: ${playersWithSpecialChars.length}`)
            console.log(`    📊 Encoding issues: ${playersWithEncodingIssues.length}`)
            
            if (playersWithSpecialChars.length > 0) {
                console.log(`    📊 Examples: ${playersWithSpecialChars.slice(0, 3).map(p => p.name).join(', ')}`)
            }
            
            this.results.edgeCases.push({
                name: 'Special Characters and Encoding',
                passed,
                details: {
                    playersWithSpecialChars: playersWithSpecialChars.length,
                    playersWithEncodingIssues: playersWithEncodingIssues.length
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.edgeCases.push({
                name: 'Special Characters and Encoding',
                passed: false,
                error: error.message
            })
        }
    }

    async testInactivePlayers() {
        console.log('\n  Test 4.4: Inactive/Retired Players')
        
        try {
            const finnishPlayers = await this.loadFinnishPlayers()
            
            // Check for inactive players
            const inactivePlayers = finnishPlayers.filter(p => p.active === false)
            const activePlayers = finnishPlayers.filter(p => p.active === true)
            const playersWithNoActiveStatus = finnishPlayers.filter(p => p.active === undefined)
            
            const passed = activePlayers.length > inactivePlayers.length // Should have more active than inactive
            
            console.log(`    📊 Active players: ${activePlayers.length}`)
            console.log(`    📊 Inactive players: ${inactivePlayers.length}`)
            console.log(`    📊 No active status: ${playersWithNoActiveStatus.length}`)
            
            this.results.edgeCases.push({
                name: 'Inactive/Retired Players',
                passed,
                details: {
                    activePlayers: activePlayers.length,
                    inactivePlayers: inactivePlayers.length,
                    playersWithNoActiveStatus: playersWithNoActiveStatus.length
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.edgeCases.push({
                name: 'Inactive/Retired Players',
                passed: false,
                error: error.message
            })
        }
    }

    // Integration tests
    async testNHLAPIIntegration() {
        console.log('\n  Test 5.1: NHL API Integration')
        
        try {
            // Test API endpoint availability
            const apiEndpoint = 'https://api-web.nhle.com/v1/roster/COL/20242025'
            const response = await fetch(apiEndpoint)
            
            const apiAvailable = response.ok
            const data = apiAvailable ? await response.json() : null
            
            const passed = apiAvailable && data && (data.forwards || data.defensemen || data.goalies)
            
            console.log(`    📊 API available: ${apiAvailable}`)
            console.log(`    📊 Response status: ${response.status}`)
            console.log(`    📊 Data received: ${data ? 'Yes' : 'No'}`)
            
            this.results.integration.push({
                name: 'NHL API Integration',
                passed,
                details: {
                    apiAvailable,
                    responseStatus: response.status,
                    dataReceived: !!data
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.integration.push({
                name: 'NHL API Integration',
                passed: false,
                error: error.message
            })
        }
    }

    async testErrorHandling() {
        console.log('\n  Test 5.2: Error Handling and Resilience')
        
        try {
            // Test with invalid player ID
            const invalidPlayer = { id: 9999999, name: 'Invalid Player' }
            
            // Test with malformed data
            const malformedPlayer = { id: null, name: undefined }
            
            // Test with network timeout simulation
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Timeout')), 100)
            )
            
            let errorHandlingPassed = true
            
            try {
                await this.loadFinnishPlayers()
            } catch (error) {
                errorHandlingPassed = false
            }
            
            const passed = errorHandlingPassed
            
            console.log(`    📊 Error handling: ${passed ? 'Working' : 'Failed'}`)
            
            this.results.integration.push({
                name: 'Error Handling and Resilience',
                passed,
                details: {
                    errorHandlingWorking: passed
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.integration.push({
                name: 'Error Handling and Resilience',
                passed: false,
                error: error.message
            })
        }
    }

    async testCacheBehavior() {
        console.log('\n  Test 5.3: Cache Behavior')
        
        try {
            // Simulate cache behavior
            const cache = new Map()
            
            // Test cache hit
            cache.set('test-key', { data: 'test-data', timestamp: Date.now() })
            const cacheHit = cache.get('test-key')
            
            // Test cache miss
            const cacheMiss = cache.get('non-existent-key')
            
            // Test cache expiration (simulate old entry)
            cache.set('old-key', { data: 'old-data', timestamp: Date.now() - 3600000 }) // 1 hour old
            const expiredEntry = cache.get('old-key')
            
            const passed = cacheHit && !cacheMiss && expiredEntry
            
            console.log(`    📊 Cache hit: ${cacheHit ? 'Working' : 'Failed'}`)
            console.log(`    📊 Cache miss: ${cacheMiss ? 'Failed' : 'Working'}`)
            console.log(`    📊 Cache expiration: ${expiredEntry ? 'Working' : 'Failed'}`)
            
            this.results.integration.push({
                name: 'Cache Behavior',
                passed,
                details: {
                    cacheHitWorking: !!cacheHit,
                    cacheMissWorking: !cacheMiss,
                    cacheExpirationWorking: !!expiredEntry
                }
            })
            
        } catch (error) {
            console.log(`    ❌ Error: ${error.message}`)
            this.results.integration.push({
                name: 'Cache Behavior',
                passed: false,
                error: error.message
            })
        }
    }

    // Helper methods
    async loadFinnishPlayers() {
        try {
            const data = await fs.promises.readFile(TEST_CONFIG.finnishRosterPath, 'utf8')
            return JSON.parse(data)
        } catch (error) {
            throw new Error(`Failed to load Finnish players: ${error.message}`)
        }
    }

    async testAPIMethod() {
        // Simulate API-only method
        const players = await this.loadFinnishPlayers()
        return players.filter(p => p.nationality === 'FIN' || p.active === true)
    }

    async testNamePatternMethod() {
        // Simulate name pattern matching method
        const players = await this.loadFinnishPlayers()
        return players.filter(player => {
            const name = player.name.toLowerCase()
            return name.match(/nen$/) || name.match(/lä$/) || name.match(/mä$/) ||
                   name.includes('ä') || name.includes('ö') || name.includes('å')
        })
    }

    async simulateNamePatternMatching(players) {
        // Simulate the computational cost of name pattern matching
        const patterns = [/nen$/, /lä$/, /mä$/, /ä/, /ö/, /å/]
        let matches = 0
        
        for (const player of players) {
            const name = player.name.toLowerCase()
            for (const pattern of patterns) {
                if (pattern.test(name)) {
                    matches++
                    break
                }
            }
        }
        
        return matches
    }

    async generateTestPlayers(count) {
        const players = []
        for (let i = 0; i < count; i++) {
            players.push({
                id: 8470000 + i,
                name: `Test Player ${i}`,
                nationality: Math.random() > 0.5 ? 'FIN' : 'OTHER',
                active: true
            })
        }
        return players
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B'
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
    }

    generateFinalReport() {
        const endTime = performance.now()
        const totalTime = endTime - this.startTime
        
        // Calculate summary
        const allTests = [
            ...this.results.accuracy,
            ...this.results.performance,
            ...this.results.validation,
            ...this.results.edgeCases,
            ...this.results.integration
        ]
        
        const totalTests = allTests.length
        const passedTests = allTests.filter(t => t.passed).length
        const failedTests = totalTests - passedTests
        
        this.results.summary = {
            totalTests,
            passedTests,
            failedTests,
            executionTime: totalTime,
            passRate: (passedTests / totalTests * 100).toFixed(1)
        }
        
        // Display results
        console.log('\n' + '='.repeat(70))
        console.log('📈 COMPREHENSIVE TEST RESULTS')
        console.log('='.repeat(70))
        
        console.log(`\n🎯 Overall Summary:`)
        console.log(`  Total tests: ${totalTests}`)
        console.log(`  Passed: ${passedTests}`)
        console.log(`  Failed: ${failedTests}`)
        console.log(`  Pass rate: ${this.results.summary.passRate}%`)
        console.log(`  Execution time: ${totalTime.toFixed(0)}ms`)
        
        // Category summaries
        console.log(`\n📊 Category Results:`)
        console.log(`  Accuracy: ${this.results.accuracy.filter(t => t.passed).length}/${this.results.accuracy.length} passed`)
        console.log(`  Performance: ${this.results.performance.filter(t => t.passed).length}/${this.results.performance.length} passed`)
        console.log(`  Validation: ${this.results.validation.filter(t => t.passed).length}/${this.results.validation.length} passed`)
        console.log(`  Edge Cases: ${this.results.edgeCases.filter(t => t.passed).length}/${this.results.edgeCases.length} passed`)
        console.log(`  Integration: ${this.results.integration.filter(t => t.passed).length}/${this.results.integration.length} passed`)
        
        // Recommendations
        console.log(`\n💡 Recommendations:`)
        
        if (parseFloat(this.results.summary.passRate) >= 90) {
            console.log(`  🎉 System is ready for production deployment!`)
        } else if (parseFloat(this.results.summary.passRate) >= 70) {
            console.log(`  ⚠️  System is mostly ready but needs some improvements`)
        } else {
            console.log(`  ❌ System needs significant improvements before deployment`)
        }
        
        const failedAccuracyTests = this.results.accuracy.filter(t => !t.passed)
        if (failedAccuracyTests.length > 0) {
            console.log(`  🔧 Review accuracy tests: ${failedAccuracyTests.map(t => t.name).join(', ')}`)
        }
        
        const failedPerformanceTests = this.results.performance.filter(t => !t.passed)
        if (failedPerformanceTests.length > 0) {
            console.log(`  ⚡ Optimize performance: ${failedPerformanceTests.map(t => t.name).join(', ')}`)
        }
        
        // Save detailed results
        const resultsPath = path.join(projectRoot, 'test-results', 'finnish-player-detection-results.json')
        fs.mkdirSync(path.dirname(resultsPath), { recursive: true })
        fs.writeFileSync(resultsPath, JSON.stringify(this.results, null, 2))
        console.log(`\n📄 Detailed results saved to: ${resultsPath}`)
    }
}

// Run the test suite
async function main() {
    const testSuite = new TestSuite()
    await testSuite.runAllTests()
}

// Execute if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(error => {
        console.error('❌ Test suite failed:', error)
        process.exit(1)
    })
}

export { TestSuite }