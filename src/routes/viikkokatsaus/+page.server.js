import { base } from '$app/paths';

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch }) {
    const response = await fetch(`${base}/data/articles.json`);
    const articles = await response.json();
    
    // Sort by date, newest first
    articles.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    
    return {
        articles
    };
}
