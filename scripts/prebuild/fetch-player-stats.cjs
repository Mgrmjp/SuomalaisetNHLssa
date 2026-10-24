#!/usr/bin/env node

/**
 * Pre-build script to fetch NHL player data with Finnish name corrections.
 * This runs during build to ensure all player names have correct Finnish letters (ä, ö, å).
 *
 * Usage: node scripts/prebuild/fetch-player-stats.js
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

// Configuration
const OUTPUT_DIR = path.join(process.cwd(), 'static/data/player-stats');
const SEASON_ID_ENV = process.env.NHL_SEASON_ID;
const MAX_FETCH_RETRIES = Number(process.env.NHL_API_MAX_RETRIES ?? 8);
const INITIAL_RETRY_DELAY_MS = Number(process.env.NHL_API_RETRY_DELAY_MS ?? 2000);
const MAX_RETRY_DELAY_MS = Number(process.env.NHL_API_MAX_RETRY_DELAY_MS ?? 60000);
const CACHE_FALLBACK_ENABLED = process.env.NHL_API_CACHE_FALLBACK !== 'false';

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Calculate current NHL season ID
 */
function getSeasonId() {
    if (SEASON_ID_ENV) return SEASON_ID_ENV;

    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth();

    // NHL season starts in October (month 9)
    // If Jan-Aug, season started previous year
    const startYear = currentMonth < 9 ? currentYear - 1 : currentYear;
    const endYear = startYear + 1;
    return `${startYear}${endYear}`;
}

/**
 * Get path to cached data file if it exists
 */
function getCachedDataPath(seasonId, type) {
    return path.join(OUTPUT_DIR, `${type}-${seasonId}.json`);
}

/**
 * Load cached data as fallback
 */
function loadCachedData(seasonId, type, quiet = false) {
    if (!CACHE_FALLBACK_ENABLED) return null;

    const cachePath = getCachedDataPath(seasonId, type);
    if (!fs.existsSync(cachePath)) return null;

    try {
        const data = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
        if (!Array.isArray(data)) return null;
        if (!quiet) console.warn(`   📦 Using cached data from ${path.basename(cachePath)} (${data.length} ${type})`);
        return data;
    } catch {
        return null;
    }
}

function loadPreviousMetadata(seasonId) {
    try {
        const metadata = JSON.parse(fs.readFileSync(path.join(OUTPUT_DIR, 'metadata.json'), 'utf8'));
        return metadata.seasonId === seasonId ? metadata : null;
    } catch {
        return null;
    }
}

/**
 * Fetch data from NHL API with retry & backoff
 */
async function fetchNHLData(url, attempt = 0) {
    const response = await fetch(url);

    if (response.ok) {
        return response.json();
    }

    const isRetryable =
        response.status === 429 ||
        response.status === 408 ||
        (response.status >= 500 && response.status < 600);

    if (isRetryable && attempt < MAX_FETCH_RETRIES) {
        const retryAfterHeader = response.headers.get('retry-after');
        const retryAfterSeconds = retryAfterHeader ? Number(retryAfterHeader) : NaN;
        const backoffMs = Number.isFinite(retryAfterSeconds)
            ? retryAfterSeconds * 1000
            : Math.min(INITIAL_RETRY_DELAY_MS * Math.pow(2, attempt), MAX_RETRY_DELAY_MS);

        console.warn(`   ⏳ NHL API rate limited (HTTP ${response.status}). Retrying in ${Math.round(backoffMs)} ms... (attempt ${attempt + 1}/${MAX_FETCH_RETRIES})`);
        await delay(backoffMs);
        return fetchNHLData(url, attempt + 1);
    }

    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
}

// Track if we've warned about OpenAI key
let openaiWarned = false;

/**
 * Correct Finnish name using OpenAI
 */
async function correctNameWithOpenAI(name) {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
        if (!openaiWarned) {
            console.warn('⚠️  OPENAI_API_KEY not set, using pattern-based correction');
            openaiWarned = true;
        }
        return correctNameWithPatterns(name);
    }

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-6-luna',
                reasoning_effort: 'none',
                messages: [{
                    role: 'user',
                    content: `Correct this Finnish name if needed. Only fix obvious Finnish letter patterns (ä, ö, å).

Name: "${name}"

Return ONLY the corrected name. If correct, return unchanged.`
                }],
                temperature: 0.1,
                max_completion_tokens: 50
            })
        });

        if (!response.ok) {
            throw new Error(`OpenAI API error: ${response.status}`);
        }

        const data = await response.json();
        const corrected = data.choices[0].message.content.trim();

        // Clean up any extra text
        return corrected.replace(/^"|"$/g, '').split('\n')[0].trim();
    } catch (error) {
        console.warn(`⚠️  OpenAI correction failed for "${name}": ${error.message}`);
        return correctNameWithPatterns(name);
    }
}

/**
 * Pattern-based name correction (fallback)
 */
function correctNameWithPatterns(name) {
    if (!name || typeof name !== 'string') return name;

    // Already has Finnish letters
    if (/[äöåÄÖÅ]/.test(name)) return name;

    // Pattern: ia -> iä at end
    if (/ia$/.test(name)) return name.replace(/ia$/, 'iä');

    // Pattern: aa + ty/ny -> ää
    if (/aa(ty|ny|ly|ry)$/.test(name)) return name.replace(/aa/, 'ää');

    // Pattern: aanen -> äänen
    if (/aanen$/.test(name)) return name.replace(/aa/, 'ää');

    // Pattern: aki -> äki
    if (/aki$/.test(name)) return name.replace(/aki$/, 'äki');

    // Pattern: jarvi -> järvi
    if (/jarvi/i.test(name)) return name.replace(/jarvi/g, 'järvi').replace(/Jarvi/g, 'Järvi');

    return name;
}

/**
 * Process and correct player data
 */
async function processPlayers(players, nameField) {
    const corrected = [];

    for (const player of players) {
        const fullName = player[nameField];
        if (!fullName) {
            corrected.push(player);
            continue;
        }

        // Split into parts and correct each (await the async corrections)
        const parts = fullName.trim().split(/\s+/);
        const correctedParts = await Promise.all(
            parts.map(part => correctNameWithOpenAI(part))
        );

        corrected.push({
            ...player,
            [nameField]: correctedParts.join(' ')
        });
    }

    return corrected;
}

async function fetchWithFallback(url, seasonId, dataType, nameField, previousMetadata) {
    try {
        const data = await fetchNHLData(url);
        if (!Array.isArray(data?.data)) {
            throw new Error(`Malformed ${dataType} stats response`);
        }
        const cachedData = loadCachedData(seasonId, dataType, true);
        if (cachedData && data.data.length < cachedData.length) {
            throw new Error(`Incomplete ${dataType} stats response would replace existing results`);
        }
        return { players: await processPlayers(data.data, nameField), updatedAt: new Date().toISOString() };
    } catch (error) {
        if (CACHE_FALLBACK_ENABLED) {
            console.error(`   ❌ API failed: ${error.message}`);
            console.warn(`   ↩️  Falling back to cached ${dataType} data...`);
            const cachedData = loadCachedData(seasonId, dataType);
            if (cachedData) {
                return {
                    players: cachedData,
                    updatedAt: previousMetadata?.[`${dataType}UpdatedAt`] ?? previousMetadata?.updatedAt ?? null,
                };
            }
        }
        throw error;
    }
}

/**
 * Main function
 */
async function main() {
    console.log('🏒 Starting pre-build: Fetching player stats with Finnish name corrections...\n');

    const seasonId = getSeasonId();
    const previousMetadata = loadPreviousMetadata(seasonId);
    console.log(`📅 Season: ${seasonId}`);

    // Ensure output directory exists
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // Fetch Finnish skaters
    console.log('\n📊 Fetching skaters...');
    const skaterUrl = `https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D%5D&start=0&limit=500&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`;

    const skatersResult = await fetchWithFallback(skaterUrl, seasonId, 'skaters', 'skaterFullName', previousMetadata);
    console.log(`   ✅ ${skatersResult.players.length} skaters processed`);

    // Fetch Finnish goalies
    console.log('\n📊 Fetching goalies...');
    const goalieUrl = `https://api.nhle.com/stats/rest/en/goalie/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22wins%22,%22direction%22:%22DESC%22%7D%5D&start=0&limit=100&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`;

    const goaliesResult = await fetchWithFallback(goalieUrl, seasonId, 'goalies', 'goalieFullName', previousMetadata);
    console.log(`   ✅ ${goaliesResult.players.length} goalies processed`);

    // Fetch Finnish playoff skaters
    console.log('\n🏆 Fetching playoff skaters...');
    const playoffSkaterUrl = `https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D%5D&start=0&limit=500&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D3%20and%20seasonId%3D${seasonId}`;

    const playoffSkatersResult = await fetchWithFallback(playoffSkaterUrl, seasonId, 'playoff-skaters', 'skaterFullName', previousMetadata);
    console.log(`   ✅ ${playoffSkatersResult.players.length} playoff skaters processed`);

    // Fetch Finnish playoff goalies
    console.log('\n🏆 Fetching playoff goalies...');
    const playoffGoalieUrl = `https://api.nhle.com/stats/rest/en/goalie/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22wins%22,%22direction%22:%22DESC%22%7D%5D&start=0&limit=100&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D3%20and%20seasonId%3D${seasonId}`;

    const playoffGoaliesResult = await fetchWithFallback(playoffGoalieUrl, seasonId, 'playoff-goalies', 'goalieFullName', previousMetadata);
    console.log(`   ✅ ${playoffGoaliesResult.players.length} playoff goalies processed`);

    // Collect every response before writing; a missing fallback leaves the previous snapshot intact.
    const results = [
        ['skaters', skatersResult],
        ['goalies', goaliesResult],
        ['playoff-skaters', playoffSkatersResult],
        ['playoff-goalies', playoffGoaliesResult],
    ];
    for (const [type, result] of results) {
        const file = path.join(OUTPUT_DIR, `${type}-${seasonId}.json`);
        fs.writeFileSync(file, JSON.stringify(result.players, null, 2));
        console.log(`   💾 Saved: ${file}`);
    }

    // Save metadata
    const timestamps = results.map(([, result]) => result.updatedAt);
    const metadata = {
        seasonId,
        updatedAt: timestamps.every(Boolean) ? timestamps.sort()[0] : null,
        skatersUpdatedAt: skatersResult.updatedAt,
        goaliesUpdatedAt: goaliesResult.updatedAt,
        'playoff-skatersUpdatedAt': playoffSkatersResult.updatedAt,
        'playoff-goaliesUpdatedAt': playoffGoaliesResult.updatedAt,
        skaterCount: skatersResult.players.length,
        goalieCount: goaliesResult.players.length,
        playoffSkaterCount: playoffSkatersResult.players.length,
        playoffGoalieCount: playoffGoaliesResult.players.length
    };

    const metaFile = path.join(OUTPUT_DIR, 'metadata.json');
    fs.writeFileSync(metaFile, JSON.stringify(metadata, null, 2));
    console.log(`   💾 Saved: ${metaFile}`);

    console.log('\n✅ Pre-build complete!');
}

module.exports = { main };

if (require.main === module) {
    main().catch(error => {
        console.error('\n❌ Pre-build failed:', error);
        process.exit(1);
    });
}
