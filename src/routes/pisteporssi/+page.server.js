import { json } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch }) {
    try {
        // Calculate current season ID dynamically
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth(); // 0-11
        
        // NHL season usually starts in October (month 9)
        // If we are in Jan-Aug, the season started in previous year
        // If we are in Oct-Dec, the season started in current year
        // Sept is tricky, usually preseason, but let's assume if month < 9, use previous year start
        
        const startYear = currentMonth < 9 ? currentYear - 1 : currentYear;
        const endYear = startYear + 1;
        const seasonId = `${startYear}${endYear}`;
        
        // Construct the API URL
        // gameTypeId=2 for Regular Season
        // limit=100 to get top 100 Finnish players
        const apiUrl = `https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D%5D&start=0&limit=100&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`;

        const response = await fetch(apiUrl);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch stats: ${response.status}`);
        }

        const data = await response.json();
        
        return {
            players: data.data || [],
            seasonId,
            updatedAt: new Date().toISOString()
        };

    } catch (error) {
        console.error('Error fetching leaderboard data:', error);
        return {
            players: [],
            error: 'Tilastojen lataus epäonnistui'
        };
    }
}
