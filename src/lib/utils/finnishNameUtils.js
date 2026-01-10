/**
 * Finnish name correction utilities.
 * Corrects Finnish letter patterns (ä, ö, å) using cache + patterns.
 * Works in both server (Node.js) and browser environments.
 */

// In-memory cache with common corrections
const defaultCorrections = {
    "Pyyhtia": "Pyyhtiä",
    "Kaskimaki": "Kaskimäki",
    "Raty": "Räty",
    "Raaty": "Räty",
    "Teravainen": "Teräväinen",
    "Parssinen": "Pärssinen",
    "Puljujarvi": "Puljujärvi",
    "Maatta": "Määttä",
    "Liljegren": "Liljegren",
    "Helenius": "Helenius",
    "Jarvi": "Järvi",
    "Jarvenpaa": "Järvenpää",
    "Hameenlinna": "Hämeenlinna",
    "Siilinjarvi": "Siilinjärvi",
    "Kaarina": "Kaarina",
    "Merilainen": "Meriläinen",
    "Luukkonen": "Luukkonen",
    "Husso": "Husso",
};

// In-memory cache (starts with defaults)
let nameCache = { ...defaultCorrections };

/**
 * Correct Finnish name using cache and patterns.
 *
 * @param {string} name - The name to correct
 * @returns {string} Corrected name
 */
export function correctFinnishName(name) {
    if (!name || typeof name !== 'string') {
        return name;
    }

    // If name already has Finnish characters, it's likely correct
    if (/[äöåÄÖÅ]/.test(name)) {
        return name;
    }

    // Check cache first
    if (nameCache[name]) {
        return nameCache[name];
    }

    // Apply pattern-based corrections
    const corrected = applyPatternCorrections(name);

    // If correction was made, cache it
    if (corrected !== name) {
        nameCache[name] = corrected;
    }

    return corrected;
}

/**
 * Apply pattern-based corrections to a name.
 */
function applyPatternCorrections(name) {
    // Pattern: 'ia' -> 'iä' at end of word (Finnish words ending in iä)
    if (/ia$/.test(name)) {
        const corrected = name.replace(/ia$/, 'iä');
        if (isFinnishPattern(corrected)) {
            return corrected;
        }
    }

    // Pattern: 'aa' -> 'ää' before 'nen' or 'ty'
    if (/aa/.test(name)) {
        // Raaty -> Räty
        if (/aa(ty|ny|ly|ry)$/.test(name)) {
            return name.replace(/aa/, 'ää');
        }
        // Parssinen -> Pärssinen
        if (/aanen$/.test(name)) {
            return name.replace(/aa/, 'ää');
        }
    }

    // Pattern: 'aki' -> 'äki' at end
    if (/aki$/.test(name)) {
        const corrected = name.replace(/aki$/, 'äki');
        if (isFinnishPattern(corrected)) {
            return corrected;
        }
    }

    // Pattern: 'paa' -> 'pä' (common prefix)
    if (/paa/.test(name)) {
        return name.replace(/paa/g, 'pää');
    }

    // Pattern: 'jarvi' -> 'järvi'
    if (/jarvi/i.test(name)) {
        return name.replace(/jarvi/g, 'järvi').replace(/Jarvi/g, 'Järvi');
    }

    return name;
}

/**
 * Check if corrected name follows Finnish patterns.
 */
function isFinnishPattern(name) {
    // Common Finnish ending patterns
    const finnishEndings = ['nen', 'mäki', 'järvi', 'lahti', 'niemi', 'saari', 'tä', 'jä', 'ty', 'iä'];
    return finnishEndings.some(ending => name.toLowerCase().endsWith(ending));
}

/**
 * Correct full name (first + last)
 */
export function correctFullName(fullName) {
    if (!fullName || typeof fullName !== 'string') {
        return fullName;
    }

    const parts = fullName.trim().split(/\s+/);
    if (parts.length === 0) return fullName;

    // Correct each part
    const corrected = parts.map(part => correctFinnishName(part));

    return corrected.join(' ');
}

/**
 * Process player data array and correct Finnish names
 */
export function correctPlayerNames(players) {
    if (!Array.isArray(players)) {
        return players;
    }

    return players.map(player => {
        if (player.skaterFullName) {
            player.skaterFullName = correctFullName(player.skaterFullName);
        }
        if (player.goalieFullName) {
            player.goalieFullName = correctFullName(player.goalieFullName);
        }
        if (player.lastName) {
            player.lastName = correctFinnishName(player.lastName);
        }
        return player;
    });
}

/**
 * Manually add a correction to the cache.
 * Useful for adding known corrections that patterns don't catch.
 */
export function addCorrection(incorrect, correct) {
    nameCache[incorrect] = correct;
}

/**
 * Get cache statistics for debugging.
 */
export function getCacheStats() {
    return {
        entries: Object.keys(nameCache).length,
        keys: Object.keys(nameCache)
    };
}
