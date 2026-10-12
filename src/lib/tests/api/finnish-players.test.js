// @ts-nocheck
/**
 * Finnish Players API Tests
 * Exercises the real /api/finnish-players GET handler against an isolated
 * filesystem sandbox, so assertions cover the production response format
 * without mocking the handler or the node:fs module graph.
 */

import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { GET } from '../../../routes/api/finnish-players/+server.js'

const originalCwd = process.cwd()

/** Roster record in the cache format produced by the Python pipeline. */
const cacheFormatRoster = {
    8477476: {
        playerId: 8477476,
        name: 'Sebastian Aho',
        position: 'C',
        teamAbbrev: 'CAR',
        sweaterNumber: 20,
        shootsCatches: 'L',
        heightInches: 71,
        weightLbs: 182,
        birthDate: '1997-07-26',
        birthCity: { default: 'Rauma' },
        birthCountry: 'FIN',
        draftYear: 2015,
        draftRound: 2,
        draftOverall: 35,
        isRookie: false,
        isActive: true,
        headshot: 'https://assets.nhle.com/mugs/nhl/20252026/CAR/8477476.png',
    },
    8478483: {
        playerId: 8478483,
        name: 'Mikko Rantanen',
        position: 'R',
        teamAbbrev: 'DAL',
        sweaterNumber: 96,
        isActive: false,
        gamesPlayed: 82,
        lastTeam: 'COL',
        headshot: 'https://assets.nhle.com/mugs/nhl/20252026/DAL/8478483.png',
    },
}

/** Legacy array format, used by a few older snapshots. */
const arrayFormatRoster = [
    {
        id: 8477476,
        name: 'Sebastian Aho',
        position: 'C',
        team: 'CAR',
        is_active: true,
    },
]

let sandbox

/**
 * Point the handler's process.cwd()-based lookup at a sandbox directory and
 * write the given roster content (or nothing at all for the missing case).
 */
function serveRoster(content) {
    sandbox = fs.mkdtempSync(path.join(os.tmpdir(), 'finnish-players-api-'))
    if (content !== undefined) {
        const playersDir = path.join(sandbox, 'static', 'data', 'players')
        fs.mkdirSync(playersDir, { recursive: true })
        fs.writeFileSync(
            path.join(playersDir, 'finnish-roster.json'),
            typeof content === 'string' ? content : JSON.stringify(content)
        )
    }
    process.chdir(sandbox)
}

function requestFor(query = '') {
    return GET({ url: new URL(`http://localhost/api/finnish-players${query}`) })
}

describe('GET /api/finnish-players (real handler)', () => {
    beforeEach(() => {
        sandbox = null
    })

    afterEach(() => {
        process.chdir(originalCwd)
        if (sandbox) fs.rmSync(sandbox, { recursive: true, force: true })
    })

    describe('full format (default)', () => {
        it('returns a bare array of players, not a success envelope', async () => {
            serveRoster(cacheFormatRoster)
            const response = await requestFor()

            expect(response.status).toBe(200)
            const data = await response.json()
            expect(Array.isArray(data)).toBe(true)
            expect(data).toHaveLength(2)
        })

        it('maps cache aliases to the serialized response contract', async () => {
            serveRoster(cacheFormatRoster)
            const data = await (await requestFor()).json()
            const aho = data.find((player) => player.name === 'Sebastian Aho')

            expect(aho).toMatchObject({
                id: 8477476,
                name: 'Sebastian Aho',
                position: 'C',
                team: 'CAR',
                team_abbrev: 'CAR',
                jersey_number: 20,
                shoots_catches: 'L',
                height: 71,
                weight: 182,
                birth_date: '1997-07-26',
                birth_city: 'Rauma',
                birth_country: 'FIN',
                draft_year: 2015,
                draft_round: 2,
                draft_overall: 35,
                is_rookie: false,
                is_active: true,
            })
        })

        it('preserves explicit inactive flags and keeps active default true', async () => {
            serveRoster(cacheFormatRoster)
            const data = await (await requestFor()).json()

            const active = data.find((player) => player.name === 'Sebastian Aho')
            const inactive = data.find((player) => player.name === 'Mikko Rantanen')
            expect(active.is_active).toBe(true)
            expect(inactive.is_active).toBe(false)
        })

        it('supports the legacy array roster format', async () => {
            serveRoster(arrayFormatRoster)
            const response = await requestFor()
            const data = await response.json()

            expect(response.status).toBe(200)
            expect(data).toEqual([
                expect.objectContaining({
                    id: 8477476,
                    name: 'Sebastian Aho',
                    team: 'CAR',
                    is_active: true,
                }),
            ])
        })
    })

    describe('format parameter', () => {
        beforeEach(() => {
            serveRoster(cacheFormatRoster)
        })

        it('simple format returns a name-to-position mapping', async () => {
            const data = await (await requestFor('?format=simple')).json()

            expect(data).toEqual({
                'Sebastian Aho': 'C',
                'Mikko Rantanen': 'R',
            })
        })

        it('names format returns an array of names', async () => {
            const data = await (await requestFor('?format=names')).json()

            expect(data).toEqual(['Sebastian Aho', 'Mikko Rantanen'])
        })

        it('falls back to full format for unknown or dangerous values', async () => {
            for (const value of ['invalid', 'full;rm', '../../etc']) {
                const response = await requestFor(`?format=${encodeURIComponent(value)}`)
                expect(response.status).toBe(200)
                expect(Array.isArray(await response.json())).toBe(true)
            }
        })
    })

    describe('filesystem and data errors', () => {
        it('returns an empty array when the roster file is missing', async () => {
            serveRoster()
            const response = await requestFor()

            expect(response.status).toBe(200)
            expect(await response.json()).toEqual([])
        })

        it('returns an empty array when the roster file is malformed JSON', async () => {
            serveRoster('{not json')
            const response = await requestFor()

            expect(response.status).toBe(200)
            expect(await response.json()).toEqual([])
        })

        it('returns an empty array when the roster is empty', async () => {
            serveRoster({})
            const response = await requestFor()

            expect(response.status).toBe(200)
            expect(await response.json()).toEqual([])
        })
    })

    describe('normalization rules', () => {
        it('infers the team from the headshot URL when no team field exists', async () => {
            serveRoster({
                8477476: {
                    playerId: 8477476,
                    name: 'Kaapo Kakko',
                    position: 'R',
                    headshot: 'https://assets.nhle.com/mugs/nhl/20252026/SEA/8477476.png',
                },
            })
            const data = await (await requestFor()).json()

            expect(data[0].team).toBe('SEA')
            expect(data[0].team_abbrev).toBe('SEA')
        })

        it('keeps zero-valued and explicit-false fields intact', async () => {
            serveRoster({
                8477476: {
                    playerId: 8477476,
                    name: 'Zero Stats',
                    position: 'C',
                    teamAbbrev: 'CAR',
                    draftRound: 0,
                    isRookie: false,
                    isActive: false,
                    gamesPlayed: 0,
                },
            })
            const data = await (await requestFor()).json()

            expect(data[0]).toMatchObject({
                draft_round: 0,
                is_rookie: false,
                is_active: false,
            })
        })
    })

    describe('response basics', () => {
        it('includes cache headers', async () => {
            serveRoster(cacheFormatRoster)
            const response = await requestFor()

            expect(response.headers.get('Cache-Control')).toBeDefined()
        })

        it('handles concurrent requests consistently', async () => {
            serveRoster(cacheFormatRoster)
            const responses = await Promise.all([requestFor(), requestFor(), requestFor()])
            const payloads = await Promise.all(responses.map((response) => response.json()))

            for (const data of payloads) {
                expect(Array.isArray(data)).toBe(true)
                expect(data).toHaveLength(2)
            }
        })
    })
})
