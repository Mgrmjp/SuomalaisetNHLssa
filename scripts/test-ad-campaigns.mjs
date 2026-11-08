import assert from 'node:assert/strict'
import puppeteer from 'puppeteer'

const baseUrl = process.env.TEST_URL || 'http://localhost:3000'
const before = Date.parse('2026-11-30T23:59:00+02:00')
const after = Date.parse('2026-12-01T00:00:00+02:00')
const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] })

async function visit(width, now, imageFailure, randomValue) {
    const page = await browser.newPage()
    const errors = []
    page.on('pageerror', (error) => errors.push(error.message))
    page.on('console', (message) => {
        if (/hydration/i.test(message.text())) errors.push(message.text())
    })
    await page.setViewport({ width, height: 1000 })
    if (imageFailure) {
        await page.setRequestInterception(true)
        page.on('request', (request) => {
            if (
                request.resourceType() !== 'image' ||
                (!request.url().includes('track.adtraction.com') &&
                    !(imageFailure === 'all' && request.url().includes('-mobile.')))
            ) {
                return request.continue()
            } else if (imageFailure === 'network' || imageFailure === 'all') {
                return request.abort()
            } else {
                // An unavailable creative can return HTTP 200 with a transparent tracking pixel.
                return request.respond({
                    status: 200,
                    contentType: 'image/gif',
                    body: Buffer.from(
                        'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
                        'base64'
                    ),
                })
            }
        })
    }
    await page.evaluateOnNewDocument(
        ({ now, randomValue }) => {
            if (randomValue !== undefined) Math.random = () => randomValue
            const NativeDate = Date
            window.__campaignNow = now
            window.__campaignExpiry = []
            window.__adRotations = []
            const nativeInterval = window.setInterval.bind(window)
            window.setInterval = (callback, delay, ...args) => {
                if (delay === 20000) window.__adRotations.push(() => callback(...args))
                return nativeInterval(callback, delay, ...args)
            }
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
        },
        { now, randomValue }
    )
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
        assert.equal(
            await page.$$eval(selector, (nodes) => nodes.length),
            selector.includes('mobile-ad-container') ? 2 : 1
        )
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
    if (page.viewport().width < 768) await verifyMobileLayout(page)
    const labels = await page.$$eval(
        '.ad-slot--desktop, .mobile-ad-container, .vertical-ad-container, .vertical-ad-container-left',
        (slots) =>
            slots
                .filter((slot) => slot.getBoundingClientRect().height > 0)
                .map((slot) => {
                    const pills = [...slot.querySelectorAll('.ad-disclaimer')]
                    const pill = pills[0]
                    const bounds = slot.getBoundingClientRect()
                    const rect = pill?.getBoundingClientRect()
                    const creative = slot.querySelector('a.active')?.getBoundingClientRect()
                    const style = pill && getComputedStyle(pill)
                    return {
                        count: pills.length,
                        fontSize: style?.fontSize,
                        color: style?.color,
                        background: style?.backgroundColor,
                        inside:
                            rect &&
                            rect.top >= bounds.top &&
                            rect.left >= bounds.left &&
                            rect.right <= bounds.right &&
                            rect.bottom <= bounds.bottom,
                        above: rect && creative && rect.bottom <= creative.top,
                    }
                })
    )
    assert(labels.length > 0)
    for (const label of labels) {
        assert.equal(label.count, 1, 'Each placement keeps one stable Mainos pill during rotation')
        assert(
            label.inside && label.above,
            'The label stays above the creative and inside its slot'
        )
        assert.equal(label.fontSize, '11px')
        assert.equal(label.color, labels[0].color)
        assert.equal(label.background, labels[0].background)
    }
}

async function verifyMobileLayout(page) {
    await page.waitForFunction(() =>
        [...document.querySelectorAll('.mobile-ad-container img')].some(
            (image) => image.complete && image.naturalWidth > 1
        )
    )
    const slots = await page.$$eval('.mobile-ad-container, .ad-slot', (nodes) =>
        nodes
            .filter((node) => node.getBoundingClientRect().height > 0)
            .filter((node) => !node.querySelector('.mobile-ad-container'))
            .map((node) => {
                const active = node.querySelector('a.active')
                const image = active?.querySelector('img')
                const label = node.querySelector('.ad-disclaimer')
                const bounds = node.getBoundingClientRect()
                const labelBounds = label?.getBoundingClientRect()
                return {
                    width: image?.naturalWidth,
                    height: image?.naturalHeight,
                    labelInside:
                        !!labelBounds &&
                        labelBounds.top >= bounds.top &&
                        labelBounds.bottom <= bounds.bottom,
                    keyboardLinks: [...node.querySelectorAll('a')].filter(
                        (link) => link.tabIndex >= 0
                    ).length,
                }
            })
    )
    assert.equal(slots.length, 2, 'Mobile should show an ad between each visible player type')
    for (const slot of slots) {
        assert(
            slot.width > 1 && slot.height > 1,
            'The active creative must not be a tracking pixel or broken image'
        )
        assert(slot.labelInside, 'The Mainos label must fit inside its slot')
        assert.equal(slot.keyboardLinks, 1, 'Only the visible ad should be keyboard focusable')
    }
    const placements = await page.$$eval('.mobile-ad-container', (nodes) =>
        nodes.map((node) => ({
            nextGroup: node.nextElementSibling?.dataset.position,
            previousGroup: node
                .closest('.scoring-list__section')
                ?.previousElementSibling?.querySelector('h2')?.dataset.position,
        }))
    )
    assert.deepEqual(placements, [
        { previousGroup: 'forwards', nextGroup: 'defenders' },
        { previousGroup: 'defenders', nextGroup: 'goalies' },
    ])
    assert.equal(
        await page.$('.dashboard__ads .mobile-ad-container'),
        null,
        'No mobile ad in the footer'
    )
}

try {
    const seededSelections = []
    for (const randomValue of [0.01, 0.99]) {
        const { page } = await visit(375, after, 'pixel', randomValue)
        await page.waitForFunction(() =>
            [...document.querySelectorAll('.mobile-ad-container img')].every(
                (image) => image.complete
            )
        )
        const selections = await page.$$eval('.mobile-ad-container a.active', (nodes) =>
            nodes.map((node) => new URL(node.href).searchParams.get('a'))
        )
        assert.equal(
            new Set(selections).size,
            2,
            'Mobile placements should select different loaded ads'
        )
        seededSelections.push(selections)
        await page.close()
    }
    assert.notDeepEqual(
        seededSelections[0],
        seededSelections[1],
        'Random input must affect the initial selections'
    )
    console.log('PASS mobile randomization: different initial choices and separate placements')
    for (const imageFailure of ['pixel', 'network']) {
        const { page, errors } = await visit(343, after, imageFailure)
        await page.waitForFunction(
            () =>
                window.__adRotations.length >= 3 &&
                [...document.querySelectorAll('.mobile-ad-container img')].every(
                    (image) => image.complete
                )
        )
        await page.$$eval('.mobile-ad-container .ad-wrapper', (wrappers) => {
            for (const wrapper of wrappers) {
                wrapper.dispatchEvent(new PointerEvent('pointerenter', { pointerType: 'touch' }))
                wrapper.dispatchEvent(new MouseEvent('mouseenter'))
            }
        })
        for (let rotation = 0; rotation < 15; rotation++) {
            const previous = await page.$$eval('.mobile-ad-container a.active', (nodes) =>
                nodes.map((node) => node.href)
            )
            await page.evaluate(() => {
                for (const rotate of window.__adRotations) rotate()
            })
            await verifyMobileLayout(page)
            const next = await page.$$eval('.mobile-ad-container a.active', (nodes) =>
                nodes.map((node) => node.href)
            )
            assert(
                next.every((href, index) => href !== previous[index]),
                'Each placement rotates to another loaded ad'
            )
            assert.equal(new Set(next).size, 2, 'Rotating placements avoid duplicate ads')
        }
        assert.deepEqual(errors, [])
        await page.close()
        console.log(
            `PASS mobile ${imageFailure}: ads between player types, readable labels and keyboard links`
        )
    }
    const unavailable = await visit(343, after, 'all')
    await unavailable.page.waitForFunction(() => {
        const slots = [...document.querySelectorAll('.mobile-ad-container')]
        const images = slots.flatMap((slot) => [...slot.querySelectorAll('img')])
        return (
            images.length > 0 &&
            images.every((image) => image.complete) &&
            slots.every((slot) => slot.getBoundingClientRect().height === 0)
        )
    })
    assert.deepEqual(unavailable.errors, [])
    await unavailable.page.close()
    console.log('PASS mobile unavailable: failed slot collapses without an empty box')
    for (const width of [1920, 1440, 375, 320]) {
        const { page, errors } = await visit(width, before)
        await page.waitForSelector('img[alt^="Björn Borg Black Week"]')
        await page.waitForFunction(() => window.__campaignExpiry.length >= 3)
        if (width >= 768) await page.hover('.ad-container')
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
        if (width < 768) {
            await fresh.page.select('.scoring-list__controls select', 'defenders')
            await fresh.page.waitForFunction(() => !document.querySelector('.mobile-ad-container'))
            await fresh.page.select('.scoring-list__controls select', 'all')
            await verifyMobileLayout(fresh.page)
        } else {
            assert.equal(
                await fresh.page.$$eval(
                    '.mobile-ad-container',
                    (nodes) =>
                        nodes.filter((node) => node.getBoundingClientRect().height > 0).length
                ),
                0
            )
        }
        await fresh.page.close()
        console.log(
            `PASS ${width}px: midnight expiry, fresh-page hydration, image/link pairs and layout`
        )
    }
} finally {
    await browser.close()
}
