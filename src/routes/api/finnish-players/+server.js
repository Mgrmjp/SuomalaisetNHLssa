import { json } from '@sveltejs/kit'
import { readFile } from 'node:fs/promises'
import path from 'node:path'

// Security: Define allowed formats to prevent command injection
const ALLOWED_FORMATS = ['full', 'simple', 'names']

/**
 * Validate and sanitize user input to prevent command injection
 * @param {string} format - User input format parameter
 * @returns {string} - Validated format or default
 */
function validateFormat(format) {
    if (!format || typeof format !== 'string') {
        return 'full'
    }

    // Remove any potentially dangerous characters
    const sanitized = format.replace(/[^a-zA-Z0-9_-]/g, '')

    // Check if the sanitized format is in our allowlist
    if (ALLOWED_FORMATS.includes(sanitized.toLowerCase())) {
        return sanitized.toLowerCase()
    }

    // Default to 'full' if invalid format provided
    return 'full'
}

/**
 * Load Finnish players from the pre-populated JSON database
 */
async function loadFinnishPlayers() {
    try {
        // Load the pre-populated Finnish players data
        // This uses the file that's populated by the Python script via build process
        const dbPath = path.join(process.cwd(), 'data', 'players', 'finnish-roster.json')
        const data = await readFile(dbPath, 'utf8')
        return JSON.parse(data)
    } catch (error) {
        console.error('Error reading finnish-roster.json, returning empty array:', error)
        // Return empty array if file doesn't exist (expected during initial setup)
        return []
    }
}

export async function GET({ url }) {
    try {
        const rawFormat = url.searchParams.get('format')

        // Security: Validate and sanitize user input
        const format = validateFormat(rawFormat)

        // Log validation for security monitoring
        if (rawFormat && rawFormat !== format) {
            console.warn(
                `Security: Invalid format parameter sanitized: "${rawFormat}" -> "${format}"`
            )
        }

        // Load Finnish players from pre-populated JSON database
        const players = await loadFinnishPlayers()

        // Format response based on requested format
        let data
        if (format === 'simple') {
            // Return name: position mapping
            data = players.reduce((acc, player) => {
                acc[player.name] = player.position
                return acc
            }, {})
        } else if (format === 'names') {
            // Return just names array
            data = players.map((player) => player.name)
        } else {
            // Return full player data (compatible format)
            data = players.map((player) => ({
                name: player.name,
                position: player.position,
                team: player.team,
                team_abbrev: player.team_abbrev || player.team || '',
                jersey_number: player.jersey_number,
                shoots_catches: player.shoots_catches || '',
                height: player.height || null,
                weight: player.weight || null,
                birth_date: player.birth_date || null,
                birth_city: player.birth_city || null,
                birth_country: player.birth_country || null,
                draft_year: player.draft_year || null,
                draft_round: player.draft_round || null,
                draft_overall: player.draft_overall || null,
                is_rookie: player.is_rookie || false,
                is_active: player.is_active || true,
                id: player.id || null,
            }))
        }

        return json(data)
    } catch (error) {
        console.error('Error loading Finnish players:', error)
        return json({ error: 'Failed to fetch Finnish players' }, { status: 500 })
    }
}
