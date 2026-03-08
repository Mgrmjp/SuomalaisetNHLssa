import { error } from '@sveltejs/kit'
import fs from 'fs/promises'
import path from 'path'
import { marked } from 'marked'

export async function load({ params }) {
    const { slug } = params
    
    const contentPath = path.resolve('content/scouting', `${slug}.md`)
    
    try {
        const content = await fs.readFile(contentPath, 'utf-8')
        const html = marked.parse(content)
        
        return {
            slug,
            content: html,
        }
    } catch (err) {
        throw error(404, 'Scouting report not found')
    }
}

export async function entries() {
    const scoutingDir = path.resolve('content/scouting')
    
    try {
        const files = await fs.readdir(scoutingDir)
        const mdFiles = files.filter(f => f.endsWith('.md') && f !== 'index.md')
        
        return mdFiles.map(file => ({
            slug: file.replace('.md', '')
        }))
    } catch {
        return []
    }
}
