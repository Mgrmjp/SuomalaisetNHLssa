import { json } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch }) {
    try {
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth();
        
        // Similar logic to pisteporsi for season determination
        const startYear = currentMonth < 9 ? currentYear - 1 : currentYear;
        const endYear = startYear + 1;
        const seasonId = `${startYear}${endYear}`;
        
        // Fetch all Finnish skaters
        // limit=500 to cover everyone
        // sort by name
        const skaterUrl = `https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22skaterFullName%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=500&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`;

        // Fetch all Finnish goalies
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
            updatedAt: new Date().toISOString()
        };

    } catch (error) {
        console.error('Error fetching player data:', error);
        return {
            skaters: [],
            goalies: [],
            error: 'Pelaajaliistan lataus epäonnistui'
        };
    }
}
