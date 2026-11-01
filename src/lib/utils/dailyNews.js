// @ts-nocheck
const MAX_AGE_MS = 48 * 60 * 60 * 1000
const GENERIC =
    /NHL:n (?:päivän puheenaiheet|huhukatsaus|kierroskatsaus|aamukatsaus|viikon puheenaiheet|pudotuspeliseuranta)|NHL-lähde julkaisi|Kooste päivän|Alkuperäinen (?:kuvaus|otsikko)/i
const fold = (text) =>
    String(text || '')
        .normalize('NFKD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/\s+/g, ' ')
        .trim()
const finnishDate = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Helsinki' })

function canonicalUrl(url) {
    try {
        const parsed = new URL(url)
        if (parsed.protocol !== 'https:' || parsed.username || parsed.password) return ''
        parsed.hash = ''
        parsed.hostname = parsed.hostname.replace(/^www\./, '')
        parsed.pathname = parsed.pathname.replace(/\/$/, '')
        for (const key of [...parsed.searchParams.keys()]) {
            if (key.startsWith('utm_') || ['fbclid', 'gclid'].includes(key))
                parsed.searchParams.delete(key)
        }
        parsed.searchParams.sort()
        return parsed.toString()
    } catch {
        return ''
    }
}

export function normalizeDailyNewsItem(item) {
    if (
        !item ||
        typeof item.title !== 'string' ||
        item.publicationVerified !== true ||
        !['article:published_time', 'schema.org:datePublished'].includes(item.publicationSource) ||
        !/T.*(?:Z|[+-]\d{2}:?\d{2})$/.test(item.publishedAt || '') ||
        !Number.isFinite(Date.parse(item.publishedAt)) ||
        !canonicalUrl(item.url) ||
        !Array.isArray(item.matchedPlayers) ||
        !item.matchedPlayers.length
    )
        return null
    const headline = ` ${fold(item.title).replace(/[^a-z0-9]+/g, ' ')} `
    const namedSubject = item.matchedPlayers.some((name) => {
        const full = fold(name).replace(/[^a-z0-9]+/g, ' ')
        const surname = full.split(' ').at(-1)
        return (
            full &&
            (headline.includes(` ${full} `) || (surname && headline.includes(` ${surname} `)))
        )
    })
    if (!namedSubject) return null
    const verifiedTranslation =
        item.translationSourceTitle === item.title &&
        item.translationSourceSummary === item.summary &&
        !GENERIC.test(`${item.translatedTitle || ''} ${item.translatedSummary || ''}`)
    return {
        ...item,
        url: canonicalUrl(item.url),
        translatedTitle:
            verifiedTranslation && item.translatedTitle ? item.translatedTitle : item.title,
        translatedSummary:
            verifiedTranslation && item.translatedSummary
                ? item.translatedSummary
                : item.summary || '',
    }
}

export function selectDailyNews(newsIndex, dateString, limit = 2, now = new Date()) {
    if (!newsIndex || !dateString) return []
    const end = new Date(now).getTime()
    if (!Number.isFinite(end)) return []
    const items = Object.values(newsIndex.byDate || {})
        .flatMap((bucket) => (Array.isArray(bucket) ? bucket : []))
        .map(normalizeDailyNewsItem)
        .filter(Boolean)
        .filter((item) => {
            const published = Date.parse(item.publishedAt)
            return (
                published <= end &&
                published >= end - MAX_AGE_MS &&
                finnishDate.format(new Date(published)) <= dateString
            )
        })
        .sort((a, b) => Date.parse(b.publishedAt) - Date.parse(a.publishedAt))
    const urls = new Set()
    const titles = new Set()
    return items
        .filter((item) => {
            const title = fold(item.title)
            if (urls.has(item.url) || titles.has(title)) return false
            urls.add(item.url)
            titles.add(title)
            return true
        })
        .slice(0, Math.max(0, Math.min(2, limit)))
}
