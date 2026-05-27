import { describe, expect, it } from 'vitest'
import { jsonLdScript } from '$lib/utils/jsonLd.js'

describe('jsonLdScript', () => {
    it('escapes script-breaking characters inside JSON-LD', () => {
        const script = jsonLdScript({
            headline: '</script><script>alert(1)</script>',
        })

        expect(script).toContain('<script type="application/ld+json">')
        expect(script).toContain('\\u003c/script\\u003e')
        expect(script).not.toContain('</script><script>')
    })
})
