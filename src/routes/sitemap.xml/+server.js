export const prerender = true;

const siteUrl = 'https://suomalaisetnhlssa.fi';

const pages = [
  { path: '/', priority: '1.0', changefreq: 'daily' },
  { path: '/pisteporssi', priority: '0.9', changefreq: 'daily' },
  { path: '/sarjataulukko', priority: '0.8', changefreq: 'daily' },
  { path: '/tietoa', priority: '0.5', changefreq: 'monthly' },
];

/** @type {import('./$types').RequestHandler} */
export async function GET() {
  const today = new Date().toISOString().split('T')[0];

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map(page => `  <url>
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
