/**
 * API Helper Utilities
 *
 * Centralized API fetching logic with consistent error handling and retry logic
 */

import { base } from '$app/paths'

// Base path for static assets
const appBase = base

/**
 * Fetch data from NHL API with retry logic
 *
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @param {number} retries - Number of retries (default: 3)
 * @param {number} delay - Delay between retries in ms (default: 1000)
 * @returns {Promise<Object|null>} JSON response or null on failure
 */
export async function fetchFromAPI(url, options = {}, retries = 3, delay = 1000) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options)
            if (!response.ok) {
                if (response.status === 404) return null
                throw new Error(`HTTP ${response.status}: ${response.statusText}`)
            }
            return await response.json()
        } catch (error) {
            if (i === retries - 1) {
                console.error(`Failed to fetch ${url} after ${retries} attempts:`, error.message)
                return null
            }
            await new Promise((resolve) => setTimeout(resolve, delay * (i + 1)))
        }
    }
    return null
}

/**
 * Fetch JSON data from local file with error handling
 *
 * @param {string} path - Path to JSON file
 * @returns {Promise<Object|null>} JSON data or null on failure
 */
export async function fetchLocalJSON(path) {
    try {
        // Prepend base path if path starts with /
        const fullPath = path.startsWith('/') ? appBase + path : path
        const response = await fetch(fullPath)
        if (!response.ok) return null
        return await response.json()
    } catch (error) {
        console.debug(`No data found at ${path}:`, error.message)
        return null
    }
}

/**
 * Fetch data with timeout
 *
 * @param {string} url - URL to fetch
 * @param {number} timeoutMs - Timeout in milliseconds
 * @param {Object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 * @throws {Error} If timeout occurs
 */
export async function fetchWithTimeout(url, timeoutMs = 10000, options = {}) {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
        })
        clearTimeout(timeoutId)
        return response
    } catch (error) {
        clearTimeout(timeoutId)
        if (error.name === 'AbortError') {
            throw new Error(`Request timeout after ${timeoutMs}ms`)
        }
        throw error
    }
}
