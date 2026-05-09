// @ts-nocheck

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

    const exactItems = Array.isArray(newsIndex.byDate?.[dateString])
        ? newsIndex.byDate[dateString]
        : []
    if (exactItems.length > 0) {
        return exactItems.slice(0, limit)
    }

    const weekKey = getIsoWeekKey(dateString)
    const weeklyItems = Array.isArray(newsIndex.byWeek?.[weekKey]) ? newsIndex.byWeek[weekKey] : []

    return weeklyItems.slice(0, limit)
}
