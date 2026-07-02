import { readFile } from 'node:fs/promises'
import { join } from 'node:path'

export function getOffseasonMovesPath() {
    return join(process.cwd(), 'static', 'data', 'offseason-moves.json')
}

export async function loadOffseasonMovesFromDisk() {
    try {
        const content = await readFile(getOffseasonMovesPath(), 'utf-8')
        return JSON.parse(content)
    } catch (error) {
        const code =
            typeof error === 'object' && error !== null && 'code' in error ? error.code : undefined
        if (code !== 'ENOENT') {
            console.warn('Could not load offseason moves:', error)
        }
        return null
    }
}
