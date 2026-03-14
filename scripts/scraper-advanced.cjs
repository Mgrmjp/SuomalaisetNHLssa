#!/usr/bin/env node
/**
 * Advanced Puppeteer-based scraper with network interception
 * 
 * Features:
 * - Network request interception to find API endpoints
 * - Sophisticated cookie consent handling for Liiga
 * - Debug mode to analyze page structure
 * - CDP (Chrome DevTools Protocol) support for better control
 * 
 * Usage: 
 *   node scripts/scraper-advanced.cjs [league] [--debug]
 *   node scripts/scraper-advanced.cjs --debug-all
 *   node scripts/scraper-advanced.cjs --find-apis
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const OUTPUT_DIR = path.join(__dirname, '../static/data/leagues');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'league_prospects_advanced.json');

// League configurations including Liiga, SHL, and other European leagues
const leagueConfigs = [
    // European leagues - need special handling
    { 
        name: 'Liiga', 
        type: 'european',
        url: 'https://www.liiga.fi/tilastot/pelaajat',
        cookieUrl: 'https://www.liiga.fi',
        lang: 'fi',
        acceptButtonTexts: ['HYVÄKSY', 'Hyväksy kaikki', 'ACCEPT', 'Sallitse kaikki'],
        waitTime: 15000,
        // Real API endpoint discovered via browser network inspection (March 2026)
        // Season year_end=2026 corresponds to 2025-26 regular season
        apiEndpoints: [
            'https://www.liiga.fi/api/v2/players/stats/summed/2026/2026/runkosarja/false?dataType=basicStats&splitTeams=true&team=',
            'https://www.liiga.fi/api/v2/players/stats/summed/2025/2025/runkosarja/false?dataType=basicStats&splitTeams=true&team=',
        ]
    },
    { 
        name: 'SHL', 
        type: 'european',
        url: 'https://www.shl.se/statistik/spelare',
        cookieUrl: 'https://www.shl.se',
        lang: 'sv',
        acceptButtonTexts: ['ACCEPTERA', 'Godkänn', 'ACCEPT ALL', 'I agree'],
        waitTime: 15000
    },
    { 
        name: 'KHL', 
        type: 'european',
        url: 'https://en.khl.ru/stat/players/2025-2026/',
        cookieUrl: 'https://en.khl.ru',
        lang: 'en',
        acceptButtonTexts: ['ACCEPT', 'Accept', 'AGREE', 'I agree'],
        waitTime: 15000
    },
    { 
        name: 'Mestis', 
        type: 'european',
        url: 'https://www.mestis.fi/tilastot/pelaajat',
        cookieUrl: 'https://www.mestis.fi',
        lang: 'fi',
        acceptButtonTexts: ['HYVÄKSY', 'Hyväksy kaikki', 'ACCEPT'],
        waitTime: 15000
    },
    // HockeyTech leagues
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
];

// Store captured network requests
const networkLogs = [];
const apiEndpoints = new Set();
// Store raw JSON responses captured directly from Puppeteer
const interceptedJsonPayloads = [];
let debugMode = false;
let findApisOnly = false;

// Finnish name detection
function isFinnishName(name) {
    if (!name || name.length < 3) return false;
    const nl = name.toLowerCase().trim();
    if (/[äöåÄÖÅ]/.test(nl)) return true;
    
    const finnishPatterns = [
        /nen$/, /lä$/, /kkä$/, /pää$/, /sörum$/, /sorum$/, /kangas$/, 
        /koivu$/, /mäki$/, /vuori$/, /salmi$/, /lahti$/, /aho$/, /niemi$/, 
        /järvi$/, /linna$/, /koski$/, /lampi$/, /kari$/, /selänne$/,
        /granlund$/, /laine$/, /riano$/, /rantanen$/, /hintz$/, /kotkaniemi$/,
        /lundell$/, /heiskanen$/, /pulkkinen$/, /teräväinen$/, /kapanen$/,
        /leppänen$/, /tuulola$/, /rasanen$/, /hyry$/, /sandin$/, /brodzinski$/,
        /kiviranta$/, /oikarinen$/, /niemi$/, /pajuluoma$/
    ];
    return finnishPatterns.some(p => p.test(nl));
}

// HTTP helper for API calls
function httpGet(url) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        const req = client.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9'
            }
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve({ status: res.statusCode, data }));
        });
        req.on('error', reject);
        req.setTimeout(10000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });
    });
}

// Network request interceptor
function setupNetworkInterception(page, leagueName) {
    networkLogs.length = 0;
    apiEndpoints.clear();
    
    page.on('request', (request) => {
        const url = request.url();
        const method = request.method();
        const resourceType = request.resourceType();
        
        // Log interesting requests
        if (resourceType === 'xhr' || resourceType === 'fetch' || 
            url.includes('/api/') || url.includes('/stats/') || 
            url.includes('.json') || url.includes('/player')) {
            
            const log = {
                league: leagueName,
                url: url,
                method: method,
                resourceType: resourceType,
                timestamp: new Date().toISOString()
            };
            networkLogs.push(log);
            
            // Extract potential API endpoints
            try {
                const urlObj = new URL(url);
                if (url.includes('/api/') || url.includes('json') || url.includes('stats')) {
                    apiEndpoints.add(url);
                }
            } catch (e) {
                // Invalid URL, skip
            }
        }
    });
    
    page.on('response', async (response) => {
        const url = response.url();
        const status = response.status();
        
        if ((status >= 200 && status < 300) && 
            (url.includes('/api/') || url.includes('.json') || url.includes('/stats/') || url.includes('player'))) {
            
            networkLogs.push({
                league: leagueName,
                url: url,
                status: status,
                type: 'response',
                timestamp: new Date().toISOString()
            });
            
            // Intercept JSON body directly
            try {
                const contentType = response.headers()['content-type'] || '';
                if (contentType.includes('application/json')) {
                    const jsonBody = await response.json();
                    
                    // Basic sanity check to ensure it's not a generic translation or config file
                    const rawText = JSON.stringify(jsonBody);
                    if (rawText.includes('player') || rawText.includes('lastName') || rawText.includes('points') || rawText.includes('goals')) {
                        interceptedJsonPayloads.push({
                            url: url,
                            data: jsonBody
                        });
                        console.log(`    [Intercept] Captured JSON payload from ${url.substring(0, 80)}...`);
                    }
                }
            } catch (err) {
                // Ignore errors reading body (e.g. CORS or navigation aborted)
            }
        }
    });
}

// Advanced cookie consent handler using CDP
async function handleCookieConsentAdvanced(page, config) {
    console.log('  Attempting advanced cookie consent handling...');
    
    try {
        // First, try pre-setting common consent cookies
        const commonCookies = [
            { 
                name: 'cookie_consent', 
                value: '1', 
                domain: new URL(config.cookieUrl || config.url).hostname,
                path: '/'
            },
            { 
                name: 'consent', 
                value: 'true', 
                domain: new URL(config.cookieUrl || config.url).hostname,
                path: '/'
            },
            { 
                name: 'eu-consent', 
                value: 'true', 
                domain: new URL(config.cookieUrl || config.url).hostname,
                path: '/'
            }
        ];
        
        for (const cookie of commonCookies) {
            try {
                await page.setCookie(cookie);
                console.log(`    Set cookie: ${cookie.name}`);
            } catch (e) {
                // Cookie might not be applicable
            }
        }
        
        // Wait a moment for page to load
        await new Promise(r => setTimeout(r, 3000));
        
        // Use CDP for more control
        const client = await page.target().createCDPSession();
        
        // Try to evaluate and click consent buttons in the page context
        const buttonTexts = config.acceptButtonTexts || ['ACCEPT', 'ACCEPTERA', 'HYVÄKSY', 'Agree'];
        
        for (const btnText of buttonTexts) {
            try {
                const result = await page.evaluate((text) => {
                    // Try to find button by text
                    const buttons = Array.from(document.querySelectorAll('button, a[role="button"], .cookie-button, [class*="cookie"], [class*="consent"]'));
                    
                    for (const btn of buttons) {
                        if (btn.textContent.toLowerCase().includes(text.toLowerCase())) {
                            btn.click();
                            return { success: true, text: btn.textContent };
                        }
                    }
                    
                    // Try to find by data attributes
                    const consentElements = document.querySelectorAll('[data-consent], [data-accept], [id*="consent"], [class*="consent"]');
                    for (const el of consentElements) {
                        if (el.click) {
                            el.click();
                            return { success: true, text: el.textContent || 'consent-element' };
                        }
                    }
                    
                    return { success: false };
                }, btnText);
                
                if (result.success) {
                    console.log(`    Clicked button: ${result.text}`);
                    await new Promise(r => setTimeout(r, 2000));
                    break;
                }
            } catch (e) {
                console.log(`    Button ${btnText} not found: ${e.message}`);
            }
        }
        
        // Try using CDP to find and click buttons
        try {
            const domResult = await client.send('DOM.getDocument');
            // This is a simplified approach - CDP can do more advanced DOM manipulation
        } catch (e) {
            // CDP DOM might not be available
        }
        
        await client.detach();
        
    } catch (e) {
        console.log(`  Cookie handling note: ${e.message}`);
    }
}

// Wait for dynamic content to render
async function waitForContent(page, config) {
    console.log('  Waiting for content to render...');
    
    // Wait for network to be idle
    try {
        await page.waitForNetworkIdle({ idleTime: 2000, timeout: 10000 });
    } catch (e) {
        console.log('  Network idle timeout, continuing...');
    }
    
    // Additional wait for React/Angular
    await new Promise(resolve => setTimeout(resolve, config.waitTime || 10000));
    
    // Scroll to trigger lazy loading
    try {
        await page.evaluate(() => {
            const scrollStep = window.innerHeight / 3;
            for (let y = 0; y < document.body.scrollHeight; y += scrollStep) {
                window.scrollTo(0, y);
            }
            window.scrollTo(0, 0);
        });
        await new Promise(r => setTimeout(r, 1000));
    } catch (e) {
        // Scroll might fail
    }
}

// Extract Finnish players from page
async function extractPlayers(page, leagueName) {
    const players = await page.evaluate(() => {
        const players = [];
        
        function isFinnishName(name) {
            if (!name || name.length < 3) return false;
            const nl = name.toLowerCase().trim();
            if (/[äöåÄÖÅ]/.test(nl)) return true;
            
            const finnishPatterns = [
                /nen$/, /lä$/, /kkä$/, /pää$/, /sörum$/, /sorum$/, /kangas$/, 
                /koivu$/, /mäki$/, /vuori$/, /salmi$/, /lahti$/, /aho$/, /niemi$/, 
                /järvi$/, /linna$/, /koski$/, /lampi$/, /kari$/, /selänne$/,
                /granlund$/, /laine$/, /riano$/, /rantanen$/, /hintz$/, /kotkaniemi$/,
                /lundell$/, /heiskanen$/, /pulkkinen$/, /teräväinen$/, /kapanen$/
            ];
            return finnishPatterns.some(p => p.test(nl));
        }
        
        // Strategy 1: HockeyTech tables
        let tables = document.querySelectorAll('.ht-table, table.ht-table, table.stats, table.player-stats');
        if (tables.length === 0) {
            tables = document.querySelectorAll('table');
        }
        
        console.log(`    Found ${tables.length} tables`);
        
        for (const table of tables) {
            const headers = Array.from(table.querySelectorAll('th, thead td'));
            const headerText = headers.map(h => h.textContent.toLowerCase().trim());
            
            const hasName = headerText.some(h => /name|player|pelaaja|namn|nimi/i.test(h));
            const hasStats = headerText.some(h => /goal|assist|point|gp|game|o|ottelut|m|maalit|s|sy.t.t|syötöt|p|pisteet/i.test(h));
            
            if (!hasName || !hasStats) continue;
            
            // Special handling for Mestis - the table structure is different
            const isMestisTable = headerText.some(h => /nimi/i.test(h)) && 
                                  headerText.some(h => /joukkue/i.test(h)) &&
                                  headerText.some(h => /pp/i.test(h)) &&
                                  headerText.some(h => /o/i.test(h));
            

            
            let nameIdx = headerText.findIndex(h => /name|player|pelaaja|namn|nimi/i.test(h));
            let teamIdx = headerText.findIndex(h => /team|lag|joukkue/i.test(h));
            let posIdx = headerText.findIndex(h => /pos|pp|pelipaikka/i.test(h));
            let gpIdx = headerText.findIndex(h => /gp|game|o|ottelut/i.test(h));
            let gIdx = headerText.findIndex(h => /g$|^g$|goal|m|maalit/i.test(h));
            let aIdx = headerText.findIndex(h => /a$|^a$|assist|s|sy.t.t|syötöt/i.test(h));
            let ptsIdx = headerText.findIndex(h => /pts|point|p|pisteet/i.test(h));
            let natIdx = headerText.findIndex(h => /nat|country|land|maa/i.test(h));
            
            if (nameIdx === -1) nameIdx = 0;
            
            const rows = table.querySelectorAll('tbody tr, tr');
            
            for (const row of rows) {
                const cells = row.querySelectorAll('td, th');
                if (cells.length < 4) continue;
                
                // For Mestis tables, skip the first data row as it contains headers
                if (isMestisTable) {
                    const firstCellText = cells[0]?.textContent?.trim() || '';
                    if (firstCellText === '#' || firstCellText === 'Nimi') {
                        continue;
                    }
                }
                

                
                // Check nationality first if available
                if (natIdx >= 0 && cells[natIdx]) {
                    const nat = cells[natIdx].textContent.trim();
                    if (nat && !/FIN|Finland|SUOMI/i.test(nat)) continue;
                }
                
                const name = cells[nameIdx]?.textContent?.trim() || '';
                if (!name || name.length < 3) continue;
                
                // If nationality not available, check if name is Finnish
                // For Mestis specifically, include all players since it's a Finnish league
                if (natIdx === -1) {
                    if (isMestisTable) {
                        // Mestis is a Finnish league, include all players
                        // Only exclude clearly non-Finnish names
                        const clearlyNotFinnish = name.split(',')[0].trim(); // Get lastname
                        if (clearlyNotFinnish && !isFinnishName(clearlyNotFinnish) && !isFinnishName(name)) {
                            continue;
                        }
                    } else if (!isFinnishName(name)) {
                        continue;
                    }
                }
                
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
        
        // Strategy 2: React component structure
        if (players.length === 0) {
            // Look for common React data attributes
            const reactElements = document.querySelectorAll('[data-player], [data-player-name], [class*="player-row"], [class*="PlayerRow"]');
            
            for (const el of reactElements) {
                const nameEl = el.querySelector('[class*="name"], .name, .player-name');
                if (nameEl) {
                    const name = nameEl.textContent.trim();
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
        }
        
        // Strategy 3: JSON data in page
        if (players.length === 0) {
            const scripts = document.querySelectorAll('script[type="application/json"]');
            for (const script of scripts) {
                try {
                    const data = JSON.parse(script.textContent);
                    // Look for player arrays in the JSON
                    const findPlayers = (obj) => {
                        if (Array.isArray(obj)) {
                            if (obj[0]?.name || obj[0]?.playerName || obj[0]?.lastName) {
                                return obj;
                            }
                        }
                        if (typeof obj === 'object') {
                            for (const key of Object.keys(obj)) {
                                const result = findPlayers(obj[key]);
                                if (result) return result;
                            }
                        }
                        return null;
                    };
                    
                    const playerArray = findPlayers(data);
                    if (playerArray) {
                        for (const p of playerArray) {
                            const name = p.name || p.playerName || `${p.firstName} ${p.lastName}`;
                            if (name && isFinnishName(name)) {
                                players.push({
                                    name: name,
                                    team: p.team || p.club || '',
                                    position: p.position || p.pos || '',
                                    games: p.games || p.gp || p.gamesPlayed || '0',
                                    goals: p.goals || p.g || '0',
                                    assists: p.assists || p.a || '0',
                                    points: p.points || p.pts || '0'
                                });
                            }
                        }
                    }
                } catch (e) {
                    // Not valid JSON
                }
            }
        }
        
        return players;
    });
    
    return players;
}

// Debug page structure
async function debugPage(page, leagueName, config) {
    console.log(`\n=== DEBUG: ${leagueName} ===`);
    
    const debugInfo = {
        league: leagueName,
        url: config.url,
        timestamp: new Date().toISOString(),
        networkRequests: [],
        htmlStructure: {},
        cookies: [],
        localStorage: {}
    };
    
    // Get cookies
    try {
        debugInfo.cookies = await page.cookies();
    } catch (e) {
        debugInfo.cookies = [];
    }
    
    // Get page title
    try {
        debugInfo.title = await page.title();
    } catch (e) {
        debugInfo.title = '';
    }
    
    // Analyze HTML structure
    try {
        debugInfo.htmlStructure = await page.evaluate(() => {
            const result = {
                tables: document.querySelectorAll('table').length,
                scripts: document.querySelectorAll('script').length,
                divs: document.querySelectorAll('div').length,
                buttons: document.querySelectorAll('button').length,
                iframes: document.querySelectorAll('iframe').length,
                classes: []
            };
            
            // Get unique class names that might be player-related
            const allElements = document.querySelectorAll('*');
            const classSet = new Set();
            allElements.forEach(el => {
                if (el.className && typeof el.className === 'string') {
                    const classes = el.className.split(/\s+/).filter(c => c.length > 3);
                    classes.forEach(c => {
                        if (/player|stats|table|row|data/i.test(c)) {
                            classSet.add(c);
                        }
                    });
                }
            });
            result.classes = Array.from(classSet).slice(0, 30);
            
            // Sample table headers
            const tables = document.querySelectorAll('table');
            result.tableHeaders = [];
            tables.forEach((table, i) => {
                if (i < 3) {
                    const headers = Array.from(table.querySelectorAll('th')).map(h => h.textContent.trim());
                    result.tableHeaders.push(headers);
                }
            });
            
            // Check for consent/cookie elements
            result.cookieElements = [];
            const cookieSelectors = ['[class*="cookie"]', '[id*="cookie"]', '[class*="consent"]', '[id*="consent"]'];
            cookieSelectors.forEach(sel => {
                const els = document.querySelectorAll(sel);
                if (els.length > 0) {
                    els.forEach(el => {
                        result.cookieElements.push({
                            tag: el.tagName,
                            id: el.id,
                            class: el.className,
                            text: el.textContent?.substring(0, 100)
                        });
                    });
                }
            });
            
            // Check for React root
            const reactRoot = document.querySelector('#root, #__next, [data-reactroot]');
            result.hasReactRoot = !!reactRoot;
            
            return result;
        });
    } catch (e) {
        debugInfo.htmlStructure = { error: e.message };
    }
    
    // Capture network requests
    debugInfo.networkRequests = networkLogs.slice(0, 50);
    
    console.log('  Title:', debugInfo.title);
    console.log('  Tables found:', debugInfo.htmlStructure.tables);
    console.log('  Scripts found:', debugInfo.htmlStructure.scripts);
    console.log('  Cookie elements:', debugInfo.htmlStructure.cookieElements.length);
    console.log('  Network requests captured:', networkLogs.length);
    console.log('  Has React root:', debugInfo.htmlStructure.hasReactRoot);
    
    if (debugInfo.htmlStructure.tableHeaders.length > 0) {
        console.log('  Table headers sample:', debugInfo.htmlStructure.tableHeaders[0]);
    }
    
    // Print key network requests
    const apiRequests = networkLogs.filter(l => 
        l.url.includes('/api') || l.url.includes('.json') || l.resourceType === 'xhr'
    );
    if (apiRequests.length > 0) {
        console.log('\n  API/XHR Requests:');
        apiRequests.slice(0, 10).forEach(req => {
            console.log(`    - ${req.method} ${req.url.substring(0, 80)}`);
        });
    }
    
    return debugInfo;
}

// Try to call API endpoints directly
async function tryApiEndpoints(leagueName, config) {
    console.log(`\n=== API Discovery: ${leagueName} ===`);
    
    const foundPlayers = [];
    
    // Try common API patterns based on league
    const apiPatterns = {
        'Liiga': [
            'https://www.liiga.fi/api/v2/players?season=2025-2026',
            'https://www.liiga.fi/api/v1/players',
            'https://www.liiga.fi/api/v2/players',
            'https://liiga.fi/api/v2/players',
            'https://liiga.fi/api/v1/players',
            'https://www.liiga.fi/api/v2/stats/players',
            'https://www.liiga.fi/api/v2/playerstats',
            'https://www.liiga.fi/api/v2/runkosarja/playerstats'
        ],
        'SHL': [
            'https://api.shl.se/players',
            'https://www.shl.se/api/players',
            'https://shl.se/api/v1/players',
            'https://api.shl.se/v1/players'
        ],
        'KHL': [
            'https://en.khl.ru/api/players',
            'https://api.khl.ru/v1/players',
            'https://en.khl.ru/stat/players/2025-2026/'
        ],
        'Mestis': [
            'https://mestis.fi/api/v1/players',
            'https://www.mestis.fi/api/players',
            'https://mestis.fi/api/v2/players'
        ],
        'AHL': [
            'https://cluster.leankr.com/api/v1/theahl/players',
            'https://api-web.nhle.com/player/details/'
        ]
    };
    
    const patterns = apiPatterns[leagueName] || [];
    
    for (const apiUrl of patterns) {
        try {
            console.log(`  Trying: ${apiUrl}`);
            const response = await httpGet(apiUrl);
            
            if (response.status >= 200 && response.status < 300 && response.data) {
                try {
                    const data = JSON.parse(response.data);
                    console.log(`    ✓ Got JSON response (${response.data.length} bytes)`);
                    
                    // Extract players from response
                    const extractFromJson = (obj) => {
                        if (Array.isArray(obj)) {
                            // Check if this looks like player data
                            if (obj[0]?.firstName || obj[0]?.lastName || obj[0]?.name) {
                                return obj;
                            }
                        }
                        if (typeof obj === 'object') {
                            // Look for common keys
                            const keys = ['players', 'data', 'roster', 'playerList'];
                            for (const key of keys) {
                                if (obj[key]) {
                                    const result = extractFromJson(obj[key]);
                                    if (result) return result;
                                }
                            }
                        }
                        return null;
                    };
                    
                    const players = extractFromJson(data);
                    if (players && players.length > 0) {
                        console.log(`    Found ${players.length} players in API response`);
                        
                        for (const p of players) {
                            const name = p.name || `${p.firstName || ''} ${p.lastName || ''}`.trim();
                            if (name && isFinnishName(name)) {
                                foundPlayers.push({
                                    name: name,
                                    team: p.team || p.club || '',
                                    position: p.position || p.pos || '',
                                    games: p.games || p.gp || '0',
                                    goals: p.goals || p.g || '0',
                                    assists: p.assists || p.a || '0',
                                    points: p.points || p.pts || '0',
                                    apiSource: apiUrl
                                });
                            }
                        }
                    }
                } catch (e) {
                    console.log(`    Not valid JSON: ${e.message}`);
                }
            } else {
                console.log(`    Status: ${response.status}`);
            }
        } catch (e) {
            console.log(`    Error: ${e.message}`);
        }
    }
    
    // Check intercepted JSON payloads collected natively
    if (interceptedJsonPayloads.length > 0) {
        console.log(`\n  Analyzing ${interceptedJsonPayloads.length} intercepted JSON payloads...`);
        for (const payload of interceptedJsonPayloads) {
            try {
                const extractFromJson = (obj) => {
                    if (Array.isArray(obj)) {
                        if (obj[0]?.firstName || obj[0]?.lastName || obj[0]?.name || obj[0]?.etunimi) {
                            return obj;
                        }
                    }
                    if (typeof obj === 'object' && obj !== null) {
                        const keys = ['players', 'data', 'roster', 'playerList', 'items', 'results'];
                        for (const key of keys) {
                            if (obj[key]) {
                                const result = extractFromJson(obj[key]);
                                if (result) return result;
                            }
                        }
                    }
                    return null;
                };
                
                const players = extractFromJson(payload.data);
                if (players && players.length > 0) {
                    console.log(`    Found ${players.length} players in intercepted JSON from ${payload.url}`);
                    
                    for (const p of players) {
                        const name = p.name || p.nimi || `${p.firstName || p.etunimi || ''} ${p.lastName || p.sukunimi || ''}`.trim();
                        if (name && isFinnishName(name)) {
                            foundPlayers.push({
                                name: name,
                                team: p.team || p.club || p.joukkue?.nimi || '',
                                position: p.position || p.pos || p.pelipaikka || '',
                                games: p.games || p.gp || p.ottelut || '0',
                                goals: p.goals || p.g || p.maalit || '0',
                                assists: p.assists || p.a || p.syötöt || '0',
                                points: p.points || p.pts || p.pisteet || '0',
                                apiSource: payload.url
                            });
                        }
                    }
                }
            } catch (e) {
                // Skip invalid payload formats
            }
        }
    }
    
    // Also try captured API endpoints from network logs (Fall-back)
    if (foundPlayers.length === 0 && apiEndpoints.size > 0) {
        console.log('\n  Trying captured API endpoints (fallback):');
        for (const url of apiEndpoints) {
            if (url.includes('player') || url.includes('stats') || url.includes('.json')) {
                try {
                    const response = await httpGet(url);
                    if (response.status >= 200 && response.status < 300 && response.data) {
                        console.log(`    ✓ ${url.substring(0, 60)}...`);
                    }
                } catch (e) {
                    // Skip failed requests
                }
            }
        }
    }
    
    return foundPlayers;
}

// Special function to extract Mestis player images
async function extractMestisPlayerImages(browser, players, mainPage) {
    const playersWithImages = [];
    const startTime = Date.now();
    const maxDuration = 120000; // 2 minutes max for image extraction
    
    for (let i = 0; i < players.length; i++) {
        // Check timeout
        if (Date.now() - startTime > maxDuration) {
            console.log('  Image extraction timeout reached, stopping...');
            break;
        }
        const player = players[i];
        let playerWithImage = {...player};
        
        try {
            // Create a format suitable for Mestis URL (remove spaces, commas, etc.)
            const nameForUrl = player.name
                .replace(/\s*,\s*/g, '-')  // Replace comma+space with dash
                .replace(/\s+/g, '-')    // Replace spaces with dashes
                .replace(/[^\w\u00C0-\u024F-]/g, '')  // Remove special chars but keep Finnish letters
                .toLowerCase();
            
            // Try to find player ID from the main page by matching name
            const playerLinks = await mainPage.evaluate((playerName) => {
                const links = Array.from(document.querySelectorAll('a[href*="/pelaajat/"]'));
                return links
                    .filter(link => {
                        const linkText = link.textContent.trim();
                        const playerNameNormalized = playerName.replace(/\s*,\s*/g, ' ').trim();
                        const linkTextNormalized = linkText.replace(/\s*,\s*/g, ' ').trim();
                        return linkTextNormalized === playerNameNormalized;
                    })
                    .map(link => link.getAttribute('href'));
            }, player.name);
            
            if (playerLinks.length > 0) {
                const playerUrl = playerLinks[0];
                const fullPlayerUrl = playerUrl.startsWith('http') ? playerUrl : `https://www.mestis.fi${playerUrl}`;
                
                // Visit player page to extract image
                const playerPage = await browser.newPage();
                try {
                    await playerPage.goto(fullPlayerUrl, {
                        waitUntil: 'networkidle2',
                        timeout: 30000
                    });
                    
                    const imageUrl = await playerPage.evaluate(() => {
                        const imgElement = document.querySelector('.player-image-wrapper img');
                        return imgElement ? imgElement.getAttribute('src') : null;
                    });
                    
                    if (imageUrl) {
                        // Convert relative URL to absolute
                        if (imageUrl.startsWith('/')) {
                            playerWithImage.image = `https://www.mestis.fi${imageUrl}`;
                        } else {
                            playerWithImage.image = imageUrl;
                        }
                        console.log(`    Image found for ${player.name}`);
                    } else {
                        console.log(`    No image found for ${player.name}`);
                    }
                    
                    await playerPage.close();
                } catch (error) {
                    console.log(`    Error getting image for ${player.name}: ${error.message}`);
                    await playerPage.close();
                }
            } else {
                console.log(`    No player link found for ${player.name}`);
            }
            
        } catch (error) {
            console.log(`    Error processing player ${player.name}: ${error.message}`);
        }
        
        playersWithImages.push(playerWithImage);
    }
    
    return playersWithImages;
}

// Main scrape function for a league
async function scrapeLeague(browser, config) {
    console.log(`\n--- ${config.name} ---`);
    console.log(`  URL: ${config.url}`);
    
    let page;
    let players = [];
    
    try {
        page = await browser.newPage();
        
        // Set realistic user agent
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        await page.setViewport({ width: 1920, height: 1080 });
        
        // Setup network interception
        interceptedJsonPayloads.length = 0; // Reset for each league
        setupNetworkInterception(page, config.name);
        
        console.log('  Loading page...');
        
        // Navigate to page
        await page.goto(config.url, { 
            waitUntil: 'networkidle2', 
            timeout: 60000 
        }).catch(e => {
            console.log(`  Navigation note: ${e.message}`);
        });
        
        // Handle cookie consent for European leagues
        if (config.type === 'european') {
            await handleCookieConsentAdvanced(page, config);
        }
        
        // Wait for content
        await waitForContent(page, config);
        
        // Debug page if in debug mode
        if (debugMode) {
            await debugPage(page, config.name, config);
        }
        
        // Extract players
        players = await extractPlayers(page, config.name);
        console.log(`  Found ${players.length} Finnish players via scraping`);
        
        // Try API endpoints if no players found or in find-apis mode
        if (findApisOnly || players.length === 0) {
            const apiPlayers = await tryApiEndpoints(config.name, config);
            if (apiPlayers.length > 0) {
                console.log(`  Found ${apiPlayers.length} players via API`);
                players = [...players, ...apiPlayers];
            }
        }
        
        // Special handling for Mestis - extract player images
        if (config.name === 'Mestis' && players.length > 0) {
            console.log('  Extracting player images...');
            const playersWithImages = await extractMestisPlayerImages(browser, players, page);
            // Merge the players with images back into the full list
            players = players.map(player => {
                const playerWithImage = playersWithImages.find(p => p.name === player.name);
                return playerWithImage || player;
            });
        }
        
        await page.close();
        
    } catch (error) {
        console.log(`  Error: ${error.message}`);
        if (page) await page.close();
    }
    
    return players;
}

// Main function
async function main() {
    const args = process.argv.slice(2);
    
    // Parse flags first
    debugMode = args.includes('--debug');
    findApisOnly = args.includes('--find-apis');
    
    // Get target league (filter out flags)
    let targetLeague = args.find(a => !a.startsWith('--')) || null;
    
    // Handle special flags
    if (targetLeague === 'ALL' || targetLeague === '--debug-all') {
        debugMode = true;
        targetLeague = null;
    }
    
    console.log('='.repeat(60));
    console.log('Advanced Puppeteer Scraper - Finnish Prospects');
    console.log('='.repeat(60));
    console.log(`Time: ${new Date().toISOString()}`);
    console.log(`Debug mode: ${debugMode}`);
    console.log(`Find APIs only: ${findApisOnly}`);
    
    let leaguesToScrape = leagueConfigs;
    if (targetLeague) {
        const targetUpper = targetLeague.toUpperCase();
        leaguesToScrape = leagueConfigs.filter(l => l.name.toUpperCase() === targetUpper);
        if (leaguesToScrape.length === 0) {
            console.log(`\nUnknown league: ${targetLeague}`);
            console.log('Available leagues:', leagueConfigs.map(l => l.name).join(', '));
            process.exit(1);
        }
    }
    
    // Launch browser
    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--allow-running-insecure-content'
        ]
    });
    
    const results = {
        generated_at: new Date().toISOString(),
        season: '2025-2026',
        data_source: 'puppeteer-advanced',
        scraper_version: '4.0',
        leagues: {},
        players: [],
        network_logs: debugMode ? networkLogs : [],
        api_endpoints: Array.from(apiEndpoints)
    };
    
    // Scrape each league
    for (const league of leaguesToScrape) {
        console.log(`\n[${leaguesToScrape.indexOf(league) + 1}/${leaguesToScrape.length}] Processing ${league.name}...`);
        
        const players = await scrapeLeague(browser, league);
        results.leagues[league.name.toLowerCase()] = { 
            count: players.length, 
            url: league.url, 
            type: league.type 
        };
        
        for (const player of players) {
            results.players.push({ 
                ...player, 
                league: league.name, 
                source: 'puppeteer-advanced', 
                scraped_at: new Date().toISOString() 
            });
        }
        
        // Wait between leagues
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    await browser.close();
    
    // Sort by points
    results.players.sort((a, b) => (parseInt(b.points) || 0) - (parseInt(a.points) || 0));
    results.total_players = results.players.length;
    
    // Summary
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
    
    // Also save debug info if in debug mode
    if (debugMode) {
        const debugFile = path.join(OUTPUT_DIR, 'debug_network.json');
        fs.writeFileSync(debugFile, JSON.stringify({
            networkLogs: networkLogs,
            apiEndpoints: Array.from(apiEndpoints),
            timestamp: new Date().toISOString()
        }, null, 2));
        console.log(`✓ Debug data saved to ${debugFile}`);
    }
    
    return results;
}

main().catch(console.error);
