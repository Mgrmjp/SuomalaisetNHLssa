# Deployment Guide

This guide covers deployment strategies, configurations, and best practices for the Finnish NHL Player Tracker application.

## Overview

The Finnish NHL Player Tracker is built as a **static site** using SvelteKit with the static adapter. This makes it ideal for deployment to various hosting platforms that support static site hosting.

## Supported Deployment Platforms

### Recommended Platforms

1. **Vercel** (Recommended)
   - Zero-config deployment
   - Automatic HTTPS
   - Built-in CDN
   - Preview deployments for PRs

2. **Netlify**
   - Git-based deployment
   - Form handling
   - Edge functions support
   - Split testing

3. **Cloudflare Pages**
   - Global CDN
   - Built-in analytics
   - D1 database support
   - WebAssembly support

4. **GitHub Pages**
   - Free hosting
   - GitHub integration
   - Custom domain support
   - Automatic HTTPS

### Alternative Platforms

- **AWS S3 + CloudFront**
- **Firebase Hosting**
- **Surge.sh**
- **Any static file hosting service**

## Pre-Deployment Checklist

### Code Quality

```bash
# Run all quality checks
npm run lint
npm run check
npm test
```

### Build Verification

```bash
# Build for production
npm run build

# Preview the build
npm run preview

# Check build output
ls -la build/
```

### Environment Configuration

```bash
# Verify environment variables
cat .env.production

# Test with production config
npm run build
```

### Performance Optimization

```bash
# Analyze bundle size
npm run build
npx vite-bundle-analyzer build/

# Check Lighthouse scores (optional)
npm run build
npm run preview
# Run Lighthouse on localhost:4173
```

## Platform-Specific Deployments

### 1. Vercel Deployment

#### Automatic Deployment

1. **Connect Repository**
   ```bash
   # Install Vercel CLI
   npm i -g vercel

   # Login to Vercel
   vercel login

   # Deploy from project root
   vercel
   ```

2. **Configuration Files**
   ```json
   // vercel.json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "build",
     "installCommand": "npm install",
     "framework": "sveltekit"
   }
   ```

3. **Environment Variables**
   ```bash
   # Set via Vercel dashboard or CLI
   vercel env add NHL_API_BASE_URL production
   vercel env add CACHE_TTL production
   ```

#### Manual Deployment

```bash
# Build and deploy
npm run build
vercel --prod
```

#### Domain Configuration

```bash
# Add custom domain
vercel domains add yourdomain.com
```

### 2. Netlify Deployment

#### Build Configuration

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

#### Deployment via Git

1. **Connect Repository**
   - Connect GitHub/GitLab repository to Netlify
   - Configure build settings

2. **Environment Variables**
   ```
   NHL_API_BASE_URL = https://api-web.nhle.com
   CACHE_TTL = 300000
   NODE_ENV = production
   ```

#### Manual Deployment

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
npm run build
netlify deploy --prod --dir=build
```

### 3. Cloudflare Pages Deployment

#### Configuration

```toml
# wrangler.toml (for Cloudflare Pages)
name = "finnish-nhl-tracker"
compatibility_date = "2024-01-01"

[env.production]
vars = { NODE_ENV = "production" }
```

#### Deployment via Dashboard

1. **Connect Repository**
   - Add repository to Cloudflare Pages
   - Configure build settings

2. **Build Settings**
   ```
   Build command: npm run build
   Build output directory: build
   Node.js version: 18
   ```

#### Manual Deployment

```bash
# Install Wrangler
npm install -g wrangler

# Deploy
npm run build
wrangler pages publish build
```

### 4. GitHub Pages Deployment

#### Configuration

```javascript
// vite.config.js
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  base: process.env.NODE_ENV === 'production'
    ? '/finnish-nhl-tracker/'
    : '/',
  build: {
    outDir: 'build',
    assetsDir: 'assets'
  }
});
```

#### SvelteKit Configuration

```javascript
// svelte.config.js
import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: null,
      precompress: false,
      strict: true
    }),
    paths: {
      base: process.env.NODE_ENV === 'production'
        ? '/finnish-nhl-tracker'
        : ''
    }
  }
};

export default config;
```

#### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test

    - name: Build
      run: npm run build

    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./build
```

## Environment Configuration

### Production Environment Variables

Create `.env.production` in project root:

```env
# NHL API Configuration
NHL_API_BASE_URL=https://api-web.nhle.com
CACHE_TTL=300000

# Feature Flags
ENABLE_REAL_API=true
ENABLE_CACHE_MONITORING=false

# Analytics (optional)
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX

# Performance Monitoring (optional)
SENTRY_DSN=https://your-sentry-dsn
```

### Runtime Configuration

```typescript
// src/lib/config/runtime.js
export const config = {
  api: {
    baseUrl: import.meta.env.VITE_NHL_API_BASE_URL || 'https://api-web.nhle.com',
    timeout: 10000
  },
  cache: {
    ttl: parseInt(import.meta.env.VITE_CACHE_TTL) || 300000
  },
  features: {
    realApi: import.meta.env.VITE_ENABLE_REAL_API === 'true',
    cacheMonitoring: import.meta.env.VITE_ENABLE_CACHE_MONITORING === 'true'
  },
  analytics: {
    googleAnalyticsId: import.meta.env.VITE_GOOGLE_ANALYTICS_ID
  }
};
```

## Build Optimization

### Bundle Analysis

```bash
# Analyze bundle size
npm run build
npx vite-bundle-analyzer build/

# Check for large dependencies
npm ls --depth=0
```

### Asset Optimization

```javascript
// vite.config.js
export default defineConfig({
  build: {
    minify: 'terser',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['svelte'],
          ui: ['tailwindcss']
        }
      }
    }
  },
  optimizeDeps: {
    exclude: ['@sveltejs/kit']
  }
});
```

### Compression

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  build: {
    rollupOptions: {
      output: {
        // Compress assets
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `images/[name]-[hash][extname]`;
          }
          return `${ext}/[name]-[hash][extname]`;
        }
      }
    }
  }
});
```

## Performance Monitoring

### Web Vitals

```typescript
// src/lib/utils/webVitals.js
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to analytics service
  if (typeof gtag !== 'undefined') {
    gtag('event', metric.name, {
      event_category: 'Web Vitals',
      event_label: metric.id,
      value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
      non_interaction: true
    });
  }
}

export function initWebVitals() {
  getCLS(sendToAnalytics);
  getFID(sendToAnalytics);
  getFCP(sendToAnalytics);
  getLCP(sendToAnalytics);
  getTTFB(sendToAnalytics);
}
```

### Error Tracking

```typescript
// src/lib/utils/errorTracking.js
export function initErrorTracking() {
  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    // Send to error tracking service
  });

  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    // Send to error tracking service
  });
}
```

## Security Considerations

### Content Security Policy

```html
<!-- src/app.html -->
<head>
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'self';
                script-src 'self' 'unsafe-inline' https://www.googletagmanager.com;
                style-src 'self' 'unsafe-inline';
                img-src 'self' data: https:;
                font-src 'self' data:;
                connect-src 'self' https://api-web.nhle.com;">
</head>
```

### Security Headers

```javascript
// hooks.server.js (if using server-side features)
export function handle({ event, resolve }) {
  const response = await resolve(event);

  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');

  return response;
}
```

## Caching Strategy

### Browser Caching

```javascript
// build configuration for cache headers
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        // Hash filenames for cache busting
        entryFileNames: '[name]-[hash].js',
        chunkFileNames: '[name]-[hash].js',
        assetFileNames: '[name]-[hash].[ext]'
      }
    }
  }
});
```

### CDN Configuration

```yaml
# Netlify _headers file (for CDN caching)
/*
  Cache-Control: public, max-age=31536000, immutable

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*.html
  Cache-Control: public, max-age=0, must-revalidate

/api/*
  Cache-Control: public, max-age=300, s-maxage=600
```

## Monitoring and Analytics

### Google Analytics Setup

```typescript
// src/lib/components/Analytics.svelte
<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';

  onMount(() => {
    if (browser && import.meta.env.VITE_GOOGLE_ANALYTICS_ID) {
      // Load Google Analytics
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${import.meta.env.VITE_GOOGLE_ANALYTICS_ID}`;
      document.head.appendChild(script);

      // Initialize gtag
      window.dataLayer = window.dataLayer || [];
      window.gtag = function() {
        window.dataLayer.push(arguments);
      };
      gtag('js', new Date());
      gtag('config', import.meta.env.VITE_GOOGLE_ANALYTICS_ID);
    }
  });
</script>
```

### Custom Analytics

```typescript
// src/lib/utils/analytics.js
export class Analytics {
  static track(event, properties = {}) {
    // Send to analytics service
    console.log('Analytics event:', event, properties);
  }

  static pageView(path) {
    this.track('page_view', { path });
  }

  static trackUserAction(action, details = {}) {
    this.track('user_action', { action, ...details });
  }
}
```

## Deployment Checklist

### Pre-Deployment

- [ ] All tests pass: `npm test`
- [ ] Code quality checks pass: `npm run lint && npm run check`
- [ ] Build succeeds: `npm run build`
- [ ] Environment variables configured
- [ ] Bundle size analyzed and optimized
- [ ] Performance budgets met
- [ ] Security headers configured
- [ ] Analytics configured (if needed)

### Post-Deployment

- [ ] Site loads correctly
- [ ] All pages work (404 checks)
- [ ] Forms function properly
- [ ] API integrations work
- [ ] Cache system functions
- [ ] Analytics tracking works
- [ ] Performance metrics acceptable
- [ ] Mobile responsiveness verified
- [ ] Accessibility verified

### Monitoring Setup

- [ ] Error tracking configured
- [ ] Performance monitoring active
- [ ] Uptime monitoring set up
- [ ] Analytics dashboard configured
- [ ] Security monitoring enabled

## Troubleshooting

### Common Deployment Issues

#### Build Failures

```bash
# Clear all caches
rm -rf build/ .svelte-kit/ node_modules/
npm install
npm run build
```

#### Environment Variables

```bash
# Check environment variables
printenv | grep VITE_

# Test with production config
NODE_ENV=production npm run build
```

#### Routing Issues

```javascript
// Ensure proper base path configuration
// svelte.config.js
const config = {
  kit: {
    paths: {
      base: process.env.NODE_ENV === 'production' ? '/your-repo-name' : ''
    }
  }
};
```

#### API Issues

```typescript
// Verify API endpoints are accessible
fetch('https://api-web.nhle.com/v1/score/2024-01-15')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Performance Issues

#### Large Bundle Size

```bash
# Analyze bundle
npm run build
npx vite-bundle-analyzer build/

# Check for large dependencies
npm ls --depth=0 | grep -E '[0-9]+\.[0-9]+\.[0-9]+.*[0-9]+'
```

#### Slow Load Times

```bash
# Check with Lighthouse
npm run build
npm run preview
# Run Lighthouse on localhost:4173
```

## Rollback Procedures

### Quick Rollback

```bash
# Git rollback
git checkout previous-commit-hash
npm run build
# Deploy to platform
```

### Platform-Specific Rollbacks

#### Vercel
```bash
# List deployments
vercel ls

# Rollback to specific deployment
vercel rollback [deployment-url]
```

#### Netlify
```bash
# List deploys
netlify deploy:list

# Promote specific deploy
netlify deploy:promote --site=site-id [deploy-id]
```

## Maintenance

### Regular Tasks

1. **Dependency Updates**
   ```bash
   npm outdated
   npm update
   ```

2. **Security Audits**
   ```bash
   npm audit
   npm audit fix
   ```

3. **Performance Monitoring**
   - Check Core Web Vitals
   - Monitor bundle size
   - Review API response times

4. **Backup Strategy**
   - Git repository backup
   - Configuration backup
   - Data backup (if applicable)

This deployment guide provides comprehensive instructions for deploying the Finnish NHL Player Tracker to various platforms while ensuring performance, security, and maintainability.