import adapter from "@sveltejs/adapter-static";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      pages: "build",
      assets: "build",
      fallback: "404.html",
      precompress: false, // GitHub Pages handles compression via CDN
      strict: true,
    }),
    prerender: {
      // Explicitly generate API endpoints needed by the static site
      entries: ['*', '/api/available-dates', '/sitemap.xml'],
      // Handle missing headshots gracefully during prerender
      handleHttpError: ({ path, referrer, message }) => {
        // Ignore 404 errors for headshots during build
        if (path?.includes('/headshots/')) {
          return 'ignore';
        }
        // Fail on other errors
        return 'fail';
      }
    },
  },
};

export default config;
