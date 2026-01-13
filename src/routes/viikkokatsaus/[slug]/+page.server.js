import { base } from '$app/paths';
import { error } from '@sveltejs/kit';
import { marked } from 'marked';

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch, params }) {
    const response = await fetch(`${base}/data/articles.json`);
    const articles = await response.json();

    // Sort by date for navigation
    articles.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

    const currentIndex = articles.findIndex(a => a.slug === params.slug);

    if (currentIndex === -1) {
        throw error(404, 'Artikkelia ei löytynyt');
    }

    const article = articles[currentIndex];
    const prevArticle = currentIndex < articles.length - 1 ? articles[currentIndex + 1] : null;
    const nextArticle = currentIndex > 0 ? articles[currentIndex - 1] : null;

    // Convert markdown content to HTML
    const articleWithHtml = {
        ...article,
        content: marked.parse(article.content)
    };

    return {
        article: articleWithHtml,
        prevArticle,
        nextArticle
    };
}

/** @type {import('./$types').EntryGenerator} */
export async function entries() {
    // This runs at build time to generate all article pages
    const articles = await import('../../../../static/data/articles.json', { with: { type: 'json' } });
    return articles.default.map(article => ({ slug: article.slug }));
}

export const prerender = true;
