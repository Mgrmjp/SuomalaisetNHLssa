#!/usr/bin/env node

const fs = require('node:fs')
const path = require('node:path')

const buildDir = path.resolve(process.cwd(), 'build')
const siteOrigin = 'https://suomalaisetnhlssa.fi'
const placeholderPatterns = [
    /\{displayName\}/,
    /\{formattedSeason\}/,
    /\{player\.gamesPlayed\}/,
    /cms\.nhk\.bamgrid\.com\/images\/https?:\/\//,
    /<title>Suomalaiset NHL-pelaajat<\/title>/,
]

function fail(message) {
    console.error(`SEO validation failed: ${message}`)
    process.exitCode = 1
}

function read(file) {
    return fs.readFileSync(file, 'utf-8')
}

function listFiles(dir, extension) {
    const files = []
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const fullPath = path.join(dir, entry.name)
        if (entry.isDirectory()) {
            files.push(...listFiles(fullPath, extension))
        } else if (entry.isFile() && entry.name.endsWith(extension)) {
            files.push(fullPath)
        }
    }
    return files
}

function routeFromHtmlFile(file) {
    const relative = path.relative(buildDir, file)
    if (relative === 'index.html') return '/'
    if (relative.endsWith('/index.html')) {
        return `/${relative.slice(0, -'/index.html'.length)}`
    }
    return `/${relative.replace(/\.html$/, '')}`
}

function generatedPathForUrl(url) {
    const pathname = new URL(url).pathname
    if (pathname === '/') return path.join(buildDir, 'index.html')
    return path.join(buildDir, pathname, 'index.html')
}

function shouldSkipHtml(route, html) {
    if (route === '/200' || route === '/404') return true
    return html.includes('http-equiv="refresh"') && html.includes('location.href=')
}

function validateHtml(file) {
    const html = read(file)
    const route = routeFromHtmlFile(file)
    if (shouldSkipHtml(route, html)) return

    const titleCount = (html.match(/<title>/g) || []).length
    const descriptionCount = (html.match(/<meta name="description"/g) || []).length
    const canonicalCount = (html.match(/<link rel="canonical"/g) || []).length

    if (titleCount !== 1) fail(`${route} has ${titleCount} title tags`)
    if (descriptionCount !== 1) fail(`${route} has ${descriptionCount} meta descriptions`)
    if (canonicalCount !== 1) fail(`${route} has ${canonicalCount} canonical links`)

    for (const pattern of placeholderPatterns) {
        if (pattern.test(html)) fail(`${route} contains ${pattern}`)
    }
}

function validateSitemap() {
    const sitemapFile = path.join(buildDir, 'sitemap.xml')
    if (!fs.existsSync(sitemapFile)) {
        fail('build/sitemap.xml is missing')
        return
    }

    const sitemap = read(sitemapFile)
    const urls = Array.from(sitemap.matchAll(/<loc>([^<]+)<\/loc>/g), (match) => match[1])
    if (urls.length === 0) fail('sitemap.xml has no URLs')

    const seen = new Set()
    for (const url of urls) {
        if (!url.startsWith(siteOrigin)) {
            fail(`sitemap URL is outside ${siteOrigin}: ${url}`)
            continue
        }

        if (seen.has(url)) {
            fail(`sitemap contains duplicate URL: ${url}`)
            continue
        }
        seen.add(url)

        const outputFile = generatedPathForUrl(url)
        if (!fs.existsSync(outputFile)) {
            fail(`sitemap URL has no generated page: ${url}`)
        }
    }
}

if (!fs.existsSync(buildDir)) {
    fail('build directory is missing. Run npm run build:quick first.')
} else {
    for (const file of listFiles(buildDir, '.html')) {
        validateHtml(file)
    }
    validateSitemap()
}

if (process.exitCode) {
    process.exit(process.exitCode)
}

console.log('SEO validation passed')
