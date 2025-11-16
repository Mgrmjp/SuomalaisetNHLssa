/**
 * Simple Node.js Logger
 *
 * A console-based logger compatible with Node.js scripts.
 * Replaces the SvelteKit-specific logger that uses import.meta.env.
 */

const isDevelopment = process.env.NODE_ENV === 'development' || !process.env.NODE_ENV

/**
 * Logger object with methods for different log levels
 */
const logger = {
  /**
   * Log info message
   * @param {string} message - Message to log
   * @param {any} data - Optional data to log
   */
  info: (message, data) => {
    if (isDevelopment) {
      console.log(`[INFO] ${message}`, data || '')
    }
  },

  /**
   * Log debug message
   * @param {string} message - Message to log
   * @param {any} data - Optional data to log
   */
  debug: (message, data) => {
    if (isDevelopment) {
      console.log(`[DEBUG] ${message}`, data || '')
    }
  },

  /**
   * Log warning message
   * @param {string} message - Message to log
   * @param {any} data - Optional data to log
   */
  warn: (message, data) => {
    console.warn(`[WARN] ${message}`, data || '')
  },

  /**
   * Log error message
   * @param {string} message - Message to log
   * @param {Error|string} error - Error object or error message
   */
  error: (message, error) => {
    console.error(`[ERROR] ${message}`)
    if (error) {
      if (error instanceof Error) {
        console.error('Stack:', error.stack)
      } else {
        console.error('Details:', error)
      }
    }
  },

  /**
   * Log success message
   * @param {string} message - Message to log
   * @param {any} data - Optional data to log
   */
  success: (message, data) => {
    console.log(`✅ ${message}`, data || '')
  },

  /**
   * Log message with timestamp
   * @param {string} message - Message to log
   * @param {any} data - Optional data to log
   */
  timestamp: (message, data) => {
    const timestamp = new Date().toISOString()
    console.log(`[${timestamp}] ${message}`, data || '')
  }
}

export default logger