import { describe, expect, it } from 'vitest'

import { getIsoWeekKey, normalizeDailyNewsItem, selectDailyNews } from '$lib/utils/dailyNews.js'

describe('dailyNews helpers', () => {
    it('builds ISO week keys from daily dates', () => {
        expect(getIsoWeekKey('2026-04-13')).toBe('2026-W16')
        expect(getIsoWeekKey('2025-12-31')).toBe('2026-W01')
    })

    it('prefers exact-date news over weekly fallback', () => {
        const newsIndex = {
            byDate: {
                '2026-04-13': [{ id: 'exact-1' }, { id: 'exact-2' }],
            },
            byWeek: {
                '2026-W16': [{ id: 'week-1' }],
            },
        }

        expect(selectDailyNews(newsIndex, '2026-04-13')).toEqual([
            { id: 'exact-1' },
            { id: 'exact-2' },
        ])
    })

    it('falls back to weekly news when the exact date is missing', () => {
        const newsIndex = {
            byDate: {},
            byWeek: {
                '2026-W16': [
                    { id: 'week-1' },
                    { id: 'week-2' },
                    { id: 'week-3' },
                    { id: 'week-4' },
                ],
            },
        }

        expect(selectDailyNews(newsIndex, '2026-04-15')).toEqual([
            { id: 'week-1' },
            { id: 'week-2' },
            { id: 'week-3' },
        ])
    })

    it('normalizes generic fallback translations into readable news cards', () => {
        const normalized = normalizeDailyNewsItem({
            title: 'NHL Rumor Mill – May 6, 2026',
            summary:
                "Check out the latest on the Penguins, Bruins, Blue Jackets, and Sharks in today's NHL Rumor Mill.",
            source: '',
            url: 'https://www.spectorshockey.net/2026/05/nhl-rumor-mill-may-6-2026/',
            matchedDate: '2026-05-09',
            translatedTitle: 'NHL-lähde julkaisi NHL-uutisen 9.5.2026',
            translatedSummary:
                " julkaisi 9.5.2026 NHL-aiheisen jutun. Alkuperäinen kuvaus: Check out the latest on the Penguins, Bruins, Blue Jackets, and Sharks in today's NHL Rumor Mill.",
        })

        expect(normalized).toMatchObject({
            source: 'Spectors Hockey',
            translatedTitle: 'NHL:n huhukatsaus 9.5.2026',
            translatedSummary: 'Kooste päivän siirtohuhuista ja puheenaiheista NHL:ssä.',
        })
    })

    it('filters cookie banners, betting promos, and stat pages out of the fallback news', () => {
        const newsIndex = {
            byDate: {
                '2026-05-16': [
                    {
                        title: 'NHL betting',
                        summary:
                            'Discover a winning edge at VSiN! Gain expert insights, exclusive tips, betting splits, real-time odds, and live broadcasts.',
                        url: 'https://www.nhl.com/partner/vsin',
                    },
                    {
                        title: 'NHL cookie notice',
                        summary:
                            'We and our third-party partners may use cookies and similar technologies to enhance site navigation.',
                        url: 'https://www.nhl.com/info/cookies',
                    },
                    {
                        title: 'NHL live leaders',
                        summary:
                            'Get the latest NHL live scoring leaders on May 16, 2026. Play fantasy hockey, follow players from around the NHL, and more.',
                        url: 'https://www.nhl.com/stats/skaters',
                    },
                    {
                        title: '2025-26 NHL Scores and Schedule 20/10/2025 - The Athletic',
                        summary:
                            'Full schedule for the 2025-26 NHL season with a list of matchups, game times, TV channels, scores, and stadium information.',
                        url: 'https://www.nytimes.com/athletic/nhl/schedule/2025-10-20/',
                    },
                ],
            },
            byWeek: {},
        }

        expect(selectDailyNews(newsIndex, '2026-05-16')).toEqual([])
    })

    it('uses weekly fallback when exact-date items are filtered out as junk', () => {
        const newsIndex = {
            byDate: {
                '2026-05-16': [
                    {
                        title: 'NHL cookie notice',
                        summary:
                            'We and our third-party partners may use cookies and similar technologies to enhance site navigation.',
                        url: 'https://www.nhl.com/info/cookies',
                    },
                ],
            },
            byWeek: {
                '2026-W20': [
                    {
                        title: 'NHL Morning Recap – May 16, 2026',
                        summary:
                            'Today, we will be looking at the scores of all NHL games played on May 15, 2026.',
                        source: 'Thehockeywriters',
                        url: 'https://thehockeywriters.com/nhl-morning-recap-may-16-2026/',
                        matchedDate: '2026-05-16',
                    },
                ],
            },
        }

        expect(selectDailyNews(newsIndex, '2026-05-16')).toMatchObject([
            {
                translatedTitle: 'NHL:n kierroskatsaus 16.5.2026',
                translatedSummary: 'Yhteenveto päivän NHL-otteluista ja käännekohdista.',
            },
        ])
    })

    it('prioritizes higher-quality trusted stories over promo-like entries', () => {
        const newsIndex = {
            byDate: {
                '2026-05-27': [
                    {
                        title: 'NHL Free Picks and Predictions for Today 5/27/2026',
                        summary: 'Dawg of the Day and best bets for tonight.',
                        source: 'YouTube',
                        url: 'https://www.youtube.com/watch?v=dKt_SVMmC54',
                    },
                    {
                        title: 'Stanley Cup Playoffs Edition – May 27, 2026',
                        summary:
                            "Undrafted forward Cole Smith scored the series-clinching goal to propel the Golden Knights to a sweep of the Presidents' Trophy winners.",
                        source: 'NHL Media',
                        url: 'https://media.nhl.com/public/news/19859',
                        matchedDate: '2026-05-27',
                    },
                ],
            },
            byWeek: {},
        }

        const selected = selectDailyNews(newsIndex, '2026-05-27')
        expect(selected).toHaveLength(1)
        expect(selected[0]).toMatchObject({
            source: 'NHL Media',
            url: 'https://media.nhl.com/public/news/19859',
        })
    })

    it('dedupes equivalent stories with tracking query differences', () => {
        const newsIndex = {
            byDate: {
                '2026-05-30': [
                    {
                        title: 'NHL Morning Recap – May 30, 2026',
                        summary: 'Daily NHL recap with key game takeaways and player performances.',
                        source: 'The Hockey Writers',
                        url: 'https://thehockeywriters.com/nhl-morning-recap-may-30-2026/?utm_source=x',
                    },
                    {
                        title: 'NHL Morning Recap – May 30, 2026',
                        summary: 'Daily NHL recap with key game takeaways and player performances.',
                        source: 'The Hockey Writers',
                        url: 'https://www.thehockeywriters.com/nhl-morning-recap-may-30-2026/',
                    },
                ],
            },
            byWeek: {},
        }

        const selected = selectDailyNews(newsIndex, '2026-05-30')
        expect(selected).toHaveLength(1)
    })

    it('keeps mainstream non-promo stories available for fallback cards', () => {
        const newsIndex = {
            byDate: {
                '2026-05-27': [
                    {
                        title: "NHL's top 12 UFAs of 2026: Latest rumours, reports - Sportsnet",
                        summary:
                            'Consider the long list of star talent who had the option of going to the highest bidder on Canada Day but instead elected to re-up with their current team.',
                        source: 'Sportsnet Ca',
                        url: 'https://www.sportsnet.ca/nhl/article/nhls-top-12-ufas-of-2026-latest-rumours-reports',
                        matchedDate: '2026-05-27',
                    },
                ],
            },
            byWeek: {},
        }

        const selected = selectDailyNews(newsIndex, '2026-05-27')
        expect(selected).toHaveLength(1)
        expect(selected[0].translatedTitle).toBe(
            "NHL's top 12 UFAs of 2026: Latest rumours, reports - Sportsnet"
        )
    })
})
