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
const CURRENT_SEASON = '20252026'; // Will be calculated dynamically

/**
 * Calculate current NHL season ID
 */
function getSeasonId() {
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
 * Fetch data from NHL API
 */
async function fetchNHLData(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
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
                model: 'gpt-4o-mini',
                messages: [{
                    role: 'user',
                    content: `Correct this Finnish name if needed. Only fix obvious Finnish letter patterns (ä, ö, å).

Name: "${name}"

Return ONLY the corrected name. If correct, return unchanged.`
                }],
                temperature: 0.1,
                max_tokens: 50
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

/**
 * Main function
 */
async function main() {
    console.log('🏒 Starting pre-build: Fetching player stats with Finnish name corrections...\n');

    const seasonId = getSeasonId();
    console.log(`📅 Season: ${seasonId}`);

    // Ensure output directory exists
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // Fetch Finnish skaters
    console.log('\n📊 Fetching skaters...');
    const skaterUrl = `https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D%5D&start=0&limit=500&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`;

    const skatersData = await fetchNHLData(skaterUrl);
    const correctedSkaters = await processPlayers(skatersData.data || [], 'skaterFullName');

    console.log(`   ✅ ${correctedSkaters.length} skaters processed`);

    // Save skaters
    const skatersFile = path.join(OUTPUT_DIR, `skaters-${seasonId}.json`);
    fs.writeFileSync(skatersFile, JSON.stringify(correctedSkaters, null, 2));
    console.log(`   💾 Saved: ${skatersFile}`);

    // Fetch Finnish goalies
    console.log('\n📊 Fetching goalies...');
    const goalieUrl = `https://api.nhle.com/stats/rest/en/goalie/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22wins%22,%22direction%22:%22DESC%22%7D%5D&start=0&limit=100&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`;

    const goaliesData = await fetchNHLData(goalieUrl);
    const correctedGoalies = await processPlayers(goaliesData.data || [], 'goalieFullName');

    console.log(`   ✅ ${correctedGoalies.length} goalies processed`);

    // Save goalies
    const goaliesFile = path.join(OUTPUT_DIR, `goalies-${seasonId}.json`);
    fs.writeFileSync(goaliesFile, JSON.stringify(correctedGoalies, null, 2));
    console.log(`   💾 Saved: ${goaliesFile}`);

    // Save metadata
    const metadata = {
        seasonId,
        updatedAt: new Date().toISOString(),
        skaterCount: correctedSkaters.length,
        goalieCount: correctedGoalies.length
    };

    const metaFile = path.join(OUTPUT_DIR, 'metadata.json');
    fs.writeFileSync(metaFile, JSON.stringify(metadata, null, 2));
    console.log(`   💾 Saved: ${metaFile}`);

    console.log('\n✅ Pre-build complete!');
}

main().catch(error => {
    console.error('\n❌ Pre-build failed:', error);
    process.exit(1);
});
