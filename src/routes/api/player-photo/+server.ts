import { json } from '@sveltejs/kit'

interface PlayerPhotoData {
    playerId: number
    headshotUrl: string | null
    fallbackUrl: string
}

const FETCH_TIMEOUT_MS = 5000
const PLAYER_ID_PATTERN = /^\d{1,10}$/
const TRUSTED_IMAGE_HOSTS = new Set([
    'assets.nhle.com',
    'cms.nhl.bamgrid.com',
    'nhl.bamcontent.com',
])

function parsePlayerId(value: string | null): number | null {
    if (!value || !PLAYER_ID_PATTERN.test(value)) return null

    const playerId = Number(value)
    return Number.isSafeInteger(playerId) && playerId > 0 ? playerId : null
}

function getTrustedImageUrl(value: unknown): string | null {
    if (!value || typeof value !== 'string') return null

    try {
        const url = new URL(value)
        if (url.protocol !== 'https:' || !TRUSTED_IMAGE_HOSTS.has(url.hostname)) {
            return null
        }

        return url.toString()
    } catch {
        return null
    }
}

/**
 * Get player photo/headshot from NHL API
 * @param {number} playerId - NHL player ID
 * @returns {Promise<PlayerPhotoData | null>} Player photo data or null
 */
async function getPlayerPhoto(playerId: number): Promise<PlayerPhotoData | null> {
    try {
        // First try to get player landing data which includes headshot
        const url = `https://api-web.nhle.com/v1/player/${playerId}/landing`
        const response = await fetch(url, { signal: AbortSignal.timeout(FETCH_TIMEOUT_MS) })

        if (!response.ok) {
            console.warn(`Failed to fetch player photo for ${playerId}: ${response.status}`)
            return null
        }

        const data = await response.json()

        // Extract headshot URL from player data
        const headshotUrl = getTrustedImageUrl(data.headshot)

        if (!headshotUrl) {
            console.warn(`No headshot found for player ${playerId}`)
            return null
        }

        return {
            playerId,
            headshotUrl,
            fallbackUrl: `https://nhl.bamcontent.com/images/headshots/current/168x168/${playerId}.jpg`,
        }
    } catch (error) {
        console.error(`Error fetching player photo for ${playerId}:`, error)
        return null
    }
}

/**
 * Generate fallback avatar URL based on player name and team
 * @param {string} playerName - Player name
 * @param {string} team - Team abbreviation
 * @returns {string} Fallback avatar URL
 */
function generateFallbackAvatar(playerName: string, team: string): string {
    // Use UI Avatars API for consistent fallback avatars
    const initials =
        playerName
            .trim()
            .split(/\s+/)
            .map((part) => Array.from(part)[0] || '')
            .join('')
            .replace(/[^\p{L}\p{N}]/gu, '')
            .toUpperCase()
            .substring(0, 2) || 'P'

    const normalizedTeam = team
        .trim()
        .toUpperCase()
        .replace(/[^A-Z]/g, '')
        .substring(0, 3)

    // Generate a consistent color based on team
    const teamColors: Record<string, string> = {
        ANA: 'B8860B',
        ARI: 'E85D04',
        BOS: 'FFB81C',
        BUF: '007A50',
        CGY: 'C8102E',
        CAR: 'CC0000',
        CHI: 'CF0A2C',
        COL: '6F002F',
        CBJ: '041E42',
        DAL: '006847',
        DET: 'C8102E',
        EDM: 'FF4C00',
        FLA: 'C8102E',
        LAK: '852C2C',
        MIN: '154734',
        MTL: 'AF1E32',
        NJD: 'CE1126',
        NSH: 'FFB81C',
        NYI: 'F47920',
        NYR: '003E7E',
        OTT: 'C8102E',
        PHI: 'FF6A00',
        PIT: 'FFB81C',
        SJS: '00627C',
        SEA: '96D822',
        STL: '002F5F',
        TBL: '002868',
        TOR: '003E7E',
        VAN: '041C42',
        VGK: 'B9975B',
        WPG: '041C42',
        WSH: 'C8102E',
    }

    const backgroundColor = teamColors[normalizedTeam] || '6B7280'

    return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=${backgroundColor}&color=FFFFFF&font-size=0.6&bold=true`
}

export async function GET({ url }) {
    try {
        const numericPlayerId = parsePlayerId(url.searchParams.get('id'))

        if (!numericPlayerId) {
            return json({ error: 'Invalid player ID' }, { status: 400 })
        }

        // Try to get player photo from NHL API
        const playerPhotoData = await getPlayerPhoto(numericPlayerId)

        if (!playerPhotoData) {
            // If NHL API fails, generate a fallback avatar
            const playerName = url.searchParams.get('name') || 'Player'
            const team = url.searchParams.get('team') || 'NHL'

            const fallbackUrl = generateFallbackAvatar(playerName, team)

            return json({
                playerId: numericPlayerId,
                headshotUrl: null,
                fallbackUrl,
                isFallback: true,
            })
        }

        return json({
            playerId: playerPhotoData.playerId,
            headshotUrl: playerPhotoData.headshotUrl,
            fallbackUrl: playerPhotoData.fallbackUrl,
            isFallback: false,
        })
    } catch (error) {
        console.error('Error in player-photo API:', error)
        return json({ error: 'Internal server error' }, { status: 500 })
    }
}
