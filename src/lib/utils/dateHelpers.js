export function formatDate(date) {
    if (typeof date === 'string') return date
    return date.toISOString().split('T')[0]
}
