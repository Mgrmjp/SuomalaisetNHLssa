// @ts-nocheck
import { describe, expect, it } from 'vitest'
import { normalizeDailyNewsItem, selectDailyNews } from '$lib/utils/dailyNews.js'

const now = new Date('2026-11-01T12:00:00Z')
const article = (extra = {}) => ({
    title: 'Aleksander Barkov returns to practice',
    summary: 'Barkov returned to Panthers practice after an injury.',
    url: 'https://www.nhl.com/panthers/news/barkov-update',
    source: 'NHL.com',
    publishedAt: '2026-11-01T09:00:00Z',
    publicationVerified: true,
    publicationSource: 'article:published_time',
    matchedPlayers: ['Aleksander Barkov'],
    ...extra,
})
const select = (items) => selectDailyNews({ byDate: { '2026-11-01': items } }, '2026-11-01', 2, now)

describe('verified Finnish NHL news', () => {
    it('rejects missing, unverified, old, future and date-only publication dates', () => {
        for (const extra of [
            { publishedAt: undefined },
            { publicationVerified: false },
            { publishedAt: '2026-10-30T11:59:59Z' },
            { publishedAt: '2026-11-01T12:00:01Z' },
            { publishedAt: '2026-11-01' },
        ]) {
            expect(select([article(extra)])).toEqual([])
        }
        expect(select([article({ publishedAt: '2026-10-30T12:00:00Z' })])).toHaveLength(1)
    })
    it('requires a Finnish player in the headline, not a passing summary mention', () => {
        expect(select([article({ title: 'NHL morning roundup' })])).toEqual([])
        expect(select([article({ matchedPlayers: [] })])).toEqual([])
        expect(select([article({ url: 'javascript:alert(1)' })])).toEqual([])
    })
    it('never uses generic dated titles or summaries as translations', () => {
        const result = normalizeDailyNewsItem(
            article({
                translatedTitle: 'NHL:n päivän puheenaiheet 1.11.2026',
                translatedSummary: 'Kooste päivän tärkeimmistä NHL-uutisista.',
            })
        )
        expect(result.translatedTitle).toBe(article().title)
        expect(result.translatedSummary).toBe(article().summary)
    })
    it('preserves verified faithful translations tied to the original text', () => {
        const item = article({
            translatedTitle: 'Aleksander Barkov palasi harjoituksiin',
            translatedSummary: 'Barkov palasi Panthersin harjoituksiin loukkaantumisen jälkeen.',
            translationSourceTitle: article().title,
            translationSourceSummary: article().summary,
        })
        expect(normalizeDailyNewsItem(item).translatedTitle).toBe(item.translatedTitle)
    })
    it('deduplicates stories and shows at most two, newest first', () => {
        const items = [
            article({ publishedAt: '2026-11-01T08:00:00Z' }),
            article({ url: `${article().url}?utm_source=test` }),
            article({
                title: 'Sebastian Aho scores',
                matchedPlayers: ['Sebastian Aho'],
                url: 'https://www.nhl.com/hurricanes/news/aho',
                publishedAt: '2026-11-01T10:00:00Z',
            }),
            article({
                title: 'Barkov speaks after practice',
                url: 'https://www.nhl.com/panthers/news/interview',
            }),
        ]
        const result = select(items)
        expect(result).toHaveLength(2)
        expect(result[0].title).toBe('Sebastian Aho scores')
        expect(new Set(result.map((item) => item.url)).size).toBe(2)
    })
    it('does not use unverified weekly fallbacks or display articles on dates before publication', () => {
        expect(
            selectDailyNews({ byWeek: { '2026-W44': [article()] } }, '2026-11-01', 2, now)
        ).toEqual([])
        expect(
            selectDailyNews({ byDate: { '2026-11-01': [article()] } }, '2026-10-31', 2, now)
        ).toEqual([])
    })
})
