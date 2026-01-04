// @ts-nocheck - This is a build configuration file, type checking is not critical
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

// Custom plugin for enhanced error reporting
const enhancedErrorReporting = () => ({
  name: 'enhanced-error-reporting',
  /** @param {import('vite').ViteDevServer} _server */
  configureServer(_server) {
    // Enhanced console error handling
    const originalError = console.error;
    console.error = (...args) => {
      if (args[0] && typeof args[0] === 'string' && args[0].includes('[vite]')) {
        originalError('\n🔥 VITE ERROR 🔥');
        originalError('═'.repeat(45));
        originalError(...args);
        originalError('═'.repeat(45));
        originalError('\n💡 Tip: Check the file path and syntax carefully');
        originalError('🔧 Fix: Save the file to trigger hot reload after fixing');
        originalError('');
      } else {
        originalError(...args);
      }
    };

    // Handle process errors
    process.on('uncaughtException', /** @param {Error} err */(err) => {
      console.error('\n💥 UNCAUGHT EXCEPTION 💥');
      console.error('═'.repeat(45));
      console.error(`Error: ${err.message}`);
      console.error(`Timestamp: ${new Date().toISOString()}`);
      if (err.stack) {
        console.error('\nStack trace:');
        console.error(err.stack);
      }
      console.error('═'.repeat(45));
    });

    process.on('unhandledRejection', /** @param {unknown} reason */ /** @param {any} promise */(reason, promise) => {
      console.error('\n🚫 UNHANDLED PROMISE REJECTION 🚫');
      console.error('═'.repeat(45));
      console.error('Promise:', promise);
      console.error('Reason:', reason);
      console.error(`Timestamp: ${new Date().toISOString()}`);
      console.error('═'.repeat(45));
    });
  }
});

export default defineConfig({
  plugins: [
    sveltekit(),
    enhancedErrorReporting(),
    {
      name: 'suppress-socket-io-errors',
      /** @param {import('vite').ViteDevServer} _server */
      configureServer(_server) {
        _server.middlewares.use((
          /** @param {import('http').IncomingMessage & {url?: string}} req */
          req,
          /** @param {import('http').ServerResponse} res */
          res,
          /** @param {Function} next */
          next
        ) => {
          if (req.url?.includes('/socket.io/')) {
            res.statusCode = 404;
            res.end();
            return;
          }
          next();
        });
      },
    },
    {
      name: 'enhanced-error-handler',
      /** @param {import('vite').ViteDevServer} _server */
      configureServer(_server) {
        _server.middlewares.use((
          /** @param {Error|null} err */
          err,
          /** @param {import('http').IncomingMessage & {url?: string, method?: string}} req */
          req,
          /** @param {import('http').ServerResponse} res */
          res,
          /** @param {Function} next */
          next
        ) => {
          if (err) {
            console.error('\n🚨 VITE SERVER ERROR 🚨');
            console.error('='.repeat(50));
            console.error(`Error: ${err.message}`);
            console.error(`URL: ${req.url}`);
            console.error(`Method: ${req.method}`);
            console.error(`Timestamp: ${new Date().toISOString()}`);
            if (err.stack) {
              console.error('\nStack trace:');
              console.error(err.stack);
            }
            console.error('='.repeat(50));

            // Enhanced error response
            res.statusCode = 500;
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify({
              error: 'Internal Server Error',
              message: err.message,
              timestamp: new Date().toISOString(),
              url: req.url
            }));
            return;
          }
          next();
        });
      },
    },
  ],
  server: {
    port: 3000,
    fs: {
      // Suppress socket.io errors from browser extensions/dev tools
      strict: false,
    },
    proxy: {
      // Proxy NHL API calls to external NHL API
      // Proxy all NHL API calls
      '/api': {
        target: 'https://api-web.nhle.com',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => {
          // Keep local endpoints as is for SvelteKit
          const localEndpoints = ['/api/finnish-players', '/api/available-dates', '/api/player-photo'];
          if (localEndpoints.some(endpoint => path.startsWith(endpoint))) {
            return path;
          }
          // Proxy everything else but remove /api prefix
          return path.replace(/^\/api/, '');
        },
        bypass: (req) => {
          // Skip proxy for local SvelteKit API routes
          const localEndpoints = ['/api/finnish-players', '/api/available-dates', '/api/player-photo'];
          if (localEndpoints.some(endpoint => req.url?.startsWith(endpoint))) {
             return req.url; // Return the URL to bypass the proxy
          }
          return null;
        },
        // @ts-ignore - Vite proxy types don't include onError but it works at runtime
        onError: (
          /** @param {Error} err */
          err,
          /** @param {import('http').IncomingMessage & {url?: string}} req */
          req,
          /** @param {import('http').ServerResponse} res */
          res
        ) => {
          console.error('\n🔄 API PROXY ERROR 🔄');
          console.error('='.repeat(40));
          console.error(`Target URL: https://api-web.nhle.com${req.url}`);
          console.error(`Error: ${err.message}`);
          console.error(`Timestamp: ${new Date().toISOString()}`);
          if (err.code) {
            console.error(`Error Code: ${err.code}`);
          }
          console.error('='.repeat(40));
        },
      }
    },
    hmr: {
      overlay: {
        // Show enhanced error overlay
        runtimeErrors: true,
        warnings: true,
      }
    }
  },
  define: {
    // Define environment variables for client-side access
    __NHL_API_BASE_URL__: JSON.stringify(process.env.NHL_API_BASE_URL || '/api'),
    __NHL_API_VERSION__: JSON.stringify(process.env.NHL_API_VERSION || 'v1'),
    __NHL_USER_AGENT__: JSON.stringify(process.env.NHL_USER_AGENT || 'Finnish-NHL-Tracker/4.0-Automatic'),
    __TEAM_LOGO_CDN_BASE_URL__: JSON.stringify(process.env.TEAM_LOGO_CDN_BASE_URL || 'https://cdn.nhl.com/images/logos/teams-current-primary-light'),
    __PLAYER_CACHE_TTL__: JSON.stringify(parseInt(process.env.PLAYER_CACHE_TTL) || 21600000),
    __API_REQUEST_TIMEOUT__: JSON.stringify(parseInt(process.env.API_REQUEST_TIMEOUT) || 10000),
    __API_MAX_RETRIES__: JSON.stringify(parseInt(process.env.API_MAX_RETRIES) || 3),
    __API_RETRY_DELAY__: JSON.stringify(parseInt(process.env.API_RETRY_DELAY) || 2000),
    __API_BATCH_SIZE__: JSON.stringify(parseInt(process.env.API_BATCH_SIZE) || 10),
    __API_DELAY_BETWEEN_CALLS__: JSON.stringify(parseInt(process.env.API_DELAY_BETWEEN_CALLS) || 500),
    __FINNISH_NATIONALITY_CODES__: JSON.stringify(process.env.FINNISH_NATIONALITY_CODES || 'FIN,FINLAND'),
    __EARLIEST_NHL_DATE__: JSON.stringify(process.env.EARLIEST_NHL_DATE || '2010-10-01'),
    __DEFAULT_SEASON_START_DATE__: JSON.stringify(process.env.DEFAULT_SEASON_START_DATE || '2025-10-01'),
    __UNIFIED_CACHE_TTL__: JSON.stringify(parseInt(process.env.UNIFIED_CACHE_TTL) || 86400000),
    __MAX_CACHE_SIZE__: JSON.stringify(parseInt(process.env.MAX_CACHE_SIZE) || 100),
    __CACHE_CLEANUP_INTERVAL__: JSON.stringify(parseInt(process.env.CACHE_CLEANUP_INTERVAL) || 1800000),
    __PERFORMANCE_COLLECTION_INTERVAL__: JSON.stringify(parseInt(process.env.PERFORMANCE_COLLECTION_INTERVAL) || 60000),
    __PERFORMANCE_SLOW_RESPONSE_THRESHOLD__: JSON.stringify(parseInt(process.env.PERFORMANCE_SLOW_RESPONSE_THRESHOLD) || 3000),
  },
  resolve: {
    alias: {
      '@data': '/data'
    }
  },
  css: {
    postcss: './postcss.config.js',
  },
  clearScreen: false,
  build: {
    // Optimize build
    minify: "terser",
    sourcemap: true,
    // Enable CSS code splitting
    cssCodeSplit: true,
    // Optimize assets
    assetsInlineLimit: 4096,
    // Chunk size warning limit
    chunkSizeWarningLimit: 1000,
    // Enhanced build reporting
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress some warnings but enhance others
        if (warning.code === 'MODULE_LEVEL_DIRECTIVE') {
          return;
        }
        if (warning.code === 'THIS_IS_UNDEFINED') {
          return;
        }

        // Enhance warning display
        console.warn('\n⚠️  ROLLUP WARNING ⚠️');
        console.warn('─'.repeat(40));
        console.warn(`Code: ${warning.code}`);
        console.warn(`Message: ${warning.message}`);
        if (warning.loc) {
          console.warn(`Location: ${warning.loc.file}:${warning.loc.line}:${warning.loc.column}`);
        }
        if (warning.frame) {
          console.warn('\nCode context:');
          console.warn(warning.frame);
        }
        console.warn('─'.repeat(40));

        // Call original warn
        warn(warning);
      },
    },
  },
  preview: {
    port: 4173,
  },
  optimizeDeps: {
    // Let the SvelteKit plugin handle framework deps to avoid bundling the server runtime in the browser
    exclude: ["svelte", "@sveltejs/kit"],
  },
  ssr: {
    noExternal: ['flowbite-svelte']
  }
});
