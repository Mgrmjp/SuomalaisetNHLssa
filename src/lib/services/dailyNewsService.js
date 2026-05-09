// @ts-nocheck

import { fetchLocalJSON } from '$lib/utils/apiHelpers.js'
import { selectDailyNews } from '$lib/utils/dailyNews.js'

let dailyNewsIndexPromise = null

async function loadDailyNewsIndex() {
    if (!dailyNewsIndexPromise) {
        dailyNewsIndexPromise = fetchLocalJSON('/data/daily-news.json')
    }

    return (await dailyNewsIndexPromise) || { byDate: {}, byWeek: {} }
}

export async function getDailyFallbackNews(date, limit = 3) {
    if (!date) {
        return []
    }

    const index = await loadDailyNewsIndex()
    return selectDailyNews(index, date, limit)
}
