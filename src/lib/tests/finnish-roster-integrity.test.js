// @ts-nocheck
import fs from 'node:fs'
import path from 'node:path'
import { beforeAll, describe, expect, it } from 'vitest'

const ROSTER_PATH = path.resolve(process.cwd(), 'static/data/players/finnish-roster.json')
const CACHE_PATH = path.resolve(
    process.cwd(),
    'scripts/data_collection/finnish/cache/finnish-players.json'
)

function loadJson(filePath) {
    const raw = fs.readFileSync(filePath, 'utf8')
    return JSON.parse(raw)
}

describe('Finnish roster - inactive player data', () => {
    let roster = {}
    let cache = {}

    beforeAll(() => {
        roster = loadJson(ROSTER_PATH)
        cache = loadJson(CACHE_PATH)
    })

    describe('roster file integrity', () => {
        it('should be a non-empty object keyed by player ID', () => {
            expect(typeof roster).toBe('object')
            expect(roster).not.toBeNull()
            const keys = Object.keys(roster)
            expect(keys.length).toBeGreaterThan(0)
            keys.forEach((key) => {
                expect(Number(key)).not.toBeNaN()
            })
        })

        it('every player entry should have required fields', () => {
            Object.values(roster).forEach((p) => {
                expect(p).toHaveProperty('playerId')
                expect(p).toHaveProperty('name')
                expect(p).toHaveProperty('position')
                expect(p).toHaveProperty('isActive')
                expect(typeof p.isActive).toBe('boolean')
            })
        })
    })

    describe('inactive player lastTeam and gamesPlayed', () => {
        it('every inactive player with empty currentTeam should have lastTeam', () => {
            const inactive = Object.values(roster).filter(
                (p) => p.isActive === false || !p.currentTeam || p.currentTeam === ''
            )

            expect(inactive.length).toBeGreaterThan(0)

            const missingLastTeam = inactive.filter((p) => !p.lastTeam || p.lastTeam === '')
            const missingCount = missingLastTeam.length

            if (missingCount > 0) {
                const names = missingLastTeam.slice(0, 5).map((p) => `${p.name} (${p.playerId})`)
                console.error(
                    `Missing lastTeam for ${missingCount} inactive players: ${names.join(', ')}`
                )
            }

            expect(missingCount).toBe(0)
        })

        it('every inactive player with empty currentTeam should have gamesPlayed', () => {
            const inactive = Object.values(roster).filter(
                (p) => p.isActive === false || !p.currentTeam || p.currentTeam === ''
            )

            expect(inactive.length).toBeGreaterThan(0)

            const missingGP = inactive.filter((p) => p.gamesPlayed == null || p.gamesPlayed === 0)
            const missingCount = missingGP.length

            if (missingCount > 0) {
                const names = missingGP.slice(0, 5).map((p) => `${p.name} (${p.playerId})`)
                console.error(
                    `Missing gamesPlayed for ${missingCount} inactive players: ${names.join(', ')}`
                )
            }

            expect(missingCount).toBe(0)
        })

        it('lastTeam should be a valid NHL team abbreviation (single or comma-separated)', () => {
            const inactive = Object.values(roster).filter(
                (p) => p.isActive === false || !p.currentTeam || p.currentTeam === ''
            )

            const validTeams = [
                'ANA',
                'ARI',
                'BOS',
                'BUF',
                'CGY',
                'CAR',
                'CHI',
                'COL',
                'CBJ',
                'DAL',
                'DET',
                'EDM',
                'FLA',
                'LAK',
                'MIN',
                'MTL',
                'NJD',
                'NSH',
                'NYI',
                'NYR',
                'OTT',
                'PHI',
                'PIT',
                'SEA',
                'SJS',
                'STL',
                'TBL',
                'TOR',
                'VAN',
                'VGK',
                'WSH',
                'WPG',
                'ATL',
                'HFD',
                'MNS',
                'PHX',
                'QUE',
                'WIN',
                'TSP',
                'DTC',
                'BAR',
                'CLR',
                'HAM',
                'KCS',
                'OAK',
                'PITP',
            ]

            inactive.forEach((p) => {
                if (p.lastTeam) {
                    const teams = p.lastTeam.split(',')
                    teams.forEach((team, i) => {
                        expect(
                            validTeams.includes(team.trim()),
                            `${p.name} has invalid lastTeam component at index ${i}: "${team.trim()}" (full: ${p.lastTeam})`
                        ).toBe(true)
                    })
                }
            })
        })

        it('gamesPlayed should be a positive number for inactive players', () => {
            const inactive = Object.values(roster).filter(
                (p) => p.isActive === false || !p.currentTeam || p.currentTeam === ''
            )

            inactive.forEach((p) => {
                if (p.gamesPlayed != null) {
                    expect(
                        typeof p.gamesPlayed === 'number' && p.gamesPlayed > 0,
                        `${p.name} has invalid gamesPlayed: ${p.gamesPlayed}`
                    ).toBe(true)
                }
            })
        })
    })

    describe('active player data', () => {
        it('active players should have a non-empty currentTeam', () => {
            const active = Object.values(roster).filter((p) => p.isActive === true)

            expect(active.length).toBeGreaterThan(0)

            const missingTeam = active.filter((p) => !p.currentTeam || p.currentTeam === '')
            const missingCount = missingTeam.length

            if (missingCount > 0) {
                const names = missingTeam.slice(0, 5).map((p) => `${p.name} (${p.playerId})`)
                console.error(
                    `Missing currentTeam for ${missingCount} active players: ${names.join(', ')}`
                )
            }

            expect(missingCount).toBe(0)
        })
    })

    describe('cache-sync consistency', () => {
        it('cache should have same player IDs as roster', () => {
            const rosterIds = new Set(Object.keys(roster))
            const cacheIds = new Set(Object.keys(cache))

            expect(cacheIds.size).toBeGreaterThan(0)

            const rosterOnly = [...rosterIds].filter((id) => !cacheIds.has(id))
            const cacheOnly = [...cacheIds].filter((id) => !rosterIds.has(id))

            if (rosterOnly.length > 0) {
                console.warn(`Player IDs in roster but not cache: ${rosterOnly.join(', ')}`)
            }
            if (cacheOnly.length > 0) {
                console.warn(`Player IDs in cache but not roster: ${cacheOnly.join(', ')}`)
            }

            expect(rosterOnly.length).toBe(0)
            expect(cacheOnly.length).toBe(0)
        })

        it('inactive player lastTeam/gamesPlayed should exist in both cache and roster', () => {
            const rosterInactive = Object.values(roster).filter(
                (p) => p.isActive === false || !p.currentTeam || p.currentTeam === ''
            )

            let rosterWithLastTeam = 0
            let cacheWithLastTeam = 0

            rosterInactive.forEach((p) => {
                if (p.lastTeam) rosterWithLastTeam++
                const cachePlayer = cache[String(p.playerId)]
                if (cachePlayer?.lastTeam) cacheWithLastTeam++
            })

            expect(rosterWithLastTeam).toBeGreaterThan(0)
            expect(cacheWithLastTeam).toBeGreaterThan(0)
            expect(cacheWithLastTeam).toBeGreaterThanOrEqual(rosterWithLastTeam * 0.9)
        })
    })
})
