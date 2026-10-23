/**
 * Finnish numeral agreement for counted nouns.
 *
 * In Finnish the head noun is nominative singular when the count is exactly 1
 * ("1 maali") and partitive singular for every other count ("0 maalia",
 * "2 maalia", "21 maalia"). Only the bare numeral 1 triggers the nominative;
 * compound numerals that merely end in 1 still take the partitive.
 */

/**
 * Pick the correct form of a noun for a count.
 * @param {number} count
 * @param {string} nominative - nominative singular, e.g. "maali"
 * @param {string} partitive - partitive singular, e.g. "maalia"
 * @returns {string}
 */
export function fiNoun(count, nominative, partitive) {
    return Number(count) === 1 ? nominative : partitive
}

/**
 * A count and its correctly inflected noun, e.g. "1 maali" / "3 maalia".
 * @param {number} count
 * @param {string} nominative
 * @param {string} partitive
 * @returns {string}
 */
export function fiCount(count, nominative, partitive) {
    const value = Number(count) || 0
    return `${value} ${fiNoun(value, nominative, partitive)}`
}

/** @param {number} count */
export function fiGoals(count) {
    return fiCount(count, 'maali', 'maalia')
}

/** @param {number} count */
export function fiAssists(count) {
    return fiCount(count, 'syöttö', 'syöttöä')
}

/** @param {number} count */
export function fiPoints(count) {
    return fiCount(count, 'piste', 'pistettä')
}

/** @param {number} count */
export function fiGames(count) {
    return fiCount(count, 'ottelu', 'ottelua')
}
