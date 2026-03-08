#!/usr/bin/env node
/**
 * Puppeteer-based scraper v3 for Finnish prospects
 * 
 * Improvements:
 * - Cookie consent handling for Liiga/SHL
 * - Better wait strategies for React/Angular rendering
 * - API-based scraping for HockeyTech leagues
 * - League-specific selectors
 * 
 * Usage: node scripts/scraper-puppeteer-v2.cjs [league]
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const OUTPUT_DIR = path.join(__dirname, '../static/data/leagues');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'league_prospects_v2.json');

// League configurations with improved settings
// Note: Liiga, SHL require API access which is not publicly available
// Focusing on HockeyTech leagues which work well
const leagueConfigs = [
    { 
        name: 'AHL', 
        type: 'hockeytech', 
        url: 'https://www.theahl.com/stats/player-stats',
        waitTime: 12000
    },
    { 
        name: 'ECHL', 
        type: 'hockeytech', 
        url: 'https://www.echl.com/stats/player-stats',
        waitTime: 12000
    },
    { 
        name: 'NAHL', 
        type: 'hockeytech', 
        url: 'https://nahl.com/skater-stats',
        waitTime: 12000
    },
    { 
        name: 'OHL', 
        type: 'hockeytech', 
        url: 'https://ontariohockeyleague.com/stats/players',
        waitTime: 12000
    },
    { 
        name: 'WHL', 
        type: 'hockeytech', 
        url: 'https://whl.ca/stats/players',
        waitTime: 12000
    },
    { 
        name: 'QMJHL', 
        type: 'hockeytech', 
        url: 'https://theqmjhl.ca/stats/players',
        waitTime: 12000
    },
    // USHL - try alternate
    // { name: 'USHL', type: 'hockeytech', url: 'https://www.ushl.com/stats/players', waitTime: 12000 },
    // These require API access - marked for future improvement
    // { name: 'Liiga', type: 'api', url: 'https://liiga.fi/api/v2/', waitTime: 5000 },
    // { name: 'SHL', type: 'api', url: 'https://www.shl.se/', waitTime: 5000 },
    // { name: 'KHL', type: 'api', url: 'https://en.khl.ru/', waitTime: 5000 }
];

// Finnish name patterns
const finnishPatterns = [
    /nen$/, /lä$/, /kkä$/, /pää$/, /sörum$/, /sorum$/, /kangas$/, 
    /koivu$/, /mäki$/, /vuori$/, /salmi$/, /lahti$/, /aho$/, /niemi$/, 
    /järvi$/, /linna$/, /koski$/, /lampi$/, /kari$/, /selänne$/,
    /granlund$/, /laine$/, /riano$/, /rantanen$/, /hintz$/, /kotkaniemi$/,
    /lundell$/, /heiskanen$/, /pulkkinen$/, /teräväinen$/, /kapanen$/,
    /leppänen$/, /tuulola$/, /rasanen$/, /hyry$/, /sandin$/, /brodzinski$/
];

const finnishChars = /[äöåÄÖÅ]/;

// Detect if a name is likely Finnish
function isFinnishName(name) {
    if (!name || name.length < 3) return false;
    const nl = name.toLowerCase().trim();
    if (finnishChars.test(nl)) return true;
    return finnishPatterns.some(p => p.test(nl));
}

// HTTP helper for API calls
function httpGet(url) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        client.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

// Cookie consent handler - improved version
async function handleCookieConsent(page) {
    try {
        // Wait a bit for consent banner to appear
        await new Promise(r => setTimeout(r, 2000));
        
        // Try to find and click accept buttons by text content
        const acceptTexts = ['HYVÄKSY', 'ACCEPT', 'Accept', 'Acceptera', 'Godkänn', 'GODKÄNN', 'ACCEPT ALL', 'Agree', 'I agree'];
        
        for (const text of acceptTexts) {
            try {
                const buttons = await page.evaluateHandle((t) => {
                    return Array.from(document.querySelectorAll('button')).filter(b => b.textContent.includes(t));
                }, text);
                
                const count = await buttons.evaluate(b => b.length);
                if (count > 0) {
                    await buttons.evaluate(b => b[0].click());
                    console.log('    Clicked cookie button:', text);
                    await new Promise(r => setTimeout(r, 1500));
                    break;
                }
            } catch (e) {
                // Continue
            }
        }
    } catch (e) {
        console.log('    Cookie handling note:', e.message);
    }
}

// Scrape HockeyTech-based leagues via their API
async function scrapeHockeyTechLeague(browser, config) {
    console.log(`  Using HockeyTech approach for ${config.name}`);
    
    let page;
    try {
        page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        await page.setViewport({ width: 1920, height: 1080 });
        
        console.log('  Loading page...');
        await page.goto(config.url, { waitUntil: 'networkidle2', timeout: 60000 }).catch(e => {
            console.log('  Navigation note: ' + e.message);
        });
        
        // Handle cookie consent if present
        await handleCookieConsent(page);
        
        console.log('  Waiting for content to render...');
        await new Promise(resolve => setTimeout(resolve, config.waitTime));
        
        // Extract player data using multiple strategies
        const players = await page.evaluate(() => {
            const players = [];
            
            // Finnish name detection - improved to reduce false positives
            function isFinnishName(name) {
                if (!name || name.length < 3) return false;
                // Clean up name - remove extra whitespace
                const nl = name.toLowerCase().replace(/\s+/g, ' ').trim();
                
                // First check for Finnish characters - strong indicator
                if (/[äöåÄÖÅ]/.test(name)) return true;
                
                // Strong Finnish surname patterns (most reliable)
                const strongPatterns = [
                    /nen$/, /lä$/, /kkä$/, /pää$/, /sörum$/, /sorum$/, // Common endings
                    /mäki$/, /niemi$/, /järvi$/, /aho$/, // Very common
                    /koivu$/, /vuori$/, /salmi$/, /lahti$/, // Nature-based
                    /kangas$/, /linna$/, /koski$/, /lampi$/ // Common
                ];
                
                // Check if name ends with strong Finnish pattern
                for (const pattern of strongPatterns) {
                    if (pattern.test(nl)) return true;
                }
                
                // Also check for known Finnish first names
                const finnishFirstNames = [
                    'aleksi', 'antti', 'arto', 'eero', 'erkki', 'esa', 'hani', 'jekku',
                    'jonathan', 'joni', 'jussi', 'juuso', 'kala', 'karri', 'kasperi',
                    'kimi', 'klaus', 'kuisma', 'lauri', 'leevi', 'leo', 'lucas', 'marcus',
                    'matias', 'mika', 'miko', 'niklas', 'niku', 'olli', 'onni', 'osmo',
                    'otto', 'pasi', 'pekka', 'peteri', 'petri', 'pikk', 'rauli', 'rikas',
                    'risto', 'roope', 'sebastian', 'teemu', 'tero', 'toni', 'topi',
                    'turo', 'ville', 'viljami', 'villi', 'eetu', 'aaro', 'aarni'
                ];
                
                const parts = nl.split(' ');
                if (parts.length >= 2) {
                    const firstName = parts[0];
                    const lastName = parts[parts.length - 1];
                    
                    // If we have a Finnish first name OR a strong Finnish surname
                    if (finnishFirstNames.includes(firstName)) return true;
                    if (strongPatterns.some(p => p.test(lastName))) return true;
                }
                
                return false;
            }
            
            // Strategy 1: Look for ht-table class (HockeyTech tables)
            let tables = document.querySelectorAll('.ht-table, table.ht-table');
            console.log('    Found ht-tables:', tables.length);
            
            // If no ht-table, look for any table with player-like headers
            if (tables.length === 0) {
                tables = document.querySelectorAll('table');
                console.log('    Found any tables:', tables.length);
            }
            
            for (const table of tables) {
                const headers = Array.from(table.querySelectorAll('th, thead td'));
                const headerText = headers.map(h => h.textContent.toLowerCase().trim());
                
                // Check if this looks like a player stats table
                const hasName = headerText.some(h => /name|player|pelaaja|namn/i.test(h));
                const hasStats = headerText.some(h => /goal|assist|point|gp|game/i.test(h));
                
                if (!hasName || !hasStats) continue;
                
                // Find column indices
                let nameIdx = headerText.findIndex(h => /name|player|pelaaja|namn/i.test(h));
                let teamIdx = headerText.findIndex(h => /team|lag|team/i.test(h));
                let posIdx = headerText.findIndex(h => /pos|position/i.test(h));
                let gpIdx = headerText.findIndex(h => /gp|game/i.test(h));
                let gIdx = headerText.findIndex(h => /g$|^g$|goal/i.test(h));
                let aIdx = headerText.findIndex(h => /a$|^a$|assist/i.test(h));
                let ptsIdx = headerText.findIndex(h => /pts|point/i.test(h));
                let natIdx = headerText.findIndex(h => /nat|country|land/i.test(h));
                
                // Default to common positions if not found
                if (nameIdx === -1) nameIdx = 0;
                if (teamIdx === -1) teamIdx = 1;
                if (posIdx === -1) posIdx = 2;
                
                const rows = table.querySelectorAll('tbody tr, tr');
                console.log('    Processing', rows.length, 'rows');
                
                for (const row of rows) {
                    const cells = row.querySelectorAll('td, th');
                    if (cells.length < 5) continue;
                    
                    const name = cells[nameIdx]?.textContent?.trim() || '';
                    if (!name || name.length < 2) continue;
                    
                    // Check nationality if available
                    if (natIdx >= 0 && cells[natIdx]) {
                        const nat = cells[natIdx].textContent.trim();
                        if (nat && !/FIN|Finland/i.test(nat)) continue;
                    }
                    
                    // Otherwise check if name is Finnish - use the function for consistency
                    // Clean name first
                    const cleanName = name.replace(/\s+/g, ' ').trim();
                    if (!isFinnishName(cleanName)) continue;
                    
                    const player = {
                        name: name,
                        team: teamIdx >= 0 ? cells[teamIdx]?.textContent?.trim() || '' : '',
                        position: posIdx >= 0 ? cells[posIdx]?.textContent?.trim() || '' : '',
                        games: gpIdx >= 0 ? cells[gpIdx]?.textContent?.trim() || '0' : '0',
                        goals: gIdx >= 0 ? cells[gIdx]?.textContent?.trim() || '0' : '0',
                        assists: aIdx >= 0 ? cells[aIdx]?.textContent?.trim() || '0' : '0',
                        points: ptsIdx >= 0 ? cells[ptsIdx]?.textContent?.trim() || '0' : '0'
                    };
                    
                    players.push(player);
                }
            }
            
            // Strategy 2: Look for React-rendered content
            if (players.length === 0) {
                const playerLinks = document.querySelectorAll('a[href*="/player"], a[href*="/player-stats"]');
                console.log('    Found player links:', playerLinks.length);
                
                for (const link of playerLinks) {
                    const name = link.textContent?.trim();
                    if (name && isFinnishName(name)) {
                        players.push({
                            name: name,
                            team: '',
                            position: '',
                            games: '0',
                            goals: '0',
                            assists: '0',
                            points: '0'
                        });
                    }
                }
            }
            
            return players;
        });
        
        console.log(`  Found ${players.length} Finnish players`);
        
        await page.close();
        return players;
        
    } catch (error) {
        console.log(`  Error: ${error.message}`);
        if (page) await page.close();
        return [];
    }
}

// Scrape React-based leagues with cookie consent
async function scrapeReactLeague(browser, config) {
    console.log(`  Using React approach for ${config.name}`);
    
    let page;
    try {
        page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        await page.setViewport({ width: 1920, height: 1080 });
        
        console.log('  Loading page...');
        await page.goto(config.url, { waitUntil: 'networkidle2', timeout: 60000 }).catch(e => {
            console.log('  Navigation note: ' + e.message);
        });
        
        // Handle cookie consent
        await handleCookieConsent(page);
        
        console.log('  Waiting for React to render...');
        await new Promise(resolve => setTimeout(resolve, config.waitTime));
        
        // Scroll to trigger lazy loading
        await page.evaluate(() => {
            window.scrollTo(0, document.body.scrollHeight / 2);
        });
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Extract player data
        const players = await page.evaluate(() => {
            const players = [];
            
            // Finnish name detection (must be inside evaluate)
            function isFinnishName(name) {
                if (!name || name.length < 3) return false;
                const nl = name.toLowerCase().trim();
                if (/[äöåÄÖÅ]/.test(nl)) return true;
                const finnishPatterns = [/nen$/, /lä$/, /kkä$/, /pää$/, /sörum$/, /sorum$/, /kangas$/, /koivu$/, /mäki$/, /vuori$/, /salmi$/, /lahti$/, /aho$/, /niemi$/, /järvi$/];
                return finnishPatterns.some(p => p.test(nl));
            }
            
            // Look for tables in the React-rendered content
            const tables = document.querySelectorAll('table');
            console.log('    Found tables:', tables.length);
            
            for (const table of tables) {
                const headers = Array.from(table.querySelectorAll('th'));
                const headerText = headers.map(h => h.textContent.toLowerCase().trim());
                
                const hasName = headerText.some(h => /player|name|pelaaja|namn/i.test(h));
                const hasStats = headerText.some(h => /goal|assist|point|gp/i.test(h));
                
                if (!hasName || !hasStats) continue;
                
                let nameIdx = headerText.findIndex(h => /player|name|pelaaja|namn/i.test(h));
                let teamIdx = headerText.findIndex(h => /team|lag|team/i.test(h));
                let posIdx = headerText.findIndex(h => /pos/i.test(h));
                let gpIdx = headerText.findIndex(h => /gp|game/i.test(h));
                let gIdx = headerText.findIndex(h => /g$|^g$/i.test(h));
                let aIdx = headerText.findIndex(h => /a$|^a$/i.test(h));
                let ptsIdx = headerText.findIndex(h => /pts|point/i.test(h));
                
                const rows = table.querySelectorAll('tbody tr, tr');
                
                for (const row of rows) {
                    const cells = row.querySelectorAll('td');
                    if (cells.length < 4) continue;
                    
                    let idx = nameIdx >= 0 ? nameIdx : 0;
                    const name = cells[idx]?.textContent?.trim() || '';
                    
                    if (!name || name.length < 3) continue;
                    
                    // Check if Finnish
                    if (!isFinnishName(name)) continue;
                    
                    players.push({
                        name: name,
                        team: teamIdx >= 0 ? cells[teamIdx]?.textContent?.trim() || '' : '',
                        position: posIdx >= 0 ? cells[posIdx]?.textContent?.trim() || '' : '',
                        games: gpIdx >= 0 ? cells[gpIdx]?.textContent?.trim() || '0' : '0',
                        goals: gIdx >= 0 ? cells[gIdx]?.textContent?.trim() || '0' : '0',
                        assists: aIdx >= 0 ? cells[aIdx]?.textContent?.trim() || '0' : '0',
                        points: ptsIdx >= 0 ? cells[ptsIdx]?.textContent?.trim() || '0' : '0'
                    });
                }
            }
            
            // Try to find player cards/rows in div structures
            if (players.length === 0) {
                const playerElements = document.querySelectorAll('[class*="player"], [class*="Player"]');
                console.log('    Found player elements:', playerElements.length);
                
                for (const el of playerElements) {
                    const text = el.textContent || '';
                    const nameMatch = text.match(/([A-ZÄÖÅ][a-zäöåéèëêùûüôîïâáà]+\s+[A-ZÄÖÅ][a-zäöåéèëêùûüôîïâáà]+)/);
                    if (nameMatch && isFinnishName(nameMatch[1])) {
                        players.push({
                            name: nameMatch[1],
                            team: '',
                            position: '',
                            games: '0',
                            goals: '0',
                            assists: '0',
                            points: '0'
                        });
                    }
                }
            }
            
            return players;
        });
        
        console.log(`  Found ${players.length} Finnish players`);
        
        await page.close();
        return players;
        
    } catch (error) {
        console.log(`  Error: ${error.message}`);
        if (page) await page.close();
        return [];
    }
}

// Main scraping function
async function scrapeLeague(browser, config) {
    console.log(`\n--- ${config.name} ---`);
    console.log(`  URL: ${config.url}`);
    
    if (config.type === 'hockeytech') {
        return scrapeHockeyTechLeague(browser, config);
    } else if (config.type === 'react-cookie') {
        return scrapeReactLeague(browser, config);
    } else if (config.type === 'khl') {
        return scrapeReactLeague(browser, config); // Use same approach for now
    }
    
    return [];
}

async function main() {
    const args = process.argv.slice(2);
    const targetLeague = args[0]?.toUpperCase();
    
    console.log('='.repeat(60));
    console.log('Puppeteer Scraper v3 - Finnish Prospects');
    console.log('='.repeat(60));
    console.log(`Time: ${new Date().toISOString()}`);
    
    let leaguesToScrape = leagueConfigs;
    if (targetLeague) {
        leaguesToScrape = leagueConfigs.filter(l => l.name.toUpperCase() === targetLeague);
        if (leaguesToScrape.length === 0) {
            console.log(`\nUnknown league: ${targetLeague}`);
            console.log('Available leagues:', leagueConfigs.map(l => l.name).join(', '));
            process.exit(1);
        }
    }
    
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled']
    });
    
    const results = {
        generated_at: new Date().toISOString(),
        season: '2025-2026',
        data_source: 'puppeteer-v2',
        scraper_version: '3.0',
        leagues: {},
        players: []
    };
    
    for (const league of leaguesToScrape) {
        console.log(`\n[${leaguesToScrape.indexOf(league) + 1}/${leaguesToScrape.length}] Processing ${league.name}...`);
        
        const players = await scrapeLeague(browser, league);
        results.leagues[league.name.toLowerCase()] = { count: players.length, url: league.url, type: league.type };
        
        for (const player of players) {
            results.players.push({ ...player, league: league.name, source: 'puppeteer-v2', scraped_at: new Date().toISOString() });
        }
        
        // Wait between leagues
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    await browser.close();
    
    // Sort by points
    results.players.sort((a, b) => (parseInt(b.points) || 0) - (parseInt(a.points) || 0));
    results.total_players = results.players.length;
    
    console.log('\n' + '='.repeat(60));
    console.log('SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total Finnish players: ${results.total_players}`);
    console.log('\nBy league:');
    for (const [league, data] of Object.entries(results.leagues)) {
        console.log(`  ${league.toUpperCase()}: ${data.count} players`);
    }
    
    if (results.players.length > 0) {
        console.log('\nTop 10 Finnish prospects:');
        for (let i = 0; i < Math.min(10, results.players.length); i++) {
            const p = results.players[i];
            console.log(`  ${i + 1}. ${p.name} (${p.league}, ${p.team}): ${p.goals}G + ${p.assists}A = ${p.points}P`);
        }
    }
    
    // Save results
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(results, null, 2));
    console.log(`\n✓ Data saved to ${OUTPUT_FILE}`);
    
    return results;
}

main().catch(console.error);
