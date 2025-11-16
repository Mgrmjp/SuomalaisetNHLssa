/**
 * Simple Error Logging Utility
 *
 * A lightweight logging utility that provides basic error logging functionality
 * without complex performance monitoring overhead.
 */

// Log levels for different types of messages
const LOG_LEVELS = {
    ERROR: 0,
    WARN: 1,
    INFO: 2,
    DEBUG: 3,
}

// Current log level (can be adjusted based on environment)
const currentLogLevel =
    typeof process !== 'undefined' && process.env.NODE_ENV === 'production'
        ? LOG_LEVELS.ERROR
        : LOG_LEVELS.DEBUG

/**
 * Simple logger with basic functionality
 */
const logger = {
    /**
     * Generic log method (for compatibility with existing code)
     * @param {string} message - Message to log
     * @param {any} data - Optional data to log
     */
    log(message, data = null) {
        if (currentLogLevel >= LOG_LEVELS.INFO) {
            console.log(message)
            if (data !== null && data !== undefined) {
                console.log('Details:', data)
            }
        }
    },

    /**
     * Log error message
     * @param {string} message - Error message
     * @param {Error|any} error - Error object or additional data
     */
    error(message, error = null) {
        if (currentLogLevel >= LOG_LEVELS.ERROR) {
            console.error(`[ERROR] ${message}`)
            if (error !== null && error !== undefined) {
                if (error instanceof Error) {
                    console.error('Details:', error.message)
                    if (currentLogLevel >= LOG_LEVELS.DEBUG) {
                        console.error('Stack:', error.stack)
                    }
                } else {
                    console.error('Details:', error)
                }
            }
        }
    },

    /**
     * Log warning message
     * @param {string} message - Warning message
     * @param {any} data - Additional data (optional)
     */
    warn(message, data = null) {
        if (currentLogLevel >= LOG_LEVELS.WARN) {
            console.warn(`[WARN] ${message}`)
            if (data !== null && data !== undefined) {
                console.warn('Details:', data)
            }
        }
    },

    /**
     * Log info message
     * @param {string} message - Info message
     * @param {any} data - Additional data (optional)
     */
    info(message, data = null) {
        if (currentLogLevel >= LOG_LEVELS.INFO) {
            console.log(`[INFO] ${message}`)
            if (data !== null && data !== undefined) {
                console.log('Details:', data)
            }
        }
    },

    /**
     * Log debug message
     * @param {string} message - Debug message
     * @param {any} data - Additional data (optional)
     */
    debug(message, data = null) {
        if (currentLogLevel >= LOG_LEVELS.DEBUG) {
            console.log(`[DEBUG] ${message}`)
            if (data !== null && data !== undefined) {
                console.log('Details:', data)
            }
        }
    },

    /**
     * Log success message (alias for info with success prefix)
     * @param {string} message - Success message
     * @param {any} data - Additional data (optional)
     */
    success(message, data = null) {
        if (currentLogLevel >= LOG_LEVELS.INFO) {
            console.log(`✅ ${message}`)
            if (data !== null && data !== undefined) {
                console.log('Details:', data)
            }
        }
    },

    /**
     * Log message with timestamp
     * @param {string} message - Message to log
     * @param {any} data - Additional data (optional)
     */
    timestamp(message, data = null) {
        if (currentLogLevel >= LOG_LEVELS.INFO) {
            const timestamp = new Date().toISOString()
            console.log(`[${timestamp}] ${message}`)
            if (data !== null && data !== undefined) {
                console.log('Details:', data)
            }
        }
    },
}

export default logger
