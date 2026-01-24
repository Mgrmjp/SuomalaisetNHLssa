import { readFileSync } from 'fs';
import { join } from 'path';

export const prerender = false;

const siteUrl = 'https://suomalaisetnhlssa.fi';

const staticPages = [
  { path: '/', priority: '1.0', changefreq: 'daily' },
  { path: '/pisteporssi', priority: '0.9', changefreq: 'daily' },
  { path: '/pelaajat', priority: '0.9', changefreq: 'daily' },
  { path: '/joukkueet', priority: '0.8', changefreq: 'daily' },
  { path: '/viikkokatsaus', priority: '0.8', changefreq: 'weekly' },
  { path: '/mestaruudet', priority: '0.8', changefreq: 'monthly' },
  { path: '/sarjataulukko', priority: '0.8', changefreq: 'daily' },
  { path: '/tietoa', priority: '0.5', changefreq: 'monthly' },
];

// Simple Finnish name correction (subset of correctFullName utility)
function correctFullName(name) {
    const corrections = {
        'Jesse Puljujarvi': 'Jesse Puljujärvi',
        'Mikko Koskinen': 'Mikko Koskinen',
        // Add more as needed - this is a minimal set for sitemap
    };
    return corrections[name] || name;
}

function nameToSlug(name) {
    return name.toLowerCase()
        .replace(/ä/g, 'a')
        .replace(/ö/g, 'o')
        .replace(/å/g, 'o')
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '');
}

function getPlayerRoutes() {
  try {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth();
    const startYear = currentMonth < 9 ? currentYear - 1 : currentYear;
    const endYear = startYear + 1;
    const seasonId = `${startYear}${endYear}`;

    const prebuiltDir = join(process.cwd(), 'static/data/player-stats');
    const skatersFile = join(prebuiltDir, `skaters-${seasonId}.json`);
    const goaliesFile = join(prebuiltDir, `goalies-${seasonId}.json`);

    const skatersData = JSON.parse(readFileSync(skatersFile, 'utf-8'));
    const goaliesData = JSON.parse(readFileSync(goaliesFile, 'utf-8'));

    const allPlayers = [...skatersData, ...goaliesData];

    return allPlayers.map(player => {
      const playerName = player.skaterFullName || player.goalieFullName;
      const correctedName = correctFullName(playerName);
      const slug = nameToSlug(correctedName);

      return {
        path: `/pelaajat/${slug}`,
        priority: '0.7',
        changefreq: 'daily'
      };
    });
  } catch (error) {
    console.warn('Could not load player data for sitemap:', error);
    return [];
  }
}

/** @type {import('./$types').RequestHandler} */
export async function GET() {
  const today = new Date().toISOString().split('T')[0];
  const playerRoutes = getPlayerRoutes();
  const allPages = [...staticPages, ...playerRoutes];

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allPages.map(page => `  <url>
    <loc>${siteUrl}${page.path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join('\n')}
</urlset>`;

  return new Response(sitemap, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'max-age=3600'
    }
  });
}
