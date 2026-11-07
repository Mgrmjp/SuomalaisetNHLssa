#!/usr/bin/env node
/**
 * Public route smoke checks and responsive screenshots.
 * TEST_URL selects dev/preview; UI_SCREENSHOT_DIR enables visual review artifacts.
 */
import assert from 'node:assert/strict'
import { mkdir, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import puppeteer from 'puppeteer'
import { isProspectsPath, PROSPECTS_ENABLED } from '../src/lib/config/features.js'

const baseUrl = process.env.TEST_URL || 'http://localhost:3000'
const screenshotDir = process.env.UI_SCREENSHOT_DIR
const articles = JSON.parse(await readFile('static/data/articles.json', 'utf8'))
const routes = ['/', '/sarjataulukko/', '/joukkueet/', '/pisteporssi/', '/pelaajat/',
    '/pelaajat/sebastian-aho/', '/lupaukset/', '/drafts/', '/mestaruudet/', '/scouting/',
    '/scouting/oliver-suvanto/', '/siirrot/', '/tietoa/', '/viikkokatsaus/',
    ...(articles[0]?.slug ? [`/viikkokatsaus/${articles[0].slug}/`] : [])].filter((path) => PROSPECTS_ENABLED || !isProspectsPath(path))
if (screenshotDir) await mkdir(screenshotDir, { recursive: true })
const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] })
const failures = []
const snapshot = JSON.parse(await readFile('static/data/standings.json', 'utf8'))
const gameDate = '2026-11-06'

async function visit(page, path) {
    const response = await page.goto(baseUrl + path, { waitUntil: 'domcontentloaded', timeout: 60000 })
    assert(response && response.status() < 400, `HTTP ${response?.status()} at ${path}`)
    await page.waitForSelector('main', { timeout: 15000 })
    await new Promise((resolve) => setTimeout(resolve, 800))
}
try {
    for (const width of process.env.UI_STATES_ONLY ? [] : [375, 768, 1440]) {
        for (const path of routes) {
            const page = await browser.newPage()
            const errors = []
            page.on('pageerror', (error) => errors.push(error.message))
            await page.setViewport({ width, height: 960 })
            try {
                await visit(page, path)
                if (path === '/sarjataulukko/') await page.waitForSelector('.standings-table tbody tr', { timeout: 10000 })
                if (path === '/') await page.waitForFunction(() => !document.querySelector('.card--skeleton'), { timeout: 20000 })
                if (path === '/joukkueet/') await page.waitForSelector('.team-card', { timeout: 10000 })
                const geometry = await page.evaluate(() => ({
                    width: document.documentElement.clientWidth,
                    scrollWidth: document.documentElement.scrollWidth,
                    navHeight: document.querySelector('.nav-tabs-list')?.getBoundingClientRect().height,
                    surface: [...document.querySelectorAll('.ui-surface, .panel')].slice(0, 8).map((node) => {
                        const style = getComputedStyle(node)
                        const radii = style.getPropertyValue('--card-radius').trim().split(/\s+/).map(Number.parseFloat)
                        return {
                            top: Number.parseFloat(style.borderTopLeftRadius),
                            bottom: Number.parseFloat(style.borderBottomLeftRadius),
                            expectedTop: radii[0],
                            expectedBottom: radii[3] ?? radii[1] ?? radii[0],
                        }
                    }),
                    overflowing: [...document.querySelectorAll('main *')].filter((node) => {
                        const rect = node.getBoundingClientRect()
                        return rect.width > 0 && rect.right > innerWidth + 2 && !node.closest('.ui-table-scroll, .overflow-x-auto, .nav-tabs-list')
                    }).slice(0, 6).map((node) => node.className),
                }))
                assert(geometry.scrollWidth <= width + 2, `Page overflow ${geometry.scrollWidth}/${width}: ${JSON.stringify(geometry.overflowing)}`)
                assert(!geometry.navHeight || geometry.navHeight <= 58, 'Navigation stays in one scrollable row')
                for (const surface of geometry.surface) {
                    assert.equal(surface.top, surface.expectedTop, 'Surface follows its active radius token')
                    assert.equal(surface.bottom, surface.expectedBottom, 'Surface follows its active radius token')
                }
                assert.deepEqual(errors, [], 'Runtime errors')
                if (!PROSPECTS_ENABLED) assert.equal(await page.$$eval('a[href]', (links) => links.filter(link => /\/(lupaukset|prospects|drafts|scouting)(\/|$)/.test(new URL(link.href).pathname)).length), 0, 'Disabled section has no public links')
                const tables = await page.$$eval('.ui-table-scroll', (regions) => regions.map((region) => ({
                    caption: region.querySelector('caption')?.textContent.trim(),
                    label: region.getAttribute('aria-label'),
                    focusable: region.tabIndex === 0,
                })))
                for (const table of tables) assert(table.caption && table.label && table.focusable, 'Tables are labelled and keyboard scrollable')
                const firstLink = await page.$('.nav-tab-item')
                if (firstLink) {
                    await firstLink.focus()
                    assert(await firstLink.evaluate((node) => parseFloat(getComputedStyle(node).outlineWidth) > 0), 'Keyboard focus visible')
                }
                await page.evaluate(() => document.activeElement?.blur())
                if (screenshotDir) {
                    const slug = path === '/' ? 'dashboard' : path.replaceAll('/', '-').replace(/^-|-$/g, '')
                    await page.screenshot({ path: join(screenshotDir, `${slug}-${width}.png`) })
                }
                console.log(`PASS ${width} ${path}`)
            } catch (error) {
                failures.push(`${width} ${path}: ${error.message}`)
                console.log(`FAIL ${failures.at(-1)}`)
            } finally { await page.close() }
        }
    }

    // Shared buttons preserve native keyboard activation and feature callbacks.
    if (PROSPECTS_ENABLED) {
    const prospectsPage = await browser.newPage()
    await visit(prospectsPage, '/lupaukset/')
    await prospectsPage.waitForSelector('[aria-label="Kenttäpelaajien järjestys"] button')
    const goalsSelector = '[aria-label="Kenttäpelaajien järjestys"] button:nth-child(2)'
    await prospectsPage.focus(goalsSelector)
    await prospectsPage.keyboard.press('Space')
    await prospectsPage.waitForFunction((selector) => document.querySelector(selector)?.textContent.includes('↓'), {}, goalsSelector)
    assert.equal(await prospectsPage.$eval(goalsSelector, (button) => button.getAttribute('aria-pressed')), 'true')
    await prospectsPage.keyboard.press('Enter')
    await prospectsPage.waitForFunction((selector) => document.querySelector(selector)?.textContent.includes('↑'), {}, goalsSelector)
    await prospectsPage.click('[aria-label="Pelaajatyyppi"] button:nth-child(3)')
    await prospectsPage.waitForSelector('#ranking-source', { visible: true })
    assert.equal(await prospectsPage.$eval('[aria-label="Pelaajatyyppi"] button:nth-child(3)', (button) => button.getAttribute('aria-pressed')), 'true')
    await prospectsPage.close()

    } else {
        const disabledPage = await browser.newPage()
        for (const path of ['/lupaukset/', '/prospects/', '/drafts/', '/scouting/', '/scouting/oliver-suvanto/']) {
            const prospectRequests = []
            const record = request => { if (/data\/(finnish_prospects|finnish_draft_rankings|leagues\/)/.test(request.url())) prospectRequests.push(request.url()) }
            disabledPage.on('request', record)
            await visit(disabledPage, path)
            assert.equal(new URL(disabledPage.url()).pathname, '/', 'Disabled route redirects home')
            assert.deepEqual(prospectRequests, [], 'Disabled route does not fetch section data')
            disabledPage.off('request', record)
        }
        const sitemap = await (await fetch(baseUrl + '/sitemap.xml')).text()
        assert(!/<loc>[^<]*\/(lupaukset|prospects|drafts|scouting)(\/|<)/.test(sitemap), 'Disabled section is absent from sitemap')
        await disabledPage.close()
        console.log('PASS disabled section navigation, direct routes, data requests and sitemap')
    }

    const directoryPage = await browser.newPage()
    await visit(directoryPage, '/pelaajat/')
    await directoryPage.waitForSelector('.player-directory-card')
    await directoryPage.type('input[type="text"]', 'no-such-player-928412')
    await directoryPage.waitForFunction(() => document.body.innerText.includes('Pelaajia ei löytynyt'))
    assert.equal(await directoryPage.$$eval('.player-directory-card', (cards) => cards.length), 0)
    await directoryPage.focus('input[type="text"]')
    await directoryPage.keyboard.down('Control')
    await directoryPage.keyboard.press('A')
    await directoryPage.keyboard.up('Control')
    await directoryPage.keyboard.press('Backspace')
    await directoryPage.waitForSelector('.player-directory-card')
    await directoryPage.close()

    const tablePage = await browser.newPage()
    await tablePage.setViewport({ width: 375, height: 960 })
    await visit(tablePage, '/pisteporssi/')
    await tablePage.focus('.ui-table-scroll')
    await tablePage.keyboard.press('ArrowRight')
    await tablePage.waitForFunction(() => document.querySelector('.ui-table-scroll')?.scrollLeft > 0)
    await tablePage.close()
    console.log('PASS keyboard sorting/filtering, search empty state and table scrolling')

    // The date picker stays compact and historical game cards remain interactive.
    for (const width of [375, 768, 1440]) {
        const dashboard = await browser.newPage()
        await dashboard.setViewport({ width, height: 960 })
        await visit(dashboard, `/?date=${gameDate}`)
        await dashboard.click('[aria-label="Avaa kalenteri"]')
        await dashboard.waitForSelector('.calendar-month')
        assert(await dashboard.$eval('.calendar-month', (node) => node.getBoundingClientRect().width <= 360), 'Compact calendar')
        await dashboard.$$eval('.calendar-month__day:not(.calendar-month__day--other-month)', (days) => days.find((day) => day.querySelector('.calendar-month__day-number')?.textContent.trim() === '5')?.click())
        await dashboard.waitForFunction(() => new URL(location.href).searchParams.get('date') === '2026-11-05')
        await dashboard.click('[aria-label="Avaa kalenteri"]')
        await dashboard.$$eval('.calendar-month__day:not(.calendar-month__day--other-month)', (days) => days.find((day) => day.querySelector('.calendar-month__day-number')?.textContent.trim() === '6')?.click())
        await dashboard.waitForFunction((date) => new URL(location.href).searchParams.get('date') === date, {}, gameDate)
        const card = '.scoring-list__grid .game-player-card'
        await dashboard.waitForSelector(card + ' .card__name', { visible: true, timeout: 15000 })
        await dashboard.$eval(card, (node) => node.scrollIntoView({ block: 'center' }))
        await dashboard.click(card + ' .card__footer-hint')
        await dashboard.waitForSelector(card + '.flipped')
        await new Promise((resolve) => setTimeout(resolve, 900))
        await dashboard.focus(card + ' .card--back')
        await dashboard.keyboard.press('Enter')
        await dashboard.waitForFunction((selector) => !document.querySelector(selector)?.classList.contains('flipped'), {}, card)
        await new Promise((resolve) => setTimeout(resolve, 900))
        await dashboard.evaluate(() => document.activeElement?.blur())
        if (screenshotDir) await dashboard.screenshot({ path: join(screenshotDir, `dashboard-results-${width}.png`) })
        await dashboard.click(card + ' .card__stats-btn')
        await dashboard.waitForSelector('.player-details-dialog')
        assert.equal(await dashboard.$(card + '.flipped'), null, 'Opening details does not flip the card')
        assert(await dashboard.$eval('.player-details-dialog', (node) => node.getBoundingClientRect().right <= innerWidth), 'Modal fits viewport')
        if (screenshotDir) await dashboard.screenshot({ path: join(screenshotDir, `player-modal-${width}.png`) })
        await dashboard.click('[aria-label="Sulje pelaajan lisätiedot"]')

        // Recovery notices retain the cards and support keyboard retry.
        const names = await dashboard.$$eval('.card__name-label', (nodes) => nodes.map((node) => node.textContent))
        let failRefresh = true
        await dashboard.setRequestInterception(true)
        dashboard.on('request', (request) => failRefresh && request.url().includes(`/data/prepopulated/games/${gameDate}.json`)
            ? request.respond({ status: 503, body: '{}' }) : request.continue())
        await dashboard.evaluate(() => document.dispatchEvent(new Event('visibilitychange')))
        await dashboard.waitForSelector('.ui-notice--recovery[role="status"]')
        assert.deepEqual(await dashboard.$$eval('.card__name-label', (nodes) => nodes.map((node) => node.textContent)), names)
        if (screenshotDir) await dashboard.screenshot({ path: join(screenshotDir, `dashboard-recovery-${width}.png`) })
        failRefresh = false
        await dashboard.focus('.ui-notice--recovery button')
        await dashboard.keyboard.press('Enter')
        await dashboard.waitForSelector('.ui-notice--recovery', { hidden: true })
        assert.deepEqual(await dashboard.$$eval('.card__name-label', (nodes) => nodes.map((node) => node.textContent)), names)
        await dashboard.close()
    }
    console.log('PASS compact calendar, result card flip and player modal')

    // Standings must retain official ordering and recover without hiding last-good rows.
    const page = await browser.newPage()
    await page.setViewport({ width: 1440, height: 960 })
    await visit(page, '/sarjataulukko/')
    await page.waitForSelector('.standings-table tbody tr')
    assert.equal(await page.$$eval('.standings-table tbody tr', (rows) => rows.length), 16)
    const atlantic = snapshot.standings.filter((team) => team.divisionAbbrev === 'A').sort((a, b) => a.divisionSequence - b.divisionSequence)
    const rendered = await page.$$eval('.standings-table:first-of-type tbody .team-abbrev', (nodes) => nodes.map((node) => node.textContent))
    assert.deepEqual(rendered.slice(0, 8), atlantic.map((team) => team.teamAbbrev.default))
    await page.$$eval('button', (buttons) => buttons.find((button) => button.textContent === 'Lisätilastot')?.click())
    assert.equal(await page.$eval('.standings-table thead tr', (row) => row.children.length), 15)
    await page.$$eval('button', (buttons) => buttons.find((button) => button.textContent === 'Läntinen')?.click())
    await page.waitForFunction(() => document.querySelector('.table-heading')?.textContent.includes('Keskinen'))
    await page.setRequestInterception(true)
    let failStandingsRefresh = true
    page.on('request', (request) => failStandingsRefresh && request.url().includes('/data/standings.json') ? request.respond({ status: 503, body: '{}' }) : request.continue())
    await page.$$eval('button', (buttons) => buttons.find((button) => button.textContent === 'Päivitä')?.click())
    await page.waitForFunction(() => document.querySelector('[role="status"]')?.textContent.includes('Päivitys epäonnistui'))
    await page.waitForSelector('.ui-notice--recovery[role="status"]')
    assert.equal(await page.$$eval('.standings-table tbody tr', (rows) => rows.length), 16)
    if (screenshotDir) await page.screenshot({ path: join(screenshotDir, 'standings-recovery-1440.png') })
    failStandingsRefresh = false
    await page.focus('.ui-notice--recovery button')
    await page.keyboard.press('Enter')
    await page.waitForFunction(() => !document.querySelector('.ui-notice--recovery')?.textContent.includes('Päivitys epäonnistui'))
    assert.equal(await page.$$eval('.standings-table tbody tr', (rows) => rows.length), 16)
    await page.close()

    for (const width of [375, 320]) {
        const recoveryPage = await browser.newPage()
        await recoveryPage.setViewport({ width, height: 960 })
        let failRefresh = false
        await recoveryPage.setRequestInterception(true)
        recoveryPage.on('request', (request) => {
            if (!request.url().includes('/data/standings.json')) return request.continue()
            return request.respond(failRefresh
                ? { status: 503, body: '{}' }
                : { status: 200, contentType: 'application/json', body: JSON.stringify({ ...snapshot, fetchedAt: new Date().toISOString() }) })
        })
        await visit(recoveryPage, '/sarjataulukko/')
        await recoveryPage.waitForSelector('.standings-table tbody tr')
        failRefresh = true
        await recoveryPage.$$eval('.view-actions button', (buttons) => buttons.find((button) => button.textContent === 'Päivitä')?.click())
        await recoveryPage.waitForSelector('.ui-notice--recovery button')
        assert.equal(await recoveryPage.$$eval('.standings-table tbody tr', (rows) => rows.length), 16)
        assert(await recoveryPage.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Recovery notice fits mobile')
        if (screenshotDir) await recoveryPage.screenshot({ path: join(screenshotDir, `standings-recovery-${width}.png`) })
        failRefresh = false
        await recoveryPage.focus('.ui-notice--recovery button')
        await recoveryPage.keyboard.press('Enter')
        await recoveryPage.waitForSelector('.ui-notice--recovery', { hidden: true })
        assert.equal(await recoveryPage.$$eval('.standings-table tbody tr', (rows) => rows.length), 16)
        await recoveryPage.close()
    }
    for (const state of ['missing', 'stale']) {
        const statePage = await browser.newPage()
        let unavailable = state === 'missing'
        await statePage.setRequestInterception(true)
        statePage.on('request', (request) => {
            if (!request.url().includes('/data/standings.json')) return request.continue()
            return request.respond(unavailable
                ? { status: 503, body: '{}' }
                : { status: 200, contentType: 'application/json', body: JSON.stringify({ ...snapshot, fetchedAt: new Date(Date.now() - 4 * 3600000).toISOString() }) })
        })
        await visit(statePage, '/sarjataulukko/')
        await statePage.waitForFunction((state) => document.body.innerText.includes(state === 'missing' ? 'Yritä uudelleen' : 'yli kolme tuntia'), {}, state)
        if (screenshotDir) await statePage.screenshot({ path: join(screenshotDir, `standings-${state}.png`) })
        if (state === 'missing') {
            unavailable = false
            await statePage.focus('.ui-state button')
            await statePage.keyboard.press('Enter')
            await statePage.waitForSelector('.standings-table tbody tr')
        }
        await statePage.close()
    }
    const loadingPage = await browser.newPage()
    await loadingPage.setRequestInterception(true)
    loadingPage.on('request', async (request) => {
        if (!request.url().includes('/data/standings.json')) return request.continue()
        await new Promise((resolve) => setTimeout(resolve, 2000))
        await request.respond({ status: 200, contentType: 'application/json', body: JSON.stringify(snapshot) })
    })
    await visit(loadingPage, '/sarjataulukko/')
    assert.match(await loadingPage.$eval('.ui-state[role="status"]', (node) => node.textContent), /Ladataan virallista sarjataulukkoa/)
    await loadingPage.waitForSelector('.standings-table tbody tr')
    await loadingPage.close()
    console.log('PASS standings loading announcement and keyboard retry')
    console.log('PASS standings controls, official order, stale/missing data, last-good retention')
} catch (error) {
    failures.push(error.stack || error.message)
} finally { await browser.close() }
if (failures.length) {
    console.error(failures.join('\n'))
    process.exitCode = 1
} else console.log(`PASS ${process.env.UI_STATES_ONLY ? 'interaction/state checks' : `all ${routes.length * 3} route/viewport combinations and interaction/state checks`}`)
