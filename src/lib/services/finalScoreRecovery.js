import { isCompletedGame } from '$lib/utils/gameStateHelpers.mjs'

/** @typedef {import('./dataService.js').ResultsSnapshot} ResultsSnapshot */
/** @typedef {ResultsSnapshot['games'][number]} Game */
/** @typedef {{start: number, home: string, away: string, homeScore: number, awayScore: number, period: number, isSO: boolean}} FinalScore */

const delayThreshold = 15 * 60 * 1000
const recoveryWindow = 48 * 60 * 60 * 1000
const startTimeTolerance = 15 * 60 * 1000
const teamAliases = new Map([
    ['LA', 'LAK'],
    ['NJ', 'NJD'],
    ['SJ', 'SJS'],
    ['TB', 'TBL'],
    ['UTAH', 'UTA'],
])
/** @type {Map<number, FinalScore>} */
const recoveredFinals = new Map()

/** @param {unknown} value */
function parseScore(value) {
    if (typeof value !== 'string' || !/^\d+$/.test(value)) return NaN
    const score = Number(value)
    return Number.isSafeInteger(score) ? score : NaN
}

/** @param {any} event */
function parseFinal(event) {
    const competition = event?.competitions?.[0]
    const status = competition?.status
    const type = status?.type
    if (type?.name !== 'STATUS_FINAL' || type.state !== 'post' || type.completed !== true) {
        return null
    }
    const teams = competition.competitors
    if (!Array.isArray(teams) || teams.length !== 2) return null
    const home = teams.find((team) => team?.homeAway === 'home')
    const away = teams.find((team) => team?.homeAway === 'away')
    const homeCode = home?.team?.abbreviation
    const awayCode = away?.team?.abbreviation
    const homeScore = parseScore(home?.score)
    const awayScore = parseScore(away?.score)
    const start = Date.parse(event.date)
    const period = status.period
    if (
        !homeCode ||
        !awayCode ||
        !Number.isFinite(start) ||
        !Number.isFinite(homeScore) ||
        !Number.isFinite(awayScore) ||
        homeScore === awayScore ||
        !Number.isInteger(period) ||
        period < 3
    )
        return null

    return {
        start,
        home: teamAliases.get(homeCode) ?? homeCode,
        away: teamAliases.get(awayCode) ?? awayCode,
        homeScore,
        awayScore,
        period,
        isSO: type.altDetail === 'SO',
    }
}

/** @param {string} date @param {Game[]} games */
async function recoverFinals(date, games) {
    try {
        const response = await fetch(
            `https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates=${date.replaceAll('-', '')}`,
            {
                credentials: 'omit',
                referrerPolicy: 'no-referrer',
                signal: AbortSignal.timeout(3000),
            }
        )
        if (!response.ok) return
        const { events } = await response.json()
        if (!Array.isArray(events)) return
        const finals = events.map(parseFinal).filter((score) => score !== null)
        for (const game of games) {
            const start = Date.parse(game.startTime ?? '')
            const matches = finals.filter(
                (final) =>
                    final.home === game.homeTeam &&
                    final.away === game.awayTeam &&
                    Math.abs(final.start - start) <= startTimeTolerance
            )
            const [match] = matches
            if (match && matches.length === 1) recoveredFinals.set(game.gameId, match)
        }
    } catch {
        // Keep the published stats and any final already verified in this tab.
    }
}

/** @param {ResultsSnapshot} snapshot */
export async function recoverDelayedResults(snapshot) {
    const now = Date.now()
    const timestamp = typeof snapshot.generated_at === 'string' ? snapshot.generated_at : ''
    // Older workflow snapshots stored UTC without an offset.
    const collected = Date.parse(
        timestamp.endsWith('Z') || /[+-]\d\d:\d\d$/.test(timestamp) ? timestamp : `${timestamp}Z`
    )
    const earliestRecoverableStart = now - recoveryWindow
    for (const [id, final] of recoveredFinals) {
        if (final.start < earliestRecoverableStart) recoveredFinals.delete(id)
    }
    const delayed = new Set(
        snapshot.games.filter((game) => {
            const start = Date.parse(game.startTime ?? '')
            return (
                !isCompletedGame(game.gameState) &&
                (recoveredFinals.has(game.gameId) ||
                    now - Math.max(start, collected || 0) >= delayThreshold)
            )
        })
    )
    if (delayed.size === 0) return snapshot

    const unresolved = [...delayed].filter(
        (game) =>
            Date.parse(game.startTime ?? '') >= earliestRecoverableStart &&
            !recoveredFinals.has(game.gameId)
    )
    if (unresolved.length) await recoverFinals(snapshot.date, unresolved)

    /** @type {Map<number, FinalScore>} */
    const recoveredGames = new Map()
    const games = snapshot.games.map((game) => {
        if (!delayed.has(game)) return game
        const final = recoveredFinals.get(game.gameId)
        if (!final) return { ...game, resultDelayed: true }
        recoveredGames.set(game.gameId, final)
        return {
            ...game,
            homeScore: final.homeScore,
            awayScore: final.awayScore,
            gameState: 'FINAL',
            period: final.period,
            isOT: final.period > 3,
            isSO: final.isSO,
            playerStatsPending: true,
        }
    })

    const players = snapshot.players.map((player) => {
        const final = recoveredGames.get(player.game_id)
        if (!final || (player.team !== final.home && player.team !== final.away)) return player
        const [teamScore, opponentScore] =
            player.team === final.home
                ? [final.homeScore, final.awayScore]
                : [final.awayScore, final.homeScore]
        return {
            ...player,
            game_status: 'FINAL',
            game_score: `${teamScore}-${opponentScore}`,
            game_result: teamScore > opponentScore ? 'W' : 'L',
        }
    })
    return { ...snapshot, games, players }
}
