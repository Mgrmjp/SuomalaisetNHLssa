// @ts-nocheck
import { readdir, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { formatFinnishDateWithRelative } from '$lib/utils/dateUtils.js'

export const prerender = true

function formatLocalDate(date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
}

function buildDateLabel(value) {
    if (!value) {
        return 'valitulle päivälle'
    }

    const { formatted, relative } = formatFinnishDateWithRelative(value, {
        showYear: true,
        showWeekday: true,
        longFormat: false,
    })

    return relative ? `${relative} (${formatted})` : formatted
}

async function getGameDates(gamesDir) {
    const files = await readdir(gamesDir)
    const dates = []

    for (const file of files.filter((name) => name.endsWith('.json')).sort()) {
        const content = await readFile(join(gamesDir, file), 'utf-8')
        const data = JSON.parse(content)
        if (data.games?.length > 0) {
            dates.push(file.replace('.json', ''))
        }
    }

    return dates
}

async function loadGameData(gamesDir, date) {
    if (!date) return null
    const content = await readFile(join(gamesDir, `${date}.json`), 'utf-8')
    return JSON.parse(content)
}

function buildSeo(data, date) {
    const gameCount = data?.games?.length || 0
    const playerCount = data?.total_players ?? data?.players?.length ?? 0
    const dateLabel = buildDateLabel(date)
    const summary =
        gameCount > 0 ? `${gameCount} ottelua ${dateLabel}` : `Ei otteluita ${dateLabel}`
    const playerText =
        playerCount > 0
            ? `Seuraa ${playerCount} suomalaisen NHL-tilastoja.`
            : 'Seuraa suomalaisten NHL-matkaa.'

    return {
        date,
        dateLabel,
        gameCount,
        playerCount,
        summary,
        titleSuffix: summary,
        description: `${summary}. ${playerText} Päivän ottelut, pisteet ja onnistumiset.`,
    }
}

function getSeasonId() {
    const now = new Date()
    const currentYear = now.getFullYear()
    const currentMonth = now.getMonth()
    const startYear = currentMonth < 9 ? currentYear - 1 : currentYear
    return `${startYear}${startYear + 1}`
}

function formatSeason(seasonId) {
    return `${seasonId.slice(0, 4)}-${seasonId.slice(6, 8)}`
}

async function readJsonIfExists(filePath) {
    try {
        return JSON.parse(await readFile(filePath, 'utf-8'))
    } catch (error) {
        if (error?.code !== 'ENOENT') {
            console.warn(`Could not load ${filePath}:`, error)
        }
        return []
    }
}

async function loadPlayoffStats() {
    const seasonId = getSeasonId()
    const statsDir = join(process.cwd(), 'static', 'data', 'player-stats')
    const [skaters, goalies] = await Promise.all([
        readJsonIfExists(join(statsDir, `playoff-skaters-${seasonId}.json`)),
        readJsonIfExists(join(statsDir, `playoff-goalies-${seasonId}.json`)),
    ])

    return {
        seasonId,
        season: formatSeason(seasonId),
        skaters: skaters.map((player) => ({
            playerId: player.playerId,
            name: player.skaterFullName,
            team: player.teamAbbrevs,
            gamesPlayed: player.gamesPlayed,
            goals: player.goals,
            assists: player.assists,
            points: player.points,
        })),
        goalies: goalies.map((goalie) => ({
            playerId: goalie.playerId,
            name: goalie.goalieFullName,
            team: goalie.teamAbbrevs,
            gamesPlayed: goalie.gamesPlayed,
            wins: goalie.wins,
            savePct: goalie.savePct,
        })),
    }
}

/** @type {import('./$types').PageServerLoad} */
export async function load() {
    const gamesDir = join(process.cwd(), 'static', 'data', 'prepopulated', 'games')
    const playoffStats = await loadPlayoffStats()

    try {
        const dates = await getGameDates(gamesDir)
        const today = formatLocalDate(new Date())
        const yesterday = new Date()
        yesterday.setDate(yesterday.getDate() - 1)
        const yesterdayDate = formatLocalDate(yesterday)

        const initialDate = dates.includes(yesterdayDate)
            ? yesterdayDate
            : dates.filter((date) => date <= today).at(-1) || dates.at(-1) || ''

        const gameData = await loadGameData(gamesDir, initialDate)

        return {
            initialDate,
            seo: buildSeo(gameData, initialDate),
            playoffStats,
        }
    } catch (error) {
        console.warn('Could not load homepage SEO data:', error)
        return {
            initialDate: '',
            seo: buildSeo(null, ''),
            playoffStats,
        }
    }
}
