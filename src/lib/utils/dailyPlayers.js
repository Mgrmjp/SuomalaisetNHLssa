// @ts-nocheck
import { isGoalie } from './positionHelpers.js'

/** Players with recorded ice time or statistics; exclude scheduled and unused goalies. */
export function didParticipate(player, gamesData) {
    if (!player || player.playerId == null || player.game_id == null) return false
    const game = gamesData?.findGameById?.(player.game_id)
    const state = String(
        game?.gameState || player.game_status || player.gameStatus || player.gameState || ''
    ).toUpperCase()
    if (state === 'FUT' || state === 'PRE') return false
    const toi = player.time_on_ice || player.toi
    if (toi && toi !== '0:00' && toi !== '00:00') return true
    if (isGoalie(player)) {
        return (
            Number(player.shots_against ?? player.shotsAgainst ?? 0) > 0 ||
            Number(player.saves ?? player.goalie_saves ?? 0) > 0 ||
            Number(player.goals_against ?? player.goalsAgainst ?? 0) > 0
        )
    }
    return [
        player.points,
        player.goals,
        player.assists,
        player.shots,
        player.hits,
        player.blocked_shots,
        player.takeaways,
        player.giveaways,
        player.penalty_minutes,
        player.penaltyMinutes,
        player.plus_minus,
        player.plusMinus,
    ].some((value) => Number(value) !== 0 && Number.isFinite(Number(value)))
}

export function dailyPlayerPoints(player) {
    const points = Number(player.points)
    if (player.points != null && Number.isFinite(points)) return points
    return (Number(player.goals) || 0) + (Number(player.assists) || 0)
}

export function sortDailyPlayers(players, sortBy = 'points') {
    const number = (player, field) =>
        field === 'points' ? dailyPlayerPoints(player) : Number(player[field]) || 0
    const seconds = (player) => {
        const [minutes, secs] = String(player.time_on_ice || player.toi || '0:00')
            .split(':')
            .map(Number)
        return (minutes || 0) * 60 + (secs || 0)
    }
    const name = (player) => player.name?.default || player.name || player.fullName || ''
    return [...players].sort((a, b) => {
        if (sortBy === 'name') return name(a).localeCompare(name(b), 'fi')
        const diff =
            sortBy === 'time' ? seconds(b) - seconds(a) : number(b, sortBy) - number(a, sortBy)
        return (
            diff ||
            number(b, 'points') - number(a, 'points') ||
            number(b, 'goals') - number(a, 'goals') ||
            name(a).localeCompare(name(b), 'fi')
        )
    })
}

/** Select only exceptional performances, using completed games for shutouts. */
export function getDailyHighlights(players, gamesData) {
    return players
        .flatMap((player) => {
            const name = player.name?.default || player.name || player.fullName || ''
            if (!name) return []
            const goals = Number(player.goals) || 0
            if (!isGoalie(player) && goals >= 2) {
                return [
                    {
                        name,
                        text: goals >= 3 ? 'hattutemppu' : `${goals} maalia`,
                        priority: goals,
                        playerId: player.playerId,
                        gameId: player.game_id,
                    },
                ]
            }
            const points = dailyPlayerPoints(player)
            if (!isGoalie(player) && points >= 2) {
                return [
                    {
                        name,
                        text: `${points} pistettä`,
                        priority: points,
                        playerId: player.playerId,
                        gameId: player.game_id,
                    },
                ]
            }
            const allowed = player.goals_against ?? player.goalsAgainst
            const shots = Number(player.shots_against ?? player.shotsAgainst) || 0
            const game = gamesData?.findGameById?.(player.game_id)
            const status = String(
                game?.gameState || player.game_status || player.gameState || ''
            ).toUpperCase()
            const result = String(player.game_result || player.gameResult || '').toUpperCase()
            const finished =
                ['OFF', 'FINAL'].includes(status) ||
                (!status && ['W', 'L', 'OTL', 'SOL', 'OTW', 'SOW'].includes(result))
            if (
                isGoalie(player) &&
                allowed != null &&
                Number(allowed) === 0 &&
                shots >= 15 &&
                finished
            ) {
                return [
                    {
                        name,
                        text: 'nollapeli',
                        priority: 3,
                        playerId: player.playerId,
                        gameId: player.game_id,
                    },
                ]
            }
            return []
        })
        .sort((a, b) => b.priority - a.priority || a.name.localeCompare(b.name, 'fi'))
        .slice(0, 3)
}
