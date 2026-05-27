import fs from 'node:fs/promises'
import path from 'node:path'
import { error } from '@sveltejs/kit'
import { renderSafeMarkdown } from '$lib/utils/safeMarkdown.js'

export const prerender = true

const SCOUTING_DIR = path.resolve('content/scouting')
const SLUG_PATTERN = /^[a-z0-9-]{1,100}$/i

/** @param {string} slug */
function getContentPath(slug) {
    if (!SLUG_PATTERN.test(slug)) {
        throw error(404, 'Scouting report not found')
    }

    const contentPath = path.resolve(SCOUTING_DIR, `${slug}.md`)
    const relativePath = path.relative(SCOUTING_DIR, contentPath)

    if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
        throw error(404, 'Scouting report not found')
    }

    return contentPath
}

/** @param {string} content @param {string} label */
function extractField(content, label) {
    const match = content.match(new RegExp(`\\*\\*${label}:\\*\\*\\s*([^\\n]+)`))
    return match?.[1]?.trim() || ''
}

/** @param {string} content */
function extractRanking(content) {
    const section = content.match(/## NHL Central Scouting Ranking\s+([\s\S]*?)(?:\n##|\n---|$)/)
    return section?.[1]?.match(/\*\*([^*]+)\*\*/)?.[1]?.trim() || ''
}

/** @param {string} content */
function extractUpdated(content) {
    const match = content.match(/\*Raportti päivitetty:\s*([^*]+)\*/)
    return match?.[1]?.trim() || ''
}

/** @param {string} content @param {string} slug */
function buildMetadata(content, slug) {
    const title = content.match(/^#\s+(.+)$/m)?.[1]?.trim() || 'Scouting Report'
    const playerName = title.replace(/\s+-\s+Scouting Report$/i, '')
    const club = extractField(content, 'Seura')
    const position = extractField(content, 'Pelipaikka')
    const ranking = extractRanking(content)
    const updated = extractUpdated(content)
    const details = [club, position, ranking ? `NHL Central Scouting: ${ranking}` : '']
        .filter(Boolean)
        .join(', ')

    return {
        title,
        playerName,
        pageTitle: `${playerName} scouting report | Suomalaiset NHL:ssä`,
        description: `${playerName} scouting report. ${details}. Vahvuudet, kehityskohteet ja NHL-potentiaali suomalaiselle NHL-lupaukselle.`,
        updated,
        url: `https://suomalaisetnhlssa.fi/scouting/${slug}`,
    }
}

export async function load({ params }) {
    const { slug } = params

    const contentPath = getContentPath(slug)

    try {
        const content = await fs.readFile(contentPath, 'utf-8')
        const html = renderSafeMarkdown(content)

        return {
            slug,
            content: html,
            metadata: buildMetadata(content, slug),
        }
    } catch (_err) {
        throw error(404, 'Scouting report not found')
    }
}

export async function entries() {
    try {
        const files = await fs.readdir(SCOUTING_DIR)
        const mdFiles = files.filter((f) => f.endsWith('.md') && f !== 'index.md')

        return mdFiles.map((file) => ({
            slug: file.replace('.md', ''),
        }))
    } catch {
        return []
    }
}
