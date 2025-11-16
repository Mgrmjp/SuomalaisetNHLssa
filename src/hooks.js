// Handle the form prop warning for static adapter
export function handle({ event, resolve }) {
    return resolve(event, {
        transformPageChunk: ({ html }) => html.replace('%sveltekit.form%', 'null'),
    })
}
