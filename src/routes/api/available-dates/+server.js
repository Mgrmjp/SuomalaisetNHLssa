import { json } from '@sveltejs/kit'
import { readdir, readFile } from 'fs/promises'
import { join } from 'path'

/** @type {import('./$types').RequestHandler} */
export async function GET() {
    try {
        const gamesDir = join(process.cwd(), 'static', 'data', 'prepopulated', 'games')

        // Read all JSON files in the games directory
        const files = await readdir(gamesDir)
        const jsonFiles = files.filter((f) => f.endsWith('.json')).sort()

        const datesWithGames = []

        // Check each file for games
        for (const file of jsonFiles) {
            const filePath = join(gamesDir, file)
            const content = await readFile(filePath, 'utf-8')
            const data = JSON.parse(content)

            // Only include dates that have games
            if (data.games && data.games.length > 0) {
                // Extract date from filename (remove .json extension)
                const date = file.replace('.json', '')
                datesWithGames.push(date)
            }
        }

        return json(datesWithGames)
    } catch (error) {
        console.error('Error loading available dates:', error)
        return json([], { status: 500 })
    }
}
