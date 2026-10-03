// Temporary public section switch. Re-enable to restore navigation, routes and sitemap entries.
export const PROSPECTS_ENABLED = false

/** @param {string} pathname Path without the app base prefix. */
export function isProspectsPath(pathname) {
    return ['lupaukset', 'prospects', 'drafts', 'scouting'].includes(pathname.split('/')[1] || '')
}
