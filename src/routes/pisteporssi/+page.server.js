import { json } from '@sveltejs/kit';
import { readFileSync } from 'fs';
import { join } from 'path';

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch }) {
    try {
        // Calculate current season ID dynamically
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth();

        const startYear = currentMonth < 9 ? currentYear - 1 : currentYear;
        const endYear = startYear + 1;
        const seasonId = `${startYear}${endYear}`;

        // Try to load from pre-built JSON files first
        const prebuiltDir = join(process.cwd(), 'static/data/player-stats');
        const skatersFile = join(prebuiltDir, `skaters-${seasonId}.json`);

        try {
            const fileData = readFileSync(skatersFile, 'utf-8');
            const players = JSON.parse(fileData);

            return {
                players,
                seasonId,
                updatedAt: new Date().toISOString(),
                source: 'prebuilt'
            };
        } catch (fileError) {
            // Fallback to API if pre-built file doesn't exist
            console.warn('Pre-built data not found, fetching from NHL API...');

            const apiUrl = `https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D%5D&start=0&limit=100&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`;

            const response = await fetch(apiUrl);

            if (!response.ok) {
                throw new Error(`Failed to fetch stats: ${response.status}`);
            }

            const data = await response.json();

            return {
                players: data.data || [],
                seasonId,
                updatedAt: new Date().toISOString(),
                source: 'api'
            };
        }

    } catch (error) {
        console.error('Error fetching leaderboard data:', error);
        return {
            players: [],
            error: 'Tilastojen lataus epäonnistui'
        };
    }
}
