#!/usr/bin/env node
/**
 * HTML Structure Analyzer for Hockey League Websites
 * 
 * This script visits each league website, waits for player tables to load,
 * and dumps the relevant HTML to files for analysis.
 * 
 * Usage: node scripts/dump-html-structure.cjs
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '../temp/html_dumps');

// League URLs to analyze
const leagues = [
    { name: 'AHL', url: 'https://www.theahl.com/stats/players' },
    { name: 'ECHL', url: 'https://www.echl.com/stats/players' },
    { name: 'USHL', url: 'https://www.ushl.com/stats/players' },
    { name: 'NAHL', url: 'https://nahl.com/stats/players' },
    { name: 'OHL', url: 'https://ontariohockeyleague.com/stats/players' },
    { name: 'WHL', url: 'https://whl.ca/stats/players' },
    { name: 'QMJHL', url: 'https://theqmjhl.ca/stats/players' },
    { name: 'KHL', url: 'https://en.khl.ru/stats/players/' },
    { name: 'SHL', url: 'https://www.shl.se/statistik/spelare/' },
    { name: 'Liiga', url: 'https://liiga.fi/tilastot/pelaajat/' },
];

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&')
        .replace(/</g, '<')
        .replace(/>/g, '>')
        .replace(/"/g, '"')
        .replace(/'/g, '&#039;');
}

async function analyzeLeague(browser, league) {
    console.log('\n--- ' + league.name + ' ---');
    console.log('  URL: ' + league.url);
    
    let page;
    try {
        page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        await page.setViewport({ width: 1920, height: 1080 });
        
        await page.goto(league.url, { 
            waitUntil: 'networkidle2', 
            timeout: 60000 
        });
        
        // Additional wait for dynamic content
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Try to find and click "Show All" if available
        await page.evaluate(() => {
            const showAllButtons = Array.from(document.querySelectorAll('button, a')).filter(
                el => el.textContent.toLowerCase().includes('show all') || 
                      el.textContent.toLowerCase().includes('näytä kaikki') ||
                      el.textContent.toLowerCase().includes('visa alla')
            );
            if (showAllButtons[0]) {
                showAllButtons[0].click();
            }
        });
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Extract HTML structure
        const analysis = await page.evaluate(() => {
            const result = {
                pageTitle: document.title,
                tablesFound: 0,
                tableDetails: [],
                potentialPlayerTables: [],
                nationalityFilters: [],
                searchForms: [],
                relevantHtml: ''
            };
            
            const tables = document.querySelectorAll('table');
            result.tablesFound = tables.length;
            
            tables.forEach((table, idx) => {
                const tableInfo = {
                    index: idx,
                    classes: table.className,
                    id: table.id,
                    dataAttributes: {},
                    rowCount: 0,
                    columnCount: 0,
                    headers: [],
                    sampleRows: []
                };
                
                for (const attr of table.attributes) {
                    if (attr.name.startsWith('data-')) {
                        tableInfo.dataAttributes[attr.name] = attr.value;
                    }
                }
                
                const headerRow = table.querySelector('thead tr, tr:first-child');
                if (headerRow) {
                    const headers = headerRow.querySelectorAll('th, td');
                    tableInfo.columnCount = headers.length;
                    headers.forEach((th, hIdx) => {
                        tableInfo.headers.push({
                            index: hIdx,
                            text: th.textContent.trim(),
                            classes: th.className,
                            dataAttributes: {}
                        });
                        for (const attr of th.attributes) {
                            if (attr.name.startsWith('data-')) {
                                tableInfo.headers[hIdx].dataAttributes[attr.name] = attr.value;
                            }
                        }
                    });
                }
                
                const rows = table.querySelectorAll('tbody tr, tr');
                tableInfo.rowCount = rows.length;
                
                const sampleRows = Array.from(rows).slice(0, 3);
                sampleRows.forEach((row, rIdx) => {
                    const cells = row.querySelectorAll('th, td');
                    const rowData = [];
                    cells.forEach((cell, cIdx) => {
                        rowData.push({
                            index: cIdx,
                            text: cell.textContent.trim().substring(0, 50),
                            classes: cell.className,
                            hasLink: cell.querySelector('a') !== null,
                            linkHref: cell.querySelector('a')?.href || null
                        });
                    });
                    tableInfo.sampleRows.push(rowData);
                });
                
                result.tableDetails.push(tableInfo);
                
                // Check if this is a player table
                const headerText = tableInfo.headers.map(h => h.text.toLowerCase()).join(' ');
                const hasNameColumn = /name|player|pelaaja|namn/i.test(headerText);
                const hasStatsColumn = /goal|assist|point|gp|game|stat/i.test(headerText);
                
                if (hasNameColumn && hasStatsColumn) {
                    result.potentialPlayerTables.push({
                        index: idx,
                        classes: table.className,
                        id: table.id,
                        rowCount: tableInfo.rowCount,
                        headers: tableInfo.headers.map(h => h.text)
                    });
                    
                    if (!result.relevantHtml || result.relevantHtml.length < table.outerHTML.length) {
                        result.relevantHtml = table.outerHTML;
                    }
                }
            });
            
            // Look for nationality filters
            const nationalitySelectors = [
                'select[name*="nationality"]',
                'select[name*="country"]',
                'select[id*="nationality"]',
                'select[id*="country"]',
                'input[name*="nationality"]',
                'input[name*="country"]',
                '[data-testid*="nationality"]',
                '.nationality-filter',
                '.country-filter'
            ];
            
            for (const selector of nationalitySelectors) {
                const el = document.querySelector(selector);
                if (el) {
                    const options = Array.from(el.options || []).map(o => o.value);
                    result.nationalityFilters.push({
                        selector,
                        type: el.tagName,
                        options: options.slice(0, 20)
                    });
                }
            }
            
            // Look for search forms
            const searchInputs = document.querySelectorAll('input[type="search"], input[name*="search"], input[placeholder*="search"]');
            searchInputs.forEach(input => {
                result.searchForms.push({
                    name: input.name,
                    id: input.id,
                    placeholder: input.placeholder,
                    classes: input.className
                });
            });
            
            return result;
        });
        
        console.log('  Tables found: ' + analysis.tablesFound);
        console.log('  Player tables: ' + analysis.potentialPlayerTables.length);
        
        if (analysis.potentialPlayerTables.length > 0) {
            console.log('  Player table headers: ' + analysis.potentialPlayerTables[0].headers.join(', '));
        }
        
        if (analysis.nationalityFilters.length > 0) {
            console.log('  Nationality filters: ' + JSON.stringify(analysis.nationalityFilters));
        }
        
        const fullHtml = await page.content();
        
        const report = {
            league: league.name,
            url: league.url,
            analyzedAt: new Date().toISOString(),
            pageTitle: analysis.pageTitle,
            tablesFound: analysis.tablesFound,
            potentialPlayerTables: analysis.potentialPlayerTables,
            nationalityFilters: analysis.nationalityFilters,
            searchForms: analysis.searchForms,
            tableDetails: analysis.tableDetails.map(t => ({
                index: t.index,
                classes: t.classes,
                id: t.id,
                rowCount: t.rowCount,
                columnCount: t.columnCount,
                headers: t.headers.map(h => h.text)
            })),
            relevantHtml: analysis.relevantHtml.substring(0, 50000),
            fullHtmlSample: fullHtml.substring(0, 100000)
        };
        
        // Save HTML report
        let htmlContent = '<!DOCTYPE html>\n<html>\n<head>\n';
        htmlContent += '    <meta charset="UTF-8">\n';
        htmlContent += '    <title>' + league.name + ' - HTML Structure Analysis</title>\n';
        htmlContent += '    <style>\n';
        htmlContent += '        body { font-family: monospace; padding: 20px; max-width: 1200px; margin: 0 auto; }\n';
        htmlContent += '        h1 { color: #333; }\n';
        htmlContent += '        h2 { color: #666; margin-top: 30px; }\n';
        htmlContent += '        pre { background: #f5f5f5; padding: 15px; overflow-x: auto; border-radius: 5px; }\n';
        htmlContent += '        .table-info { background: #e8f4f8; padding: 15px; margin: 10px 0; border-radius: 5px; }\n';
        htmlContent += '        .filter-info { background: #f0e8f8; padding: 15px; margin: 10px 0; border-radius: 5px; }\n';
        htmlContent += '        table { border-collapse: collapse; width: 100%; margin: 10px 0; }\n';
        htmlContent += '        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n';
        htmlContent += '        th { background: #f5f5f5; }\n';
        htmlContent += '    </style>\n';
        htmlContent += '</head>\n<body>\n';
        htmlContent += '    <h1>' + league.name + ' - HTML Structure Analysis</h1>\n';
        htmlContent += '    <p><strong>URL:</strong> <a href="' + league.url + '">' + league.url + '</a></p>\n';
        htmlContent += '    <p><strong>Analyzed:</strong> ' + report.analyzedAt + '</p>\n';
        htmlContent += '    <p><strong>Page Title:</strong> ' + report.pageTitle + '</p>\n';
        htmlContent += '    \n';
        htmlContent += '    <h2>Summary</h2>\n';
        htmlContent += '    <div class="table-info">\n';
        htmlContent += '        <p><strong>Total Tables:</strong> ' + report.tablesFound + '</p>\n';
        htmlContent += '        <p><strong>Potential Player Tables:</strong> ' + report.potentialPlayerTables.length + '</p>\n';
        htmlContent += '    </div>\n';
        
        if (report.potentialPlayerTables.length > 0) {
            htmlContent += '    \n';
            htmlContent += '    <h2>Player Table Details</h2>\n';
            report.potentialPlayerTables.forEach((pt, idx) => {
                htmlContent += '    <div class="table-info">\n';
                htmlContent += '        <h3>Table ' + (idx + 1) + '</h3>\n';
                htmlContent += '        <p><strong>Classes:</strong> ' + pt.classes + '</p>\n';
                htmlContent += '        <p><strong>ID:</strong> ' + (pt.id || 'none') + '</p>\n';
                htmlContent += '        <p><strong>Row Count:</strong> ' + pt.rowCount + '</p>\n';
                htmlContent += '        <p><strong>Headers:</strong></p>\n';
                htmlContent += '        <ul>\n';
                pt.headers.forEach((h, i) => {
                    htmlContent += '            <li>[' + i + '] ' + h + '</li>\n';
                });
                htmlContent += '        </ul>\n';
                htmlContent += '    </div>\n';
            });
        }
        
        if (report.nationalityFilters.length > 0) {
            htmlContent += '    \n';
            htmlContent += '    <h2>Nationality Filters Found</h2>\n';
            report.nationalityFilters.forEach(f => {
                htmlContent += '    <div class="filter-info">\n';
                htmlContent += '        <p><strong>Selector:</strong> ' + f.selector + '</p>\n';
                htmlContent += '        <p><strong>Type:</strong> ' + f.type + '</p>\n';
                htmlContent += '        <p><strong>Options:</strong> ' + f.options.join(', ') + '</p>\n';
                htmlContent += '    </div>\n';
            });
        } else {
            htmlContent += '    <p><em>No nationality filters found</em></p>\n';
        }
        
        if (report.searchForms.length > 0) {
            htmlContent += '    \n';
            htmlContent += '    <h2>Search Forms</h2>\n';
            report.searchForms.forEach(s => {
                htmlContent += '    <div>\n';
                htmlContent += '        <p><strong>Name:</strong> ' + (s.name || 'none') + '</p>\n';
                htmlContent += '        <p><strong>ID:</strong> ' + (s.id || 'none') + '</p>\n';
                htmlContent += '        <p><strong>Placeholder:</strong> ' + (s.placeholder || 'none') + '</p>\n';
                htmlContent += '    </div>\n';
            });
        }
        
        htmlContent += '    \n';
        htmlContent += '    <h2>Player Table HTML (Sample)</h2>\n';
        htmlContent += '    <pre>' + escapeHtml(report.relevantHtml) + '</pre>\n';
        
        htmlContent += '    \n';
        htmlContent += '    <h2>Full Page HTML (First 100KB)</h2>\n';
        htmlContent += '    <pre>' + escapeHtml(report.fullHtmlSample) + '</pre>\n';
        
        htmlContent += '</body>\n</html>';
        
        const outputFile = path.join(OUTPUT_DIR, league.name.toLowerCase() + '.html');
        fs.writeFileSync(outputFile, htmlContent);
        console.log('  Saved to ' + outputFile);
        
        // Save JSON
        const jsonOutput = path.join(OUTPUT_DIR, league.name.toLowerCase() + '.json');
        fs.writeFileSync(jsonOutput, JSON.stringify(report, null, 2));
        console.log('  Saved JSON to ' + jsonOutput);
        
        await page.close();
        return analysis;
        
    } catch (error) {
        console.log('  Error: ' + error.message);
        
        const errorOutput = path.join(OUTPUT_DIR, league.name.toLowerCase() + '_error.txt');
        fs.writeFileSync(errorOutput, 'Error: ' + error.message + '\nStack: ' + error.stack);
        
        if (page) await page.close();
        return null;
    }
}

async function main() {
    console.log('============================================================');
    console.log('HTML Structure Analyzer for Hockey League Websites');
    console.log('============================================================');
    console.log('Output directory: ' + OUTPUT_DIR);
    
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    
    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    });
    
    const results = [];
    
    for (const league of leagues) {
        const analysis = await analyzeLeague(browser, league);
        results.push({
            league: league.name,
            success: analysis !== null,
            tablesFound: analysis ? analysis.tablesFound : 0,
            playerTables: analysis ? (analysis.potentialPlayerTables ? analysis.potentialPlayerTables.length : 0) : 0
        });
        
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    await browser.close();
    
    console.log('\n============================================================');
    console.log('SUMMARY');
    console.log('============================================================');
    
    for (const r of results) {
        const status = r.success ? 'OK' : 'FAIL';
        console.log(status + ' ' + r.league + ': ' + r.tablesFound + ' tables, ' + r.playerTables + ' player tables');
    }
    
    const successful = results.filter(r => r.success).length;
    console.log('\nSuccessfully analyzed ' + successful + '/' + leagues.length + ' leagues');
    console.log('HTML files saved to: ' + OUTPUT_DIR);
    
    return results;
}

main().catch(console.error);
