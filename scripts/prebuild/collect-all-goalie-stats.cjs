#!/usr/bin/env node

/**
 * Unified goalie stats collector.
 * Combines NHL/AHL/ECHL stats with European league stats (Liiga, Mestis, SHL, etc.)
 * into a single all-goalies.json file.
 *
 * Usage: node scripts/prebuild/collect-all-goalie-stats.cjs
 */

const fs = require('fs');
const path = require('path');

// Configuration
const STATS_DIR = path.join(process.cwd(), 'static/data/player-stats');
const LEAGUES_DIR = path.join(process.cwd(), 'static/data/leagues');
const OUTPUT_FILE = path.join(STATS_DIR, 'all-goalies.json');
const CURRENT_SEASON = '20252026';

function normalizeName(name) {
    if (!name || typeof name !== 'string') return '';
    return name.toLowerCase().trim().replace(/[^a-zäöå\s]/gi, '');
}

function loadJson(filePath) {
    if (!fs.existsSync(filePath)) {
        console.warn(`  ⚠️  File not found: ${filePath}`);
        return null;
    }
    try {
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (e) {
        console.warn(`  ⚠️  Failed to parse: ${filePath}`);
        return null;
    }
}

function normalizeGoalie(data) {
    return {
        id: String(data.playerId || data.player_id || data.id || ''),
        name: data.goalieFullName || data.name || '',
        team: data.teamAbbrevs || data.team || '',
        league: data.league || '',
        gp: data.gamesPlayed || data.games_played || 0,
        savePct: data.savePct || data.savePercentage || data.save_percentage || null,
        gaa: data.goalsAgainstAverage || data.goals_against_average || data.goalsAgainstAvg || null,
        shutouts: data.shutouts || data.shutOut || 0,
        source: data.source || 'unknown'
    };
}

function mergeGoalies(nhlGoalies, leagueGoalies) {
    const byName = new Map();

    // Add NHL goalies first
    for (const g of nhlGoalies) {
        const normalized = normalizeName(g.goalieFullName);
        const goalie = normalizeGoalie(g);
        goalie.source = 'nhl-api';
        byName.set(normalized, goalie);
    }

    // Merge/add league goalies
    for (const g of leagueGoalies) {
        const normalized = normalizeName(g.name);
        const goalie = normalizeGoalie(g);
        goalie.source = g.source_league || g.source || 'league';

        const existing = byName.get(normalized);
        if (existing) {
            // Prefer data with more fields populated
            if (goalie.savePct !== null && existing.savePct === null) {
                existing.savePct = goalie.savePct;
            }
            if (goalie.gaa !== null && existing.gaa === null) {
                existing.gaa = goalie.gaa;
            }
            if (goalie.shutouts > 0 && existing.shutouts === 0) {
                existing.shutouts = goalie.shutouts;
            }
            if (goalie.gp > existing.gp) {
                existing.gp = goalie.gp;
            }
            // Prefer specific league data if NHL has 0 stats
            if (existing.savePct === 0 || existing.savePct === null) {
                existing.savePct = goalie.savePct;
                existing.gaa = goalie.gaa;
                existing.shutouts = goalie.shutouts;
                existing.team = goalie.team;
                existing.league = goalie.league;
                existing.source = goalie.source;
            }
        } else {
            byName.set(normalized, goalie);
        }
    }

    return Array.from(byName.values());
}

async function main() {
    console.log('🏒 Collecting unified goalie stats...\n');

    const nhlFile = path.join(STATS_DIR, `goalies-${CURRENT_SEASON}.json`);
    const leagueFile = path.join(LEAGUES_DIR, 'league_prospects_official.json');

    // Load NHL goalies
    console.log('📊 Loading NHL/AHL/ECHL goalies...');
    const nhlData = loadJson(nhlFile);
    const nhlGoalies = nhlData || [];
    console.log(`   Found ${nhlGoalies.length} NHL goalies`);

    // Load league goalies
    console.log('📊 Loading European league goalies...');
    const leagueData = loadJson(leagueFile);
    let leagueGoalies = [];
    if (leagueData && leagueData.players) {
        leagueGoalies = leagueData.players.filter(p => 
            p.position === 'G' && 
            (p.save_percentage || p.goals_against_average || p.shutouts)
        );
    }
    console.log(`   Found ${leagueGoalies.length} league goalies with stats`);

    // Merge
    console.log('\n🔀 Merging goalies by name...');
    const allGoalies = mergeGoalies(nhlGoalies, leagueGoalies);
    console.log(`   Total unique goalies: ${allGoalies.length}`);

    // Filter to Finnish only
    const finnishGoalies = allGoalies.filter(g => {
        // NHL goalies are already Finnish (from NHL API filter)
        if (g.source === 'nhl-api') return true;
        // For league goalies, check if they have meaningful stats
        return g.savePct !== null || g.gaa !== null || g.shutouts > 0;
    });
    console.log(`   Finnish goalies with stats: ${finnishGoalies.length}`);

    // Sort by save percentage (best first), nulls last
    finnishGoalies.sort((a, b) => {
        const aPct = a.savePct || 0;
        const bPct = b.savePct || 0;
        if (aPct === 0 && bPct === 0) return 0;
        if (aPct === 0) return 1;
        if (bPct === 0) return -1;
        return bPct - aPct;
    });

    // Output
    const output = {
        updatedAt: new Date().toISOString(),
        season: CURRENT_SEASON,
        total: finnishGoalies.length,
        goalies: finnishGoalies
    };

    if (!fs.existsSync(STATS_DIR)) {
        fs.mkdirSync(STATS_DIR, { recursive: true });
    }
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
    console.log(`\n💾 Saved to: ${OUTPUT_FILE}`);

    // Show some examples
    console.log('\n📋 Sample goalies:');
    finnishGoalies.slice(0, 5).forEach(g => {
        const sv = g.savePct ? g.savePct.toFixed(3) : 'N/A';
        const ga = g.gaa ? g.gaa.toFixed(2) : 'N/A';
        console.log(`   ${g.name} (${g.league}): GP=${g.gp}, SV%=${sv}, GAA=${ga}, SO=${g.shutouts} [${g.source}]`);
    });

    console.log('\n✅ Done!');
}

main().catch(err => {
    console.error('❌ Error:', err);
    process.exit(1);
});
