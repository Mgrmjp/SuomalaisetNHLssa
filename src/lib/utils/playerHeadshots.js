import { normalizeTeamAbbreviation } from './teamMapping.js'

/**
 * Sanitize player image URL by stripping malformed transformation parameters.
 * Example: /media/players/Jarventie.png.600x750_q85_box-8%2C0%2C501%2C617.png -> /media/players/Jarventie.png
 * @param {string} url - The potentially malformed image URL
 * @returns {string} - Sanitized URL
 */
export function sanitizeImageUrl(url) {
    if (!url || typeof url !== 'string') {
        return url
    }

    // Pattern matches URLs with transformation parameters like:
    // .600x750_q85_box-8%2C0%2C501%2C617.png
    // The pattern is: dot, dimensions (e.g., 600x750), optional _qXX quality,
    // optional _box-XX%2CXX%2CXX%2CXX crop params, then the original extension
    const transformationPattern = /\.\d+x\d+(?:_q\d+)?(?:_box-[\d%,]+)*\.(png|jpg|jpeg|webp|gif)$/i

    const match = url.match(transformationPattern)
    if (match && match.index !== undefined) {
        // Extract the base filename (everything before the transformation params)
        const baseUrl = url.substring(0, match.index)
        const extension = match[1].toLowerCase()
        return `${baseUrl}.${extension}`
    }

    return url
}

function getCurrentSeasonId(date = new Date()) {
    const year = date.getFullYear()
    const month = date.getMonth()
    const startYear = month < 8 ? year - 1 : year
    return `${startYear}${startYear + 1}`
}

export function getLocalHeadshotUrl(playerId) {
    if (!playerId) return null
    return `/headshots/${playerId}.webp`
}

export function getLocalHeadshotThumbUrl(playerId) {
    if (!playerId) return null
    return `/headshots/thumbs/${playerId}.jpg`
}

export function getRemoteHeadshotUrl(playerId) {
    if (!playerId) return null
    return `https://nhl.bamcontent.com/images/headshots/current/168x168/${playerId}.jpg`
}

export function getLatestNhlHeadshotUrl(playerId) {
    if (!playerId) return null
    return `https://assets.nhle.com/mugs/nhl/latest/${playerId}.png`
}

export function getSeasonTeamHeadshotUrl(playerId, teamAbbrev, seasonId = getCurrentSeasonId()) {
    if (!playerId || !teamAbbrev || !seasonId) return null

    const normalizedTeam = normalizeTeamAbbreviation(teamAbbrev)
    if (!normalizedTeam) return null

    return `https://assets.nhle.com/mugs/nhl/${seasonId}/${normalizedTeam}/${playerId}.png`
}

export function getHeadshotCandidates(
    playerId,
    { teamAbbrev = '', headshotUrl = '', seasonId = getCurrentSeasonId() } = {}
) {
    if (!playerId) {
        return headshotUrl ? [sanitizeImageUrl(headshotUrl)] : []
    }

    // Sanitize the explicit URL to strip any transformation parameters
    const sanitizedHeadshotUrl = sanitizeImageUrl(headshotUrl)

    const urls = [
        sanitizedHeadshotUrl || null,
        getLatestNhlHeadshotUrl(playerId),
        getSeasonTeamHeadshotUrl(playerId, teamAbbrev, seasonId),
        getRemoteHeadshotUrl(playerId),
    ].filter(Boolean)

    return [...new Set(urls)]
}

export function getStaticSafeHeadshotUrl(playerId, options = {}) {
    const candidates = getHeadshotCandidates(playerId, options)
    // First candidate is already sanitized via getHeadshotCandidates
    return candidates[0] || null
}
