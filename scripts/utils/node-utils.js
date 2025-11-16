// Node.js compatible utilities for Finnish NHL Player Tracker CLI

/**
 * Format date as YYYY-MM-DD string
 * @param {Date} date - Date object
 * @returns {string} Formatted date string
 */
export function formatDate(date) {
  return date.toISOString().split('T')[0]
}

/**
 * Get last night's date (for European NHL audience)
 * @returns {string} Yesterday's date in YYYY-MM-DD format
 */
export function getLastNightsDate() {
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  return formatDate(yesterday)
}