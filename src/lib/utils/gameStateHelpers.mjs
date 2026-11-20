// @ts-nocheck

export const GAME_STATE = {
    OFF: 'OFF',
    FINAL: 'FINAL',
    PRE: 'PRE',
    FUT: 'FUT',
    LIVE: 'LIVE',
    CRIT: 'CRIT',
    IRT: 'IRT',
}

export function isCompletedGame(state) {
    return state === GAME_STATE.OFF || state === GAME_STATE.FINAL
}

function findPlayerGame(player, gamesData) {
    return gamesData?.findGameById?.(player?.game_id)
}

/** The game record takes precedence over duplicated fields in older player records. */
export function getGameStateForPlayer(player, gamesData) {
    const status =
        findPlayerGame(player, gamesData)?.gameState ||
        player?.game_status ||
        player?.gameStatus ||
        player?.game_state ||
        player?.gameState
    return typeof status === 'string' ? status.trim().toUpperCase() || null : null
}

export function isPlayerGameLive(player, gamesData) {
    const state = getGameStateForPlayer(player, gamesData)
    return (
        !findPlayerGame(player, gamesData)?.resultDelayed &&
        [GAME_STATE.LIVE, GAME_STATE.CRIT, GAME_STATE.IRT].includes(state)
    )
}

export function shouldShowGameResult(player, gamesData) {
    const state = getGameStateForPlayer(player, gamesData)
    return isCompletedGame(state) || (!state && Boolean(player?.game_result || player?.gameResult))
}

export function isGameUpcoming(player, gamesData) {
    const state = getGameStateForPlayer(player, gamesData)
    return state === GAME_STATE.PRE || state === GAME_STATE.FUT
}
