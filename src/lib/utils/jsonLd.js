/** @type {Record<string, string>} */
const JSON_SCRIPT_REPLACEMENTS = {
    '<': '\\u003c',
    '>': '\\u003e',
    '&': '\\u0026',
    '\u2028': '\\u2028',
    '\u2029': '\\u2029',
}

/**
 * Serialize data for a JSON-LD script tag without allowing `</script>` breakouts.
 *
 * @param {unknown} data
 * @returns {string}
 */
export function jsonLdScript(data) {
    const json = (JSON.stringify(data) ?? 'null').replace(/[<>&\u2028\u2029]/g, (char) => {
        return JSON_SCRIPT_REPLACEMENTS[char] ?? char
    })

    return `<script type="application/ld+json">${json}</script>`
}
