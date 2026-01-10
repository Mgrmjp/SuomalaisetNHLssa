import { error } from '@sveltejs/kit';
import { correctFullName } from '$lib/utils/finnishNameUtils.js';

/**
 * List of Finnish Stanley Cup winners (Player IDs).
 * This is the only hardcoded part. All data (Name, Team, Year, Win Count) is fetched from API.
 */
const winnerIds = [
    8448569, // Jari Kurri
    8451905, // Esa Tikkanen
    8451056, // Reijo Ruotsalainen
    8476874, // Olli Määttä
    8459024, // Jere Lehtinen
    8466210, // Ville Nieminen
    8457981, // Teemu Selänne
    8470047, // Valtteri Filppula
    8474550, // Antti Niemi
    8471695, // Tuukka Rask
    8459670, // Kimmo Timonen
    8476882, // Teuvo Teräväinen
    8477476, // Artturi Lehkonen
    8478420, // Mikko Rantanen
    8477493, // Aleksander Barkov
    8482113, // Anton Lundell
    8480185, // Eetu Luostarinen
    8478859, // Niko Mikkola
];

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch }) {
    
    /**
     * @param {number} id
     */
    async function fetchWinnerData(id) {
        try {
            const res = await fetch(`https://api-web.nhle.com/v1/player/${id}/landing`);
            if (!res.ok) {
                console.error(`Failed to fetch player ${id}`);
                return null;
            }
            const data = await res.json();
            
            // 1. Get Name with Finnish letter correction
            const rawName = `${data.firstName?.default || ''} ${data.lastName?.default || ''}`.trim();
            const name = correctFullName(rawName);

            // 2. Find Stanley Cup Award
            const cupAward = data.awards?.find(
                (/** @type {{ trophy: { default: string; }; }} */ a) => a.trophy?.default === 'Stanley Cup'
            );

            if (!cupAward) {
                // Should not happen for this list, but handle gracefully
                console.warn(`No Stanley Cup found for ${name} (${id})`);
                return null;
            }

            const wins = cupAward.seasons.length;

            // 3. Map Seasons to Teams
            const years = cupAward.seasons.map((/** @type {{ seasonId: number; gameTypeId: number; }} */ seasonInfo) => {
                const seasonId = seasonInfo.seasonId;
                
                // Find matching season in seasonTotals
                // We need to match seasonId AND gameTypeId (3 for playoffs)
                // Note: seasonTotals uses 'season' key (e.g. 19891990)
                const playOffStats = data.seasonTotals?.find(
                    (/** @type {{ season: number; gameTypeId: number; leagueAbbrev: string; }} */ s) => 
                        s.season === seasonId && 
                        s.gameTypeId === 3 && // Playoffs
                        s.leagueAbbrev === 'NHL'
                );

                // Use team from stats, fallback to common name if not found (unlikely)
                // stats API usually provides teamName.default
                let teamName = "Unknown Team";
                if (playOffStats && playOffStats.teamName?.default) {
                    teamName = playOffStats.teamName.default;
                } else if (playOffStats && playOffStats.teamCommonName?.default) {
                    teamName = playOffStats.teamCommonName.default;
                }

                // Format year as the ending year (e.g. 19891990 -> 1990)
                const winYear = Math.floor(seasonId % 10000);

                return {
                    year: winYear,
                    team: teamName
                };
            });

            // Sort years ascending
            years.sort((a, b) => a.year - b.year);

            return {
                id,
                name,
                wins,
                years,
                validation: { verified: true, hasCup: true } // Implicitly true since we found it
            };

        } catch (e) {
            console.error(`Error processing player ${id}:`, e);
            return null;
        }
    }

    // Parallel fetch
    const results = await Promise.all(winnerIds.map(fetchWinnerData));

    // Filter out potential failures
    const winners = results.filter(w => w !== null);

    // Sort by wins (desc), then by first win year (asc)
    winners.sort((a, b) => {
        if (b.wins !== a.wins) return b.wins - a.wins;
        // Safety check if years array is empty
        const yearA = a.years[0]?.year || 0;
        const yearB = b.years[0]?.year || 0;
        return yearA - yearB;
    });

    return {
        winners,
        lastUpdated: new Date().toISOString()
    };
}
