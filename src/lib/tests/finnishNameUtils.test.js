import { afterEach, expect, it, vi } from 'vitest'
import { correctFullName, correctFullNameWithLLM } from '../utils/finnishNameUtils.js'

afterEach(() => vi.unstubAllGlobals())

it.each(['Matias Maccelli', 'Matias Mäccelli'])('uses the verified spelling for %s', (name) => {
    expect(correctFullName(name)).toBe('Matias Maccelli')
})

it('applies verified spellings after an incorrect AI response', async () => {
    vi.stubGlobal(
        'fetch',
        vi.fn(async () => ({
            ok: true,
            json: async () => ({ choices: [{ message: { content: 'Matias Mäccelli' } }] }),
        }))
    )
    expect(await correctFullNameWithLLM('Matias Maccelli', 'test-key')).toBe('Matias Maccelli')
})
