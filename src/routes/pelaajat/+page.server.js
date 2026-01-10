import { json } from '@sveltejs/kit';
import { readFileSync } from 'fs';
import { join } from 'path';

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch }) {
    try {
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth();

        const startYear = currentMonth < 9 ? currentYear - 1 : currentYear;
        const endYear = startYear + 1;
        const seasonId = `${startYear}${endYear}`;

        // Try to load from pre-built JSON files first
        const prebuiltDir = join(process.cwd(), 'static/data/player-stats');
        const skatersFile = join(prebuiltDir, `skaters-${seasonId}.json`);
        const goaliesFile = join(prebuiltDir, `goalies-${seasonId}.json`);

        try {
            const skatersData = JSON.parse(readFileSync(skatersFile, 'utf-8'));
            const goaliesData = JSON.parse(readFileSync(goaliesFile, 'utf-8'));

            return {
                skaters: skatersData,
                goalies: goaliesData,
                seasonId,
                updatedAt: new Date().toISOString(),
                source: 'prebuilt'
            };
        } catch (fileError) {
            // Fallback to API if pre-built files don't exist
            console.warn('Pre-built data not found, fetching from NHL API...');

            const skaterUrl = `https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22skaterFullName%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=500&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`;
            const goalieUrl = `https://api.nhle.com/stats/rest/en/goalie/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22goalieFullName%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=100&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`;

            const [skaterRes, goalieRes] = await Promise.all([
                fetch(skaterUrl),
                fetch(goalieUrl)
            ]);

            if (!skaterRes.ok || !goalieRes.ok) {
                throw new Error(`Failed to fetch stats`);
            }

            const skatersData = await skaterRes.json();
            const goaliesData = await goalieRes.json();

            return {
                skaters: skatersData.data || [],
                goalies: goaliesData.data || [],
                seasonId,
                updatedAt: new Date().toISOString(),
                source: 'api'
            };
        }

    } catch (error) {
        console.error('Error fetching player data:', error);
        return {
            skaters: [],
            goalies: [],
            error: 'Pelaajaliistan lataus epäonnistui'
        };
    }
}
