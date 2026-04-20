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

/** @type {import('./$types').PageServerLoad} */
export async function load() {
    const gamesDir = join(process.cwd(), 'static', 'data', 'prepopulated', 'games')

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
        }
    } catch (error) {
        console.warn('Could not load homepage SEO data:', error)
        return {
            initialDate: '',
            seo: buildSeo(null, ''),
        }
    }
}
