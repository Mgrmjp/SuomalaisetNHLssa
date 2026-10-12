// Shared roster normalization for static/data/players/finnish-roster.json.
// Used by the /api/finnish-players endpoint and the FinnishRoster component so
// both interpret array/object cache formats, field aliases, activity flags,
// and headshot-inferred teams identically.

/**
 * Player record as stored in the roster cache. NHL API fields are camelCase;
 * pipeline additions (gamesPlayed, lastTeam) and legacy snapshots use
 * snake_case aliases.
 * @typedef {Record<string, any>} RawRosterPlayer
 */

/**
 * Normalized player record consumed by the API route and the roster component.
 * Explicit false and numeric zero values are preserved; unknown values fall
 * back to null (or the documented defaults).
 * @typedef {Object} NormalizedRosterPlayer
 * @property {number|string|null} id
 * @property {string|undefined} name
 * @property {string|undefined} position
 * @property {string} team
 * @property {string} team_abbrev
 * @property {number|string|undefined} jersey_number
 * @property {string} shoots_catches
 * @property {number|null} height
 * @property {number|null} weight
 * @property {string|null} birth_date
 * @property {string|null} birth_city
 * @property {string|null} birth_country
 * @property {number|null} draft_year
 * @property {number|null} draft_round
 * @property {number|null} draft_overall
 * @property {boolean} is_rookie
 * @property {boolean} is_active
 * @property {number|null} games_played
 * @property {string|null} lastTeam
 * @property {string|null} headshot
 */

/**
 * Extract team abbreviation from an NHL headshot URL.
 * Format: https://assets.nhle.com/mugs/nhl/20252026/TEAM/playerId.png
 * @param {unknown} headshot
 * @returns {string}
 */
export function extractTeamFromHeadshot(headshot) {
    if (!headshot || typeof headshot !== 'string') return ''
    const match = headshot.match(/\/mugs\/nhl\/\d+\/([A-Z]+)\/\d+\.png/)
    return match?.[1] ?? ''
}

/**
 * Normalize one raw roster record into the canonical player shape.
 * @param {RawRosterPlayer} player
 * @returns {NormalizedRosterPlayer}
 */
export function normalizeRosterPlayer(player) {
    const team = player.teamAbbrev || player.team || extractTeamFromHeadshot(player.headshot) || ''
    return {
        id: player.playerId ?? player.id,
        name: player.name,
        position: player.position,
        team,
        team_abbrev: team,
        jersey_number: player.sweaterNumber ?? player.jersey_number,
        shoots_catches: player.shootsCatches || player.shoots_catches || '',
        height: player.heightInches ?? player.height ?? null,
        weight: player.weightLbs ?? player.weight ?? null,
        birth_date: player.birthDate ?? player.birth_date ?? null,
        birth_city: player.birthCity?.default ?? player.birthplace ?? player.birth_city ?? null,
        birth_country: player.birthCountry ?? player.birth_country ?? null,
        draft_year: player.draftYear ?? player.draft_year ?? null,
        draft_round: player.draftRound ?? player.draft_round ?? null,
        draft_overall: player.draftOverall ?? player.draft_overall ?? null,
        is_rookie: player.isRookie ?? player.is_rookie ?? false,
        is_active: player.isActive !== false && player.is_active !== false,
        games_played: player.gamesPlayed ?? player.games_played ?? null,
        lastTeam: player.lastTeam ?? null,
        headshot: player.headshot ?? null,
    }
}

/**
 * Normalize a roster payload in either supported format: an array of player
 * records or an object keyed by player ID.
 * @param {RawRosterPlayer[] | Record<string, RawRosterPlayer>} rawData
 * @returns {NormalizedRosterPlayer[]}
 */
export function normalizeRosterData(rawData) {
    if (Array.isArray(rawData)) {
        return rawData.map(normalizeRosterPlayer)
    }
    return Object.values(rawData).map(normalizeRosterPlayer)
}
