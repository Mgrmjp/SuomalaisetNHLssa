#!/usr/bin/env node
/**
 * Puppeteer-based scraper for official league websites
 * Uses JavaScript rendering to get dynamic content
 */
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '../../static/data/leagues');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'league_prospects_puppeteer.json');

// Finnish name detection
function isFinnish(name) {
    if (!name) return false;
    const finnishChars = ['ä', 'ö', 'å', 'Ä', 'Ö', 'Å'];
    if (finnishChars.some(c => name.includes(c))) return true;
    
    const parts = name.split(' ');
    const lastName = parts[parts.length - 1];
    if (lastName && lastName.endsWith('nen')) return true;
    if (lastName && ['lä', 'lä', 'kkä', 'kkö', 'pää', 'rvi'].some(e => lastName.endsWith(e))) return true;
    
    return false;
}

// League configurations
const leagues = [
    {
        name: 'AHL',
        url: 'https://www.theahl.com/stats/players',
        tableSelector: 'table.stats-table, table.player-stats, table',
        nameSelector: 'td.player a, td:nth-child(2) a, td a',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const nameCell = cells[1];
            const name = nameCell?.textContent?.trim() || nameCell?.querySelector('a')?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
    {
        name: 'ECHL',
        url: 'https://www.echl.com/stats/players',
        tableSelector: 'table',
        nameSelector: 'td:nth-child(2)',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const name = cells[1]?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
    {
        name: 'USHL',
        url: 'https://www.ushl.com/stats/players',
        tableSelector: 'table',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const name = cells[1]?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
    {
        name: 'NAHL',
        url: 'https://nahl.com/stats/players',
        tableSelector: 'table',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const name = cells[1]?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
    {
        name: 'OHL',
        url: 'https://ontariohockeyleague.com/stats/players',
        tableSelector: 'table',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const name = cells[1]?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
    {
        name: 'WHL',
        url: 'https://whl.ca/stats/players',
        tableSelector: 'table',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const name = cells[1]?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
    {
        name: 'QMJHL',
        url: 'https://theqmjhl.ca/stats/players',
        tableSelector: 'table',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const name = cells[1]?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
    {
        name: 'KHL',
        url: 'https://en.khl.ru/stats/players/',
        tableSelector: 'table',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const name = cells[1]?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
    {
        name: 'SHL',
        url: 'https://www.shl.se/statistik/spelare/',
        tableSelector: 'table',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const name = cells[1]?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
    {
        name: 'Liiga',
        url: 'https://liiga.fi/tilastot/pelaajat/',
        tableSelector: 'table',
        extractRow: (row) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) return null;
            const name = cells[1]?.textContent?.trim();
            if (!name || !isFinnish(name)) return null;
            return {
                name,
                team: cells[2]?.textContent?.trim() || '',
                games: cells[3]?.textContent?.trim() || '0',
                goals: cells[4]?.textContent?.trim() || '0',
                assists: cells[5]?.textContent?.trim() || '0',
                points: cells[6]?.textContent?.trim() || '0',
            };
        }
    },
];

async function scrapeLeague(browser, league) {
    console.log(`\n--- ${league.name} ---`);
    console.log(`  URL: ${league.url}`);
    
    try {
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
        
        // Set timeout for navigation
        await page.goto(league.url, { waitUntil: 'networkidle2', timeout: 30000 });
        
        // Wait for tables to load
        await page.waitForSelector(league.tableSelector, { timeout: 10000 }).catch(() => {});
        
        // Get page content after JS rendering
        const html = await page.content();
        
        // Parse with DOM
        const players = await page.evaluate((leagueCfg) => {
            const tables = document.querySelectorAll(leagueCfg.tableSelector);
            const players = [];
            
            for (const table of tables) {
                const rows = table.querySelectorAll('tr');
                for (const row of rows) {
                    const player = leagueCfg.extractRow(row);
                    if (player) {
                        players.push(player);
                    }
                }
            }
            return players;
        }, league);
        
        console.log(`  Found ${players.length} Finnish players`);
        
        await page.close();
        return players;
        
    } catch (error) {
        console.log(`  Error: ${error.message}`);
        return [];
    }
}

async function main() {
    console.log('='.repeat(60));
    console.log('Puppeteer Scraper - Official League Websites');
    console.log('='.repeat(60));
    
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const results = {
        generated_at: new Date().toISOString(),
        season: '2025-2026',
        data_source: 'puppeteer-direct-scrape',
        leagues: {},
        players: []
    };
    
    // Scrape each league
    for (const league of leagues) {
        const players = await scrapeLeague(browser, league);
        results.leagues[league.name.toLowerCase()] = players.length;
        
        for (const player of players) {
            results.players.push({
                ...player,
                league: league.name,
                source: 'puppeteer',
                source_league: league.name.toLowerCase(),
                scraped_at: new Date().toISOString()
            });
        }
    }
    
    // Sort by points
    results.players.sort((a, b) => {
        const aPoints = parseInt(a.points) || 0;
        const bPoints = parseInt(b.points) || 0;
        return bPoints - aPoints;
    });
    
    results.total_players = results.players.length;
    
    await browser.close();
    
    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total Finnish players: ${results.total_players}`);
    console.log('\nBy league:');
    for (const [league, count] of Object.entries(results.leagues)) {
        console.log(`  ${league.toUpperCase()}: ${count} players`);
    }
    
    if (results.players.length > 0) {
        console.log('\nTop 10 Finnish prospects:');
        for (let i = 0; i < Math.min(10, results.players.length); i++) {
            const p = results.players[i];
            console.log(`  ${i + 1}. ${p.name} (${p.league}, ${p.team}): ${p.goals}G + ${p.assists}A = ${p.points}P`);
        }
    }
    
    // Save
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(results, null, 2));
    console.log(`\n✓ Data saved to ${OUTPUT_FILE}`);
    
    return results;
}

main().catch(console.error);
