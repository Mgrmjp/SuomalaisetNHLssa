import { describe, expect, it } from 'vitest'
import { renderSafeMarkdown } from '$lib/utils/safeMarkdown.js'

describe('renderSafeMarkdown', () => {
    it('escapes raw HTML instead of rendering it', () => {
        const html = renderSafeMarkdown('Hello <img src=x onerror=alert(1)>')

        expect(html).toContain('&lt;img src=x onerror=alert(1)&gt;')
        expect(html).not.toContain('<img src=x')
    })

    it('drops unsafe link protocols while preserving link text', () => {
        const html = renderSafeMarkdown('[read more](javascript:alert(1))')

        expect(html).toContain('<p>read more</p>')
        expect(html).not.toContain('javascript:')
        expect(html).not.toContain('<a ')
    })

    it('keeps safe links and escapes link attributes', () => {
        const html = renderSafeMarkdown('[NHL](https://www.nhl.com "Official & current")')

        expect(html).toContain(
            '<a href="https://www.nhl.com" title="Official &amp; current">NHL</a>'
        )
    })

    it('renders GitHub-flavored Markdown tables', () => {
        const html = renderSafeMarkdown('| Player | Points |\n|---|---:|\n| Aho | 80 |')

        expect(html).toContain('<table>')
        expect(html).toContain('<td align="right">80</td>')
    })
})
