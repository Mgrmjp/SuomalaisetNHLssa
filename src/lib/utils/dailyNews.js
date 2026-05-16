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
            normalizeWhitespace(normalizedItem.url) ||
            normalizeWhitespace(normalizedItem.translatedTitle) ||
            normalizeWhitespace(normalizedItem.title) ||
            normalizeWhitespace(normalizedItem.id)

        if (!key || seen.has(key)) {
            continue
        }

        seen.add(key)
        normalizedItems.push(normalizedItem)

        if (normalizedItems.length >= limit) {
            break
        }
    }

    return normalizedItems
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
