# Autoresearch: Mestis Player Image Matching

## Objective
Optimize the `extractMestisPlayerImages` function in `scraper-advanced.cjs` to improve the rate of correctly matched player images. Current issues:
- Name slug generation may not match URLs correctly
- Player link matching uses imperfect normalization
- Some Finnish compound surnames don't generate correct slugs

## Metrics
- **Primary**: image_match_rate (% of players with correctly matched images, higher is better)
- **Secondary**: slug_generation_success_rate, link_finding_success_rate

## How to Run
```bash
node scripts/scraper-advanced.cjs Mestis --debug
# Or run the test script that validates image matching
```

## Files in Scope
- `scripts/scraper-advanced.cjs` - Main scraper with `extractMestisPlayerImages` function (lines 850-984)
- Name normalization functions: `normalizeMestisName`, `toMestisSlug`

## Off Limits
- Don't change the Puppeteer browser launch configuration
- Don't remove cookie consent handling

## Constraints
- Must not increase the 10-minute timeout for image extraction
- Image URLs must still be valid (not placeholder images)

## What's Been Tried
- (No experiments run yet - baseline not established)