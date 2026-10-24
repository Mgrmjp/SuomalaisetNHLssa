import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { runInNewContext } from 'node:vm'
import { afterEach, expect, it } from 'vitest'

/** @type {string[]} */
const tempDirs = []
const nodeRequire = createRequire(import.meta.url)
afterEach(() => {
    for (const dir of tempDirs) rmSync(dir, { recursive: true, force: true })
    tempDirs.length = 0
})

it('preserves cached stats and their collection time when the API returns malformed data', async () => {
    const root = mkdtempSync(join(tmpdir(), 'stats-prebuild-'))
    tempDirs.push(root)
    const statsDir = join(root, 'static/data/player-stats')
    mkdirSync(statsDir, { recursive: true })
    const cachedSkaters = [{ playerId: 1, skaterFullName: 'Finn Player', points: 10 }]
    writeFileSync(join(statsDir, 'skaters-20262027.json'), JSON.stringify(cachedSkaters))
    writeFileSync(
        join(statsDir, 'metadata.json'),
        JSON.stringify({
            seasonId: '20262027',
            updatedAt: '2026-10-01T12:00:00.000Z',
        })
    )

    /** @type {{ exports: { main?: () => Promise<void> } }} */
    const module = { exports: {} }
    /** @type {{ message?: string, data?: unknown[] }} */
    let skaterPayload = { message: 'unexpected response' }
    const source = readFileSync(
        join(process.cwd(), 'scripts/prebuild/fetch-player-stats.cjs'),
        'utf8'
    )
    runInNewContext(source, {
        module,
        require: (/** @type {string} */ name) => requireNodeModule(name),
        process: { cwd: () => root, env: { NHL_SEASON_ID: '20262027', NHL_API_MAX_RETRIES: '0' } },
        fetch: async (/** @type {string} */ url) => ({
            ok: true,
            json: async () =>
                url.includes('/skater/') && url.includes('gameTypeId%3D2')
                    ? skaterPayload
                    : { data: [] },
        }),
        console: { log() {}, warn() {}, error() {} },
        Date,
        setTimeout,
    })

    if (!module.exports.main) throw new Error('Prebuild main was not exported')
    await module.exports.main()

    expect(JSON.parse(readFileSync(join(statsDir, 'skaters-20262027.json'), 'utf8'))).toEqual(
        cachedSkaters
    )
    const metadata = JSON.parse(readFileSync(join(statsDir, 'metadata.json'), 'utf8'))
    expect(metadata.skatersUpdatedAt).toBe('2026-10-01T12:00:00.000Z')
    expect(metadata.updatedAt).toBe('2026-10-01T12:00:00.000Z')

    skaterPayload = { data: [] }
    await module.exports.main()
    expect(JSON.parse(readFileSync(join(statsDir, 'skaters-20262027.json'), 'utf8'))).toEqual(
        cachedSkaters
    )
    expect(JSON.parse(readFileSync(join(statsDir, 'metadata.json'), 'utf8')).skatersUpdatedAt).toBe(
        '2026-10-01T12:00:00.000Z'
    )
})

/** @param {string} name */
function requireNodeModule(name) {
    if (name === 'fs') return nodeRequire('node:fs')
    if (name === 'path') return nodeRequire('node:path')
    throw new Error(`Unexpected require: ${name}`)
}
