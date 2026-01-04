import adapter from "@sveltejs/adapter-static";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      pages: "build",
      assets: "build",
      fallback: "404.html",
      precompress: false,
      strict: true,
    }),
    prerender: {
      // Explicitly generate API endpoints needed by the static site
      entries: ['*', '/api/available-dates'],
    },
  },
};

export default config;
