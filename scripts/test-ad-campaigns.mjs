import assert from 'node:assert/strict'
import puppeteer from 'puppeteer'

const baseUrl = process.env.TEST_URL || 'http://localhost:3000'
const before = Date.parse('2026-11-30T23:59:00+02:00')
const after = Date.parse('2026-12-01T00:00:00+02:00')
const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] })

async function visit(width, now) {
    const page = await browser.newPage()
    const errors = []
    page.on('pageerror', (error) => errors.push(error.message))
    page.on('console', (message) => {
        if (/hydration/i.test(message.text())) errors.push(message.text())
    })
    await page.setViewport({ width, height: 1000 })
    await page.evaluateOnNewDocument((now) => {
        const NativeDate = Date
        window.__campaignNow = now
        window.__campaignExpiry = []
        window.Date = class extends NativeDate {
            constructor(...args) {
                super(...(args.length ? args : [window.__campaignNow]))
            }
            static now() {
                return window.__campaignNow
            }
        }
        const nativeTimeout = window.setTimeout.bind(window)
        window.setTimeout = (callback, delay, ...args) => {
            if (delay === 60000) window.__campaignExpiry.push(() => callback(...args))
            return nativeTimeout(callback, delay, ...args)
        }
    }, now)
    await page.goto(`${baseUrl}/?date=2026-11-06`, { waitUntil: 'domcontentloaded' })
    await page.waitForSelector('.ad-container img[alt^="Hehku Pörssi"]')
    await page.waitForSelector('.mobile-ad-container img[alt^="Hehku Pörssi"]')
    return { page, errors }
}

async function verify(page, errors) {
    assert.equal(await page.$('img[alt^="Björn Borg Black Week"]'), null)
    for (const selector of [
        '.ad-slot--desktop .ad-link.active',
        '.mobile-ad-container .mobile-ad-link.active',
    ]) {
        assert.equal(await page.$$eval(selector, (nodes) => nodes.length), 1)
    }
    const pairs = await page.$$eval('img[alt^="Hehku"], img[alt^="Aalto Energia"]', (images) =>
        images.map((image) => ({ src: image.src, alt: image.alt, href: image.closest('a').href }))
    )
    for (const { src, alt, href } of pairs) {
        const expected = alt.startsWith('Hehku Pörssi')
            ? '2034103803'
            : alt.startsWith('Hehku Kiinteä')
              ? '2034099817'
              : '1875124667'
        const name = alt.startsWith('Hehku Pörssi')
            ? 'hehku-porssi'
            : alt.startsWith('Hehku Kiinteä')
              ? 'hehku-kiintea-12kk'
              : 'aalto-energia'
        // Vite may inline small SVGs instead of emitting a named asset.
        const artwork = src.startsWith('data:image/svg+xml;base64,')
            ? Buffer.from(src.split(',')[1], 'base64').toString('utf8')
            : decodeURIComponent(src)
        assert(src.includes(name) || artwork.includes(alt.split(' – ')[0]))
        assert.equal(new URL(href).searchParams.get('a'), expected)
    }
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
    assert.deepEqual(errors, [])
}

try {
    for (const width of [1440, 375, 320]) {
        const { page, errors } = await visit(width, before)
        await page.waitForSelector('img[alt^="Björn Borg Black Week"]')
        await page.waitForFunction(() => window.__campaignExpiry.length >= 2)
        await page.hover('.ad-container')
        await page.evaluate((after) => {
            window.__campaignNow = after
            for (const expire of window.__campaignExpiry) expire()
        }, after)
        await page.waitForFunction(
            () => !document.querySelector('img[alt^="Björn Borg Black Week"]')
        )
        await verify(page, errors)
        await page.close()

        const fresh = await visit(width, after)
        await verify(fresh.page, fresh.errors)
        await fresh.page.close()
        console.log(
            `PASS ${width}px: midnight expiry, fresh-page hydration, image/link pairs and layout`
        )
    }
} finally {
    await browser.close()
}
