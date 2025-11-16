#!/usr/bin/env node
/**
 * Fetch Finnish NHL players and generate tiny headshot thumbnails for placeholders.
 *
 * - Iterates all NHL teams via roster API
 * - Filters Finnish players (birthCountry FIN/Finland)
 * - Downloads headshot PNGs and saves 40px JPEG thumbs in static/headshots/thumbs
 *
 * Usage: node scripts/data/fetch-finnish-headshot-thumbs.js
 * Optional: install sharp for resizing (npm i -D sharp). Without sharp, files save as-is.
 */

import fs from 'fs'
import path from 'path'

const NHL_API = 'https://api-web.nhle.com'
const TEAM_ABBREVS = [
	'ANA', 'ARI', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET', 'EDM', 'FLA', 'LAK', 'MIN',
	'MTL', 'NJD', 'NSH', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'SEA', 'SJS', 'STL', 'TBL', 'TOR', 'VAN', 'VGK', 'WPG', 'WSH'
]
const HEADSHOT_BASE = 'https://assets.nhle.com/mugs/nhl/current'
const OUTPUT_DIR = path.join(process.cwd(), 'static', 'headshots', 'thumbs')
const SIZE = 40
const CONCURRENCY = 4

let sharp = null
try {
	sharp = (await import('sharp')).default
} catch {
	console.warn('sharp not found, thumbnails will be saved without resizing')
}

const sleep = (ms) => new Promise((res) => setTimeout(res, ms))

async function fetchJson(url) {
	const res = await fetch(url, { timeout: 8000 })
	if (!res.ok) throw new Error(`HTTP ${res.status}`)
	return res.json()
}

function isFinnish(player) {
	const country = (player?.birthCountry || '').toUpperCase()
	return country === 'FIN' || country === 'FINLAND'
}

function headshotUrl(team, playerId) {
	// Uses the "current" CDN path which redirects to current season mug
	return `${HEADSHOT_BASE}/${team}/${playerId}.png`
}

async function downloadBuffer(url) {
	const res = await fetch(url, { timeout: 8000 })
	if (!res.ok) throw new Error(`download failed ${res.status}`)
	return Buffer.from(await res.arrayBuffer())
}

async function saveThumb(team, playerId) {
	try {
		const url = headshotUrl(team, playerId)
		const buf = await downloadBuffer(url)
		const outPath = path.join(OUTPUT_DIR, `${playerId}.jpg`)

		if (sharp) {
			const thumb = await sharp(buf).resize(SIZE, SIZE, { fit: 'cover' }).jpeg({ quality: 65 }).toBuffer()
			fs.writeFileSync(outPath, thumb)
		} else {
			fs.writeFileSync(outPath, buf)
		}

		return { ok: true }
	} catch (err) {
		return { ok: false, error: err?.message }
	}
}

async function processTeam(team) {
	try {
		const roster = await fetchJson(`${NHL_API}/v1/roster/${team}/current`)
		const players = roster?.forwards?.concat(roster?.defensemen || [], roster?.goalies || []) || []
		const finns = players.filter(isFinnish)
		return { team, players: finns }
	} catch (err) {
		console.error(`Failed roster for ${team}:`, err?.message)
		return { team, players: [] }
	}
}

async function run() {
	fs.mkdirSync(OUTPUT_DIR, { recursive: true })

	const teamsData = []
	for (let i = 0; i < TEAM_ABBREVS.length; i += CONCURRENCY) {
		const chunk = TEAM_ABBREVS.slice(i, i + CONCURRENCY)
		const results = await Promise.all(chunk.map(processTeam))
		teamsData.push(...results)
		await sleep(200) // be nice to the API
	}

	const jobs = []
	for (const { team, players } of teamsData) {
		for (const p of players) {
			jobs.push({ team, playerId: p.id, name: `${p.firstName?.default || ''} ${p.lastName?.default || ''}`.trim() })
		}
	}

	let success = 0
	for (const job of jobs) {
		const res = await saveThumb(job.team, job.playerId)
		if (res.ok) {
			success++
		} else {
			console.warn(`Thumb failed ${job.playerId} (${job.team}): ${res.error}`)
		}
	}

	console.log(`Finnish players: ${jobs.length}, thumbs saved: ${success}, out dir: ${OUTPUT_DIR}`)
}

run().catch((err) => {
	console.error('Fatal:', err)
	process.exit(1)
})
