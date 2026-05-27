import { Marked, Renderer } from 'marked'

const LINK_PROTOCOLS = new Set(['http:', 'https:', 'mailto:'])
const IMAGE_PROTOCOLS = new Set(['https:'])

/** @type {Record<string, string>} */
const HTML_ESCAPE_REPLACEMENTS = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
}

/**
 * @param {unknown} value
 * @returns {string}
 */
export function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (char) => {
        return HTML_ESCAPE_REPLACEMENTS[char] ?? char
    })
}

/**
 * @param {string} url
 * @param {{ protocols: Set<string>, allowRelative?: boolean }} options
 * @returns {string | null}
 */
function getSafeUrl(url, { protocols, allowRelative = true }) {
    if (!url || typeof url !== 'string') return null

    const trimmed = url.trim()
    if (!trimmed || trimmed.startsWith('//')) return null

    const normalized = Array.from(trimmed)
        .filter((char) => {
            const codePoint = char.charCodeAt(0)
            return codePoint > 0x20 && codePoint !== 0x7f
        })
        .join('')
    const schemeMatch = normalized.match(/^([a-zA-Z][a-zA-Z\d+.-]*):/)

    if (schemeMatch) {
        try {
            const parsed = new URL(normalized)
            return protocols.has(parsed.protocol) ? normalized : null
        } catch {
            return null
        }
    }

    return allowRelative ? normalized : null
}

const renderer = new Renderer()

/** @param {import('marked').Tokens.HTML | import('marked').Tokens.Tag} token */
renderer.html = (token) => escapeHtml(token.text)

/** @param {import('marked').Tokens.Link} token */
renderer.link = function (token) {
    const { href, title, tokens } = token
    const label = this.parser.parseInline(tokens)
    const safeHref = getSafeUrl(href, { protocols: LINK_PROTOCOLS })

    if (!safeHref) return label

    const titleAttribute = title ? ` title="${escapeHtml(title)}"` : ''
    return `<a href="${escapeHtml(safeHref)}"${titleAttribute}>${label}</a>`
}

/** @param {import('marked').Tokens.Image} token */
renderer.image = (token) => {
    const { href, title, text } = token
    const safeHref = getSafeUrl(href, { protocols: IMAGE_PROTOCOLS, allowRelative: false })

    if (!safeHref) return escapeHtml(text)

    const titleAttribute = title ? ` title="${escapeHtml(title)}"` : ''
    return `<img src="${escapeHtml(safeHref)}" alt="${escapeHtml(text)}"${titleAttribute}>`
}

const safeMarkdown = new Marked({
    gfm: true,
    renderer,
})

/**
 * Render Markdown to HTML while blocking raw HTML and unsafe URL protocols.
 *
 * @param {unknown} markdown
 * @returns {string}
 */
export function renderSafeMarkdown(markdown) {
    const html = safeMarkdown.parse(String(markdown ?? ''))
    if (typeof html !== 'string') {
        throw new TypeError('Expected synchronous Markdown rendering')
    }

    return html
}
