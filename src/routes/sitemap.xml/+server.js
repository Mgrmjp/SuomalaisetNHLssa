// @ts-nocheck
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { correctFullName } from '$lib/utils/finnishNameUtils.js'

export const prerender = true

const siteUrl = 'https://suomalaisetnhlssa.fi'

function toDate(value) {
    if (!value) return new Date().toISOString().split('T')[0]
    return new Date(value).toISOString().split('T')[0]
}

function fileLastMod(path) {
    try {
        return toDate(statSync(path).mtime)
    } catch {
        return null
    }
}

function readJson(path) {
    return JSON.parse(readFileSync(path, 'utf-8'))
}

function latestDate(dates) {
    return dates.filter(Boolean).sort().at(-1) || null
}

function getPlayerStatsLastMod() {
    try {
        const metadataPath = join(process.cwd(), 'static/data/player-stats/metadata.json')
        const metadata = readJson(metadataPath)
        return metadata.updatedAt ? toDate(metadata.updatedAt) : fileLastMod(metadataPath)
    } catch {
        return null
    }
}

function getLatestGameLastMod() {
    try {
        const gamesDir = join(process.cwd(), 'static/data/prepopulated/games')
        const dates = readdirSync(gamesDir)
            .filter((file) => file.endsWith('.json'))
            .map((file) => file.replace('.json', ''))
        return latestDate(dates)
    } catch {
        return null
    }
}

function getLatestArticleDate() {
    try {
        const articlesPath = join(process.cwd(), 'static/data/articles.json')
        const articles = readJson(articlesPath)
        return latestDate(articles.map((article) => article.date))
    } catch {
        return null
    }
}

function getLatestScoutingLastMod() {
    try {
        const scoutingDir = join(process.cwd(), 'content/scouting')
        const dates = readdirSync(scoutingDir)
            .filter((file) => file.endsWith('.md'))
            .map((file) => fileLastMod(join(scoutingDir, file)))
        return latestDate(dates)
    } catch {
        return null
    }
}

function getStaticPages() {
    const statsLastMod = getPlayerStatsLastMod()
    const gamesLastMod = getLatestGameLastMod()
    const articlesLastMod = getLatestArticleDate()
    const rosterLastMod = fileLastMod(
        join(process.cwd(), 'static/data/players/finnish-roster.json')
    )
    const prospectsLastMod = fileLastMod(join(process.cwd(), 'static/data/finnish_prospects.json'))
    const draftLastMod = fileLastMod(join(process.cwd(), 'static/data/finnish_draft_rankings.json'))
    const scoutingLastMod = getLatestScoutingLastMod()

    return [
        { path: '/', priority: '1.0', changefreq: 'daily', lastmod: gamesLastMod || statsLastMod },
        { path: '/pisteporssi', priority: '0.9', changefreq: 'daily', lastmod: statsLastMod },
        {
            path: '/pelaajat',
            priority: '0.9',
            changefreq: 'daily',
            lastmod: statsLastMod || rosterLastMod,
        },
        { path: '/joukkueet', priority: '0.8', changefreq: 'daily', lastmod: statsLastMod },
        { path: '/viikkokatsaus', priority: '0.8', changefreq: 'weekly', lastmod: articlesLastMod },
        {
            path: '/mestaruudet',
            priority: '0.8',
            changefreq: 'monthly',
            lastmod: fileLastMod(join(process.cwd(), 'static/data/stanley-cup-winners.json')),
        },
        { path: '/sarjataulukko', priority: '0.8', changefreq: 'daily', lastmod: gamesLastMod },
        {
            path: '/tietoa',
            priority: '0.5',
            changefreq: 'monthly',
            lastmod: fileLastMod(join(process.cwd(), 'src/routes/tietoa/+page.svelte')),
        },
        { path: '/lupaukset', priority: '0.7', changefreq: 'daily', lastmod: prospectsLastMod },
        { path: '/drafts', priority: '0.7', changefreq: 'weekly', lastmod: draftLastMod },
        { path: '/scouting', priority: '0.7', changefreq: 'weekly', lastmod: scoutingLastMod },
    ]
}

function getWeeklyReviewRoutes() {
    try {
        const articlesPath = join(process.cwd(), 'static/data/articles.json')
        const articles = readJson(articlesPath)

        return articles.map((article) => ({
            path: `/viikkokatsaus/${article.slug}`,
            priority: '0.7',
            changefreq: 'weekly',
            lastmod: article.date,
        }))
    } catch (error) {
        console.warn('Could not load articles for sitemap:', error)
        return []
    }
}

function nameToSlug(name) {
    return name
        .toLowerCase()
        .replace(/ä/g, 'a')
        .replace(/ö/g, 'o')
        .replace(/å/g, 'o')
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '')
}

function getRosterName(player) {
    const firstName = player.firstName?.default || ''
    const lastName = player.lastName?.fi || player.lastName?.default || ''
    return correctFullName(`${firstName} ${lastName}`.trim() || player.name)
}

function getPlayerRoutes() {
    try {
        const routes = new Map()
        const statsLastMod = getPlayerStatsLastMod()
        const rosterPath = join(process.cwd(), 'static/data/players/finnish-roster.json')
        const rosterLastMod = fileLastMod(rosterPath)
        const now = new Date()
        const currentYear = now.getFullYear()
        const currentMonth = now.getMonth()
        const startYear = currentMonth < 9 ? currentYear - 1 : currentYear
        const endYear = startYear + 1
        const seasonId = `${startYear}${endYear}`

        const prebuiltDir = join(process.cwd(), 'static/data/player-stats')
        const skatersFile = join(prebuiltDir, `skaters-${seasonId}.json`)
        const goaliesFile = join(prebuiltDir, `goalies-${seasonId}.json`)

        const skatersData = readJson(skatersFile)
        const goaliesData = readJson(goaliesFile)

        const allPlayers = [...skatersData, ...goaliesData]

        for (const player of allPlayers) {
            const playerName = player.skaterFullName || player.goalieFullName
            const correctedName = correctFullName(playerName)
            const slug = nameToSlug(correctedName)

            routes.set(`/pelaajat/${slug}`, {
                path: `/pelaajat/${slug}`,
                priority: '0.7',
                changefreq: 'daily',
                lastmod: statsLastMod,
            })
        }

        const rosterData = readJson(rosterPath)
        for (const player of Object.values(rosterData)) {
            const slug = nameToSlug(getRosterName(player))
            const path = `/pelaajat/${slug}`
            if (!routes.has(path)) {
                routes.set(path, {
                    path,
                    priority: player.isActive ? '0.6' : '0.5',
                    changefreq: player.isActive ? 'weekly' : 'monthly',
                    lastmod: rosterLastMod,
                })
            }
        }

        return Array.from(routes.values())
    } catch (error) {
        console.warn('Could not load player data for sitemap:', error)
        return []
    }
}

function getScoutingRoutes() {
    try {
        const scoutingDir = join(process.cwd(), 'content/scouting')
        return readdirSync(scoutingDir)
            .filter((file) => file.endsWith('.md') && file !== 'index.md')
            .map((file) => {
                const slug = file.replace('.md', '')
                return {
                    path: `/scouting/${slug}`,
                    priority: '0.6',
                    changefreq: 'monthly',
                    lastmod: fileLastMod(join(scoutingDir, file)),
                }
            })
    } catch (error) {
        console.warn('Could not load scouting routes for sitemap:', error)
        return []
    }
}

/** @type {import('./$types').RequestHandler} */
export async function GET() {
    const fallbackLastMod = new Date().toISOString().split('T')[0]
    const playerRoutes = getPlayerRoutes()
    const weeklyRoutes = getWeeklyReviewRoutes()
    const scoutingRoutes = getScoutingRoutes()
    const allPages = [...getStaticPages(), ...playerRoutes, ...weeklyRoutes, ...scoutingRoutes]

    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allPages
    .map(
        (page) => `  <url>
    <loc>${siteUrl}${page.path}</loc>
    <lastmod>${page.lastmod || fallbackLastMod}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`
    )
    .join('\n')}
</urlset>`

    return new Response(sitemap, {
        headers: {
            'Content-Type': 'application/xml',
            'Cache-Control': 'max-age=3600',
        },
    })
}
