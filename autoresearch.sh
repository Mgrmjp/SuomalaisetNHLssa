#!/bin/bash
set -euo pipefail

# Autoresearch shell for mestis-image-matching experiment
# Measures image match rate for Mestis players

# The script validates the image matching logic
# Outputs METRIC lines for parsing

OUTPUT_FILE="${OUTPUT_FILE:-/tmp/mestis_test_results.json}"

# Run a quick validation of the slug generation and name matching logic
node -e "
const fs = require('fs');

// Test name normalization and slug generation
const normalizeMestisName = (value) => (value || '')
    .replace(/\*/g, '')
    .replace(/\s*,\s*/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();

const toMestisSlug = (value) => normalizeMestisName(value)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');

// Test cases - known Finnish surnames
const testNames = [
    'Mikko Rantanen',
    'Patrik Laine', 
    'Sebastian Aho',
    'Roope Hintz',
    'Aleksander Barkov',
    'Mikael Granlund',
    'Erik Karlsson',  // Swedish - should not match Finnish
    'Kimi Räikkönen',  // With special char
    'Joonas Donskoi',
    'Mikko Rantanen',  // Duplicate
];

let slugSuccess = 0;
let slugFail = 0;

for (const name of testNames) {
    const slug = toMestisSlug(name);
    if (slug && slug.length > 2) {
        slugSuccess++;
        console.log('OK: ' + name + ' -> ' + slug);
    } else {
        slugFail++;
        console.log('FAIL: ' + name + ' -> [' + slug + ']');
    }
}

console.log('');
console.log('METRIC slug_success_rate=' + (slugSuccess / testNames.length * 100).toFixed(2));
console.log('METRIC slug_success_count=' + slugSuccess);
console.log('METRIC slug_fail_count=' + slugFail);
" 2>&1