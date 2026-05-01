import { describe, expect, it } from 'vitest'
import { GET } from '../../../routes/api/finnish-players/+server.js'

describe('/api/finnish-players route', () => {
    it('preserves inactive roster players in the full response', async () => {
        const event = {
            url: new URL('http://localhost/api/finnish-players'),
        }
        const response = await GET(/** @type {any} */ (event))

        expect(response.status).toBe(200)

        /** @type {Array<{ name: string, is_active: boolean }>} */
        const players = await response.json()
        const inactivePlayer = players.find((player) => player.name === 'Timo Blomqvist')

        expect(inactivePlayer).toBeDefined()
        if (!inactivePlayer) throw new Error('Inactive test player missing from roster response')
        expect(inactivePlayer.is_active).toBe(false)
    })
})
