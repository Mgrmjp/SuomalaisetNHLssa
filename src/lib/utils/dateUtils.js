/**
 * Finnish date formatting utilities
 * Provides consistent Finnish date formatting for the NHL app
 */

/**
 * Format date in Finnish format with proper localization
 * @param {string | Date} date - Date to format
 * @param {Object} options - Formatting options
 * @returns {string} Formatted Finnish date string
 */
export function formatFinnishDate(date, options = {}) {
    const dateObj = typeof date === 'string' ? new Date(`${date}T00:00:00`) : date

    const { showYear = true, showWeekday = true, longFormat = false, capitalized = false } = options

    // Finnish month names
    const months = [
        'tammikuuta',
        'helmikuuta',
        'maaliskuuta',
        'huhtikuuta',
        'toukokuuta',
        'kesäkuuta',
        'heinäkuuta',
        'elokuuta',
        'syyskuuta',
        'lokakuuta',
        'marraskuuta',
        'joulukuuta',
    ]

    // Finnish weekday names
    const weekdays = [
        'sunnuntai',
        'maanantai',
        'tiistai',
        'keskiviikko',
        'torstai',
        'perjantai',
        'lauantai',
    ]

    const weekdayShort = ['su', 'ma', 'ti', 'ke', 'to', 'pe', 'la']

    const day = dateObj.getDate()
    const month = months[dateObj.getMonth()]
    const year = dateObj.getFullYear()
    const weekdayIndex = dateObj.getDay()

    let formattedDate = ''

    if (showWeekday) {
        if (longFormat) {
            formattedDate += `${weekdays[weekdayIndex]} `
        } else {
            formattedDate += `${weekdayShort[weekdayIndex]} `
        }
    }

    formattedDate += `${day}. ${month}`

    if (showYear) {
        formattedDate += ` ${year}`
    }

    if (capitalized) {
        return formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1)
    }

    return formattedDate
}

/**
 * Format date for display in date picker (short format)
 * @param {string | Date} date - Date to format
 * @returns {string} Short Finnish date format
 */
export function formatShortFinnishDate(date) {
    return formatFinnishDate(date, {
        showYear: false,
        showWeekday: true,
        longFormat: false,
    })
}

/**
 * Format date for full display (long format)
 * @param {string | Date} date - Date to format
 * @returns {string} Long Finnish date format
 */
export function formatLongFinnishDate(date) {
    return formatFinnishDate(date, {
        showYear: true,
        showWeekday: true,
        longFormat: true,
    })
}

/**
 * Format date for accessibility/screen readers
 * @param {string | Date} date - Date to format
 * @returns {string} Accessible Finnish date format
 */
export function formatAccessibleFinnishDate(date) {
    return formatFinnishDate(date, {
        showYear: true,
        showWeekday: true,
        longFormat: true,
        capitalized: true,
    })
}

/**
 * Get relative date description in Finnish
 * @param {string | Date} date - Date to compare
 * @param {Date} [referenceDate=new Date()] - Reference date (default: today)
 * @returns {string} Relative description (e.g., "tänään", "eilen", "huomenna")
 */
export function getRelativeFinnishDate(date, referenceDate = new Date()) {
    const dateObj = typeof date === 'string' ? new Date(`${date}T00:00:00`) : date

    // Normalize both dates to start of day
    const normalizedDate = new Date(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate())
    const normalizedRef = new Date(
        referenceDate.getFullYear(),
        referenceDate.getMonth(),
        referenceDate.getDate()
    )

    const diffTime = normalizedDate.getTime() - normalizedRef.getTime()
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

    switch (diffDays) {
        case 0:
            return 'tänään'
        case -1:
            return 'eilen'
        case 1:
            return 'huomenna'
        case -2:
            return 'toissapäivänä'
        case 2:
            return 'ylihuomenna'
        default:
            if (diffDays > 0 && diffDays <= 7) {
                return `${diffDays} päivän päästä`
            }
            if (diffDays < 0 && diffDays >= -7) {
                return `${Math.abs(diffDays)} päivää sitten`
            }
            return null // No relative description available
    }
}

/**
 * Format date with relative information if available
 * @param {string | Date} date - Date to format
 * @param {Object} options - Formatting options
 * @returns {Object} Object with formatted date and relative info
 */
export function formatFinnishDateWithRelative(date, options = {}) {
    const formatted = formatFinnishDate(date, options)
    const relative = getRelativeFinnishDate(date)

    return {
        formatted,
        relative,
        hasRelative: relative !== null,
    }
}

/**
 * Get Finnish season description for date
 * @param {string | Date} date - Date to check
 * @returns {string} Season description ("NHL-kausi", "Pudotuspelit", etc.)
 */
export function getFinnishSeason(date) {
    const dateObj = typeof date === 'string' ? new Date(`${date}T00:00:00`) : date
    const month = dateObj.getMonth() + 1 // 1-12
    const day = dateObj.getDate()

    // Regular season (October to April)
    if (
        (month === 10 && day >= 1) ||
        month === 11 ||
        month === 12 ||
        month === 1 ||
        month === 2 ||
        month === 3 ||
        (month === 4 && day <= 15)
    ) {
        return 'NHL-kausi'
    }

    // Playoffs (April to June)
    if ((month === 4 && day >= 16) || month === 5 || (month === 6 && day <= 15)) {
        return 'Pudotuspelit'
    }

    // Off-season
    return 'Kauden ulkopuolella'
}

/**
 * Validate Finnish date string
 * @param {string} dateString - Date string to validate (YYYY-MM-DD)
 * @returns {boolean} True if valid date
 */
export function isValidFinnishDateString(dateString) {
    const regex = /^\d{4}-\d{2}-\d{2}$/
    if (!regex.test(dateString)) return false

    const date = new Date(`${dateString}T00:00:00`)
    return !Number.isNaN(date.getTime())
}

/**
 * Parse Finnish date input (various formats)
 * @param {string} input - Date input from user
 * @returns {string | null} Normalized date string (YYYY-MM-DD) or null
 */
export function parseFinnishDateInput(input) {
    if (!input || typeof input !== 'string') return null

    // Try to parse as YYYY-MM-DD first
    if (isValidFinnishDateString(input)) {
        return input
    }

    // Try to parse Finnish formats
    const finnishPatterns = [
        // DD.MM.YYYY
        /^(\d{1,2})\.(\d{1,2})\.(\d{4})$/,
        // D. month YYYY
        /^(\d{1,2})\. (tammikuuta|helmikuuta|maaliskuuta|huhtikuuta|toukokuuta|kesäkuuta|heinäkuuta|elokuuta|syyskuuta|lokakuuta|marraskuuta|joulukuuta) (\d{4})$/,
    ]

    const monthMap = {
        tammikuuta: '01',
        helmikuuta: '02',
        maaliskuuta: '03',
        huhtikuuta: '04',
        toukokuuta: '05',
        kesäkuuta: '06',
        heinäkuuta: '07',
        elokuuta: '08',
        syyskuuta: '09',
        lokakuuta: '10',
        marraskuuta: '11',
        joulukuuta: '12',
    }

    // Try DD.MM.YYYY
    const match = input.match(finnishPatterns[0])
    if (match) {
        const day = match[1].padStart(2, '0')
        const month = match[2].padStart(2, '0')
        const year = match[3]
        const result = `${year}-${month}-${day}`
        if (isValidFinnishDateString(result)) return result
    }

    // Try Finnish month names
    const monthMatch = input.match(finnishPatterns[1])
    if (monthMatch) {
        const day = monthMatch[1].padStart(2, '0')
        const month = monthMap[monthMatch[2]]
        const year = monthMatch[3]
        const result = `${year}-${month}-${day}`
        if (isValidFinnishDateString(result)) return result
    }

    return null
}

/**
 * Get NHL season string in Finnish
 * @param {string | Date} date - Date within season
 * @returns {string} NHL season string (e.g., "2024-2025 kausi")
 */
export function getNHLSeasonFinnish(date) {
    const dateObj = typeof date === 'string' ? new Date(`${date}T00:00:00`) : date
    const year = dateObj.getFullYear()
    const _nextYear = year + 1

    // NHL season typically starts in October
    const month = dateObj.getMonth() + 1
    const seasonStartYear = month >= 10 ? year : year - 1
    const seasonEndYear = seasonStartYear + 1

    return `${seasonStartYear}-${seasonEndYear} kausi`
}
