#!/usr/bin/env node

/**
 * Pre-build script to fetch last NHL team and career games played
 * for inactive Finnish players. Runs during build to avoid client-side API calls.
 * 
 * Usage: node scripts/prebuild/fetch-last-teams.cjs
 */

const fs = require('fs');
const path = require('path');

function loadEnvFile(filePath) {
    if (!fs.existsSync(filePath)) return

    const content = fs.readFileSync(filePath, 'utf8')
    for (const rawLine of content.split(/\r?\n/)) {
        const line = rawLine.trim()
        if (!line || line.startsWith('#')) continue

        const separatorIndex = line.indexOf('=')
        if (separatorIndex === -1) continue

        const key = line.slice(0, separatorIndex).trim()
        if (!key || process.env[key] !== undefined) continue

        let value = line.slice(separatorIndex + 1).trim()
        value = value.replace(/^['"]|['"]$/g, '')
        process.env[key] = value
    }
}

loadEnvFile(path.join(process.cwd(), '.env.local'))
loadEnvFile(path.join(process.cwd(), '.env'))

const INPUT_FILE = path.join(process.cwd(), 'static/data/players/finnish-roster.json')

async function fetchNHLData(url) {
    const response = await fetch(url);
    if (!response.ok) {
        return null
    }
    return response.json();
}

/**
 * Fetch player's last NHL team and career games played.
 * Uses two API calls per player:
 *  1) per-season stats to find the most recent team
 *  2) aggregated career stats to get total games played
 */
async function fetchPlayerInfo(playerId, position) {
    const endpoint = position === 'G' ? 'goalie' : 'skater'
    let lastTeam = null
    let gamesPlayed = null

    try {
        const seasonUrl = `https://api.nhle.com/stats/rest/en/${endpoint}/summary?isAggregate=false&isGame=false&start=0&limit=-1&cayenneExp=playerId%3D${playerId}`
        const seasonData = await fetchNHLData(seasonUrl)

        if (seasonData?.data && seasonData.data.length > 0) {
            const sorted = seasonData.data.sort((a, b) => b.seasonId - a.seasonId)
            const teamAbbrevs = sorted[0].teamAbbrevs || ''
            lastTeam = teamAbbrevs.split(',')[0].trim() || null
        }
    } catch (e) {
        // Fall through
    }

    try {
        const careerUrl = `https://api.nhle.com/stats/rest/en/${endpoint}/summary?isAggregate=true&isGame=false&start=0&limit=1&cayenneExp=playerId%3D${playerId}`
        const careerData = await fetchNHLData(careerUrl)

        if (careerData?.data && careerData.data.length > 0) {
            gamesPlayed = careerData.data[0].gamesPlayed || null
        }
    } catch (e) {
        // Fall through
    }

    return { lastTeam, gamesPlayed }
}

async function main() {
    console.log('🏒 Fetching last NHL team & career GP for inactive players...\n')

    if (!fs.existsSync(INPUT_FILE)) {
        console.log('⚠️  No finnish-roster.json found, skipping')
        return
    }

    const rawData = JSON.parse(fs.readFileSync(INPUT_FILE, 'utf8'))
    const players = Object.values(rawData)
    const inactivePlayers = players.filter(p => !p.isActive || !p.currentTeam || p.currentTeam === '')

    console.log(`📋 Found ${inactivePlayers.length} inactive players`)

    let updated = 0
    let cached = 0
    const updates = {}

    for (const player of inactivePlayers) {
        const playerId = player.playerId || player.id
        if (!playerId) continue

        const needsTeam = !player.lastTeam
        const needsGP = player.gamesPlayed == null
        if (!needsTeam && !needsGP) {
            cached++
            continue
        }

        console.log(`   Fetching ${player.name} (${playerId})...`)
        const info = await fetchPlayerInfo(playerId, player.position)

        if (needsTeam || needsGP) {
            updates[playerId] = {}
            if (needsTeam) updates[playerId].lastTeam = info.lastTeam
            if (needsGP) updates[playerId].gamesPlayed = info.gamesPlayed
            updated++
        }

        await new Promise(resolve => setTimeout(resolve, 100))
    }

    if (updated > 0) {
        for (const player of players) {
            const playerId = player.playerId || player.id
            if (updates[playerId]) {
                if (updates[playerId].lastTeam !== undefined) player.lastTeam = updates[playerId].lastTeam
                if (updates[playerId].gamesPlayed !== undefined) player.gamesPlayed = updates[playerId].gamesPlayed
            }
        }

        fs.writeFileSync(INPUT_FILE, JSON.stringify(rawData, null, 2))
        console.log(`\n💾 Updated ${updated} players with lastTeam/gamesPlayed info`)
    } else {
        console.log(`\n✅ No updates needed (${cached} players already cached)`)
    }

    console.log('\n✅ Pre-build complete!')
}

main().catch(error => {
    console.error('\n❌ Pre-build failed:', error)
    process.exit(1)
})