#!/usr/bin/env node
/**
 * Test all pages for JavaScript errors using Agent Browser
 */

import { AgentBrowser } from '@vercel/agent-browser';

const BASE_URL = process.env.TEST_URL || 'http://localhost:3000';

// Pages to test
const PAGES = [
  '/',
  '/lupaukset',
  '/sarjataulukot',
  '/joukkueet',
  '/pisteporssi',
  '/pelaajat',
  '/mestaruudet',
];

async function testPage(browser, path) {
  const url = `${BASE_URL}${path}`;
  console.log(`\n🧪 Testing: ${url}`);
  
  const errors = [];
  const logs = [];
  
  // Create a new page
  const page = await browser.newPage();
  
  // Capture console messages
  page.on('console', (msg) => {
    const text = msg.text();
    logs.push({ type: msg.type(), text });
    
    if (msg.type() === 'error') {
      errors.push({ type: 'console.error', message: text });
    }
    if (msg.type() === 'warning' || text.includes('404')) {
      console.log(`  ⚠️  ${msg.type()}: ${text.substring(0, 100)}`);
    }
  });
  
  // Capture page errors
  page.on('pageerror', (err) => {
    errors.push({ type: 'pageerror', message: err.message, stack: err.stack });
  });
  
  // Capture request failures
  page.on('requestfailed', (request) => {
    const url = request.url();
    if (!url.includes('.svg') && !url.includes('.webp')) {
      errors.push({ type: 'requestfailed', url, reason: request.failure()?.errorText });
    }
  });
  
  try {
    // Navigate to page
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    
    // Wait for page to settle
    await page.waitForTimeout(2000);
    
    // Check for specific error elements
    const hasErrorBoundary = await page.$('text="Uncaught ReferenceError"').catch(() => null);
    if (hasErrorBoundary) {
      errors.push({ type: 'error-boundary', message: 'Error boundary rendered' });
    }
    
    // Get page title
    const title = await page.title();
    
    await page.close();
    
    // Report results
    if (errors.length === 0) {
      console.log(`  ✅ No errors found (${logs.length} log messages)`);
      return { path, status: 'ok', logs: logs.length };
    } else {
      console.log(`  ❌ Found ${errors.length} error(s):`);
      errors.forEach(e => console.log(`     - ${e.type}: ${e.message?.substring(0, 100)}`));
      return { path, status: 'error', errors };
    }
    
  } catch (err) {
    console.log(`  ❌ Navigation failed: ${err.message}`);
    return { path, status: 'fail', error: err.message };
  }
}

async function main() {
  console.log('🚀 Starting Agent Browser tests...');
  console.log(`Base URL: ${BASE_URL}`);
  
  const browser = await AgentBrowser.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const results = [];
  
  for (const page of PAGES) {
    const result = await testPage(browser, page);
    results.push(result);
  }
  
  await browser.close();
  
  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 Test Summary');
  console.log('='.repeat(50));
  
  const ok = results.filter(r => r.status === 'ok');
  const errors = results.filter(r => r.status === 'error');
  const failed = results.filter(r => r.status === 'fail');
  
  console.log(`✅ Passed: ${ok.length}/${results.length}`);
  console.log(`❌ Errors: ${errors.length}/${results.length}`);
  console.log(`💥 Failed: ${failed.length}/${results.length}`);
  
  if (errors.length > 0) {
    console.log('\n❌ Pages with errors:');
    errors.forEach(e => console.log(`   - ${e.path}`));
    process.exit(1);
  }
  
  console.log('\n🎉 All tests passed!');
  process.exit(0);
}

main().catch(err => {
  console.error('Test runner failed:', err);
  process.exit(1);
});
