// @ts-nocheck

const GENERIC_TITLE_PATTERNS = [/^NHL-lähde julkaisi NHL-uutisen\b/i]
const GENERIC_SUMMARY_PATTERNS = [
    /\bNHL-aiheisen jutun\b/i,
    /\bAlkuperäinen kuvaus:/i,
    /\bAlkuperäinen otsikko:/i,
]

const NOISE_TEXT_PATTERNS = [
    /discover a winning edge at vsin/i,
    /\bbetting splits\b/i,
    /\breal-time odds\b/i,
    /\blive broadcasts?\b/i,
    /we and our third-party partners may use cookies/i,
    /\bpersonalized advertising\b/i,
    /\blive scoring leaders?\b/i,
    /\bplay fantasy hockey\b/i,
    /\bsubscribers only\b/i,
    /\bissues by year\b/i,
]

const NOISE_TITLE_PATTERNS = [
    /^schedule\s*\|/i,
    /^nhl scores\b/i,
    /\bscores and schedule\b/i,
    /\bstandings\b/i,
    /\blive updates\b/i,
    /\bgame center\b/i,
    /\barchive\b/i,
    /\bcookies?\b/i,
    /\bbetting\b/i,
    /\bhighlights?\b/i,
    /\bpost game\b/i,
    /^review of .* nhl games\b/i,
    /^daily nhl recap\b/i,
    /\bplayoff board update\b/i,
]

const NOISE_URL_PATTERNS = [
    /\/info\/cookies/i,
    /\/partner\/vsin/i,
    /\/stats\//i,
    /\/schedule\//i,
    /archive\.thehockeynews\.com/i,
]

const SOURCE_LABELS = {
    archive: 'Archive',
    espnpressroom: 'ESPN Press Room',
    headlinehockey: 'Headline Hockey',
    'hockey-reference': 'Hockey-Reference',
    insidetherink: 'Inside the Rink',
    'insidetherink com': 'Inside the Rink',
    media: 'NHL Media',
    msn: 'MSN',
    nhl: 'NHL.com',
    nytimes: 'The Athletic',
    plaintextsports: 'Plain Text Sports',
    prohockeynews: 'Pro Hockey News',
    prohockeyrumors: 'Pro Hockey Rumors',
    spectorshockey: 'Spectors Hockey',
    'sportsnews-365': 'SportsNews 365',
    thehockeynews: 'The Hockey News',
    thehockeywriters: 'The Hockey Writers',
    youtube: 'YouTube',
}

const TRUSTED_NEWS_DOMAINS = new Set([
    'nhl.com',
    'media.nhl.com',
    'sportsnet.ca',
    'nytimes.com',
    'theathletic.com',
    'espn.com',
    'thehockeywriters.com',
    'spectorshockey.net',
    'thehockeynews.com',
    'prohockeyrumors.com',
    'insidetherink.com',
])

const LOW_VALUE_TITLE_HINTS = [
    'free picks',
    'predictions',
    'dawg of the day',
    'best bets',
    'betting',
    'odds',
    'live stream',
]

const LOW_VALUE_SUMMARY_HINTS = [
    'pickdawgz',
    'best bets',
    'betting splits',
    'real-time odds',
    'winning edge',
]

const CATEGORY_CONFIG = [
    {
        key: 'rumors',
        patterns: [/rumor roundup/i, /rumor mill/i, /trade board/i],
        title: (dateLabel) => (dateLabel ? `NHL:n huhukatsaus ${dateLabel}` : 'NHL:n huhukatsaus'),
        summary: 'Kooste päivän siirtohuhuista ja puheenaiheista NHL:ssä.',
    },
    {
        key: 'recap',
        patterns: [
            /morning recap/i,
            /preseason roundup/i,
            /recap of nhl/i,
            /recap of stanley cup playoffs/i,
        ],
        title: (dateLabel) =>
            dateLabel ? `NHL:n kierroskatsaus ${dateLabel}` : 'NHL:n kierroskatsaus',
        summary: 'Yhteenveto päivän NHL-otteluista ja käännekohdista.',
    },
    {
        key: 'morning-skate',
        patterns: [/morning skate/i],
        title: (dateLabel) => (dateLabel ? `NHL:n aamukatsaus ${dateLabel}` : 'NHL:n aamukatsaus'),
        summary: 'Kooste päivän tärkeimmistä NHL-uutisista ja ottelunostoista.',
    },
    {
        key: 'headlines',
        patterns: [/morning coffee headlines/i, /\bbuzz\b/i],
        title: (dateLabel) =>
            dateLabel ? `NHL:n päivän puheenaiheet ${dateLabel}` : 'NHL:n päivän puheenaiheet',
        summary: 'Kooste päivän tärkeimmistä NHL-uutisista ja puheenaiheista.',
    },
    {
        key: 'key-stories',
        patterns: [/five key stories/i],
        title: (dateLabel) =>
            dateLabel ? `NHL:n viikon puheenaiheet ${dateLabel}` : 'NHL:n viikon puheenaiheet',
        summary: 'Kooste viikon tärkeimmistä NHL-uutisista ja puheenaiheista.',
    },
    {
        key: 'playoffs',
        patterns: [/playoffs buzz/i, /stanley cup playoffs buzz/i],
        title: (dateLabel) =>
            dateLabel ? `NHL:n pudotuspeliseuranta ${dateLabel}` : 'NHL:n pudotuspeliseuranta',
        summary: 'Tilannekatsaus pudotuspeleihin ja sarjojen tärkeimpiin puheenaiheisiin.',
    },
    {
        key: 'analysis',
        patterns: [/trade deadline aftermath/i, /\banalysis\b/i],
        title: (dateLabel) => (dateLabel ? `NHL-analyysi ${dateLabel}` : 'NHL-analyysi'),
        summary: 'Taustoittava katsaus päivän NHL-aiheeseen.',
    },
]

function getIsoWeekParts(dateString) {
    const date = new Date(`${dateString}T00:00:00Z`)
    const working = new Date(date)
    const day = working.getUTCDay() || 7
    working.setUTCDate(working.getUTCDate() + 4 - day)

    const yearStart = new Date(Date.UTC(working.getUTCFullYear(), 0, 1))
    const week = Math.ceil(((working - yearStart) / 86400000 + 1) / 7)

    return {
        year: working.getUTCFullYear(),
        week,
    }
}

function normalizeWhitespace(text) {
    return typeof text === 'string' ? text.replace(/\s+/g, ' ').trim() : ''
}

function truncate(text, limit = 220) {
    const normalized = normalizeWhitespace(text)
    if (normalized.length <= limit) {
        return normalized
    }

    return `${normalized.slice(0, limit - 1).trimEnd()}…`
}

function formatFinnishDate(dateString) {
    if (!dateString || typeof dateString !== 'string') {
        return ''
    }

    const [year, month, day] = dateString.split('-')
    if (!year || !month || !day) {
        return ''
    }

    return `${Number(day)}.${Number(month)}.${year}`
}

function matchesAnyPattern(value, patterns) {
    return Boolean(value) && patterns.some((pattern) => pattern.test(value))
}

function isGenericFallbackTitle(title) {
    return matchesAnyPattern(normalizeWhitespace(title), GENERIC_TITLE_PATTERNS)
}

function isGenericFallbackSummary(summary) {
    return matchesAnyPattern(normalizeWhitespace(summary), GENERIC_SUMMARY_PATTERNS)
}

function inferSourceLabel(source, url) {
    const normalizedSource = normalizeWhitespace(source)
    const sourceKey = normalizedSource.toLowerCase()

    if (SOURCE_LABELS[sourceKey]) {
        return SOURCE_LABELS[sourceKey]
    }

    if (normalizedSource) {
        return normalizedSource
    }

    try {
        const hostname = new URL(url).hostname.replace(/^www\./, '').toLowerCase()
        const mapped = SOURCE_LABELS[hostname] || SOURCE_LABELS[hostname.split('.')[0]]
        if (mapped) {
            return mapped
        }

        const primaryLabel = hostname.split('.').slice(0, 2).join(' ')
        return primaryLabel.replace(/\b\w/g, (letter) => letter.toUpperCase())
    } catch {
        return ''
    }
}

function inferCategory(...parts) {
    const combinedText = parts.map((part) => normalizeWhitespace(part).toLowerCase()).join(' ')

    for (const config of CATEGORY_CONFIG) {
        if (config.patterns.some((pattern) => pattern.test(combinedText))) {
            return config
        }
    }

    return null
}

function getHost(url) {
    try {
        const hostname = new URL(url).hostname.toLowerCase()
        const normalizedHostname = hostname.startsWith('www.') ? hostname.slice(4) : hostname
        return normalizedHostname
    } catch {
        return ''
    }
}

function canonicalizeUrl(url) {
    const normalizedUrl = normalizeWhitespace(url)
    if (!normalizedUrl) return ''

    try {
        const parsed = new URL(normalizedUrl)
        parsed.hash = ''
        const trackingKeys = [
            'utm_source',
            'utm_medium',
            'utm_campaign',
            'utm_term',
            'utm_content',
            'fbclid',
            'gclid',
            'igshid',
        ]

        for (const key of trackingKeys) {
            parsed.searchParams.delete(key)
        }

        const sortedParams = [...parsed.searchParams.entries()].sort((a, b) =>
            a[0] === b[0] ? a[1].localeCompare(b[1]) : a[0].localeCompare(b[0])
        )
        parsed.search = ''
        for (const [key, value] of sortedParams) {
            parsed.searchParams.append(key, value)
        }

        const loweredHost = parsed.hostname.toLowerCase()
        parsed.hostname = loweredHost.startsWith('www.') ? loweredHost.slice(4) : loweredHost
        if (parsed.pathname !== '/' && parsed.pathname.endsWith('/')) {
            parsed.pathname = parsed.pathname.slice(0, -1)
        }

        return parsed.toString()
    } catch {
        return normalizedUrl
    }
}

function semanticTitleKey(title) {
    const lower = normalizeWhitespace(title).toLowerCase()
    if (!lower) return ''

    const words = lower
        .split(' ')
        .map((word) => {
            const chars = []
            for (const char of word) {
                const code = char.charCodeAt(0)
                const isNumber = code >= 48 && code <= 57
                const isLowerAlpha = code >= 97 && code <= 122
                if (isNumber || isLowerAlpha) {
                    chars.push(char)
                }
            }
            return chars.join('')
        })
        .filter((word) => word.length > 2)

    return words.slice(0, 10).join(' ')
}

function scoreNewsItem(item) {
    const title = normalizeWhitespace(item.title).toLowerCase()
    const summary = normalizeWhitespace(item.summary).toLowerCase()
    const source = normalizeWhitespace(item.source).toLowerCase()
    const host = getHost(item.url)
    let score = 0

    if (TRUSTED_NEWS_DOMAINS.has(host)) score += 3
    else if (SOURCE_LABELS[source]) score += 1

    if (title.includes('nhl') || title.includes('stanley cup')) score += 1
    if (summary.length >= 80) score += 1

    const combined = `${title} ${summary}`
    if (LOW_VALUE_TITLE_HINTS.some((hint) => combined.includes(hint))) score -= 4
    if (LOW_VALUE_SUMMARY_HINTS.some((hint) => combined.includes(hint))) score -= 3
    if (host.includes('youtube.com') && source !== 'nhl media') score -= 2

    if (isNoiseNewsItem(item)) score -= 6

    return score
}

function isNoiseNewsItem({ title, summary, translatedTitle, translatedSummary, url }) {
    const titleText = normalizeWhitespace(title)
    const summaryText = normalizeWhitespace(summary)
    const translatedTitleText = normalizeWhitespace(translatedTitle)
    const translatedSummaryText = normalizeWhitespace(translatedSummary)
    const combinedText = [titleText, summaryText, translatedTitleText, translatedSummaryText]
        .filter(Boolean)
        .join(' ')

    if (matchesAnyPattern(combinedText, NOISE_TEXT_PATTERNS)) {
        return true
    }

    if (matchesAnyPattern(titleText, NOISE_TITLE_PATTERNS)) {
        return true
    }

    return matchesAnyPattern(normalizeWhitespace(url), NOISE_URL_PATTERNS)
}

function buildFallbackTitle(item, category) {
    const dateLabel = formatFinnishDate(item.matchedDate)
    if (category) {
        return category.title(dateLabel)
    }

    return normalizeWhitespace(item.title)
}

function buildFallbackSummary(item, category) {
    if (category) {
        return category.summary
    }

    return truncate(item.summary || item.title)
}

export function normalizeDailyNewsItem(item) {
    if (!item || typeof item !== 'object') {
        return null
    }

    const hasNewsFields = [
        item.title,
        item.summary,
        item.translatedTitle,
        item.translatedSummary,
        item.url,
        item.source,
        item.matchedDate,
    ].some(Boolean)

    if (!hasNewsFields) {
        return item
    }

    if (isNoiseNewsItem(item)) {
        return null
    }

    const title = normalizeWhitespace(item.title)
    const summary = normalizeWhitespace(item.summary)
    const translatedTitle = normalizeWhitespace(item.translatedTitle)
    const translatedSummary = normalizeWhitespace(item.translatedSummary)
    const category = inferCategory(title, summary, translatedTitle, translatedSummary)

    const nextTitle = isGenericFallbackTitle(translatedTitle)
        ? buildFallbackTitle(item, category)
        : translatedTitle || buildFallbackTitle(item, category)

    const nextSummary = isGenericFallbackSummary(translatedSummary)
        ? buildFallbackSummary(item, category)
        : translatedSummary || buildFallbackSummary(item, category)

    if (isNoiseNewsItem({ title: nextTitle, summary: nextSummary, url: item.url })) {
        return null
    }

    return {
        ...item,
        source: inferSourceLabel(item.source, item.url),
        title,
        summary: truncate(summary),
        translatedTitle: nextTitle,
        translatedSummary: truncate(nextSummary),
    }
}

function collectNewsItems(items, limit) {
    const seen = new Set()
    const normalizedItems = []

    for (const item of Array.isArray(items) ? items : []) {
        const normalizedItem = normalizeDailyNewsItem(item)
        if (!normalizedItem) {
            continue
        }

        const key =
            canonicalizeUrl(normalizedItem.url) ||
            semanticTitleKey(normalizedItem.translatedTitle || normalizedItem.title) ||
            normalizeWhitespace(normalizedItem.id)

        if (!key || seen.has(key)) {
            continue
        }

        seen.add(key)
        normalizedItems.push(normalizedItem)
    }

    return normalizedItems
        .map((item) => ({ item, score: scoreNewsItem(item) }))
        .filter((entry) => entry.score >= 0)
        .sort((a, b) => {
            if (b.score !== a.score) return b.score - a.score
            const aSummary = normalizeWhitespace(a.item.translatedSummary || a.item.summary)
            const bSummary = normalizeWhitespace(b.item.translatedSummary || b.item.summary)
            return bSummary.length - aSummary.length
        })
        .slice(0, limit)
        .map((entry) => entry.item)
}

export function getIsoWeekKey(dateString) {
    if (!dateString || typeof dateString !== 'string') {
        return ''
    }

    const { year, week } = getIsoWeekParts(dateString)
    return `${year}-W${String(week).padStart(2, '0')}`
}

export function selectDailyNews(newsIndex, dateString, limit = 3) {
    if (!newsIndex || !dateString) {
        return []
    }

    const exactItems = collectNewsItems(newsIndex.byDate?.[dateString], limit)
    if (exactItems.length > 0) {
        return exactItems
    }

    const weekKey = getIsoWeekKey(dateString)
    const weeklyItems = collectNewsItems(newsIndex.byWeek?.[weekKey], limit)

    return weeklyItems
}
