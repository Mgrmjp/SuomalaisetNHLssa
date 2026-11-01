// @ts-nocheck
import { base } from '$app/paths'
import { fetchWithTimeout } from '$lib/utils/apiHelpers.js'
import { selectDailyNews } from '$lib/utils/dailyNews.js'

const REFRESH_MS = 60 * 60 * 1000
let cachedIndex = null
let loadedAt = 0
let pending = null

async function loadDailyNewsIndex() {
    if (cachedIndex && Date.now() - loadedAt < REFRESH_MS) return cachedIndex
    if (!pending) {
        pending = (async () => {
            try {
                const response = await fetchWithTimeout(`${base}/data/daily-news.json`, 10000, {
                    cache: 'no-store',
                })
                if (!response.ok) throw new Error('News unavailable')
                const index = await response.json()
                if (
                    !index?.byDate ||
                    typeof index.byDate !== 'object' ||
                    Array.isArray(index.byDate)
                )
                    throw new Error('Invalid news index')
                cachedIndex = index
                loadedAt = Date.now()
            } catch {
                // Preserve the last good index; selection still enforces publication expiry.
            } finally {
                pending = null
            }
            return cachedIndex || { byDate: {} }
        })()
    }
    return pending
}

export async function getDailyFallbackNews(date, limit = 2) {
    if (!date) return []
    return selectDailyNews(await loadDailyNewsIndex(), date, limit)
}
