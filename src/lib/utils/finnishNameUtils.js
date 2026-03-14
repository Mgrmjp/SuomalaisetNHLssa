/**
 * Finnish name correction utilities.
 * Corrects Finnish letter patterns (ä, ö, å) using cache + patterns.
 * Works in both server (Node.js) and browser environments.
 */

// In-memory cache with common corrections
const defaultCorrections = {
    Armiä: 'Armia',
    Pyyhtia: 'Pyyhtiä',
    Kaskimaki: 'Kaskimäki',
    Kivenmaki: 'Kivenmäki',
    Raty: 'Räty',
    Raaty: 'Räty',
    Rasanen: 'Räsänen',
    Teravainen: 'Teräväinen',
    Parssinen: 'Pärssinen',
    Puljujarvi: 'Puljujärvi',
    Maatta: 'Määttä',
    Niemelainen: 'Niemeläinen',
    Hameenaho: 'Hämeenaho',
    Jamsen: 'Jämsén',
    Vaananen: 'Väänänen',
    Liljegren: 'Liljegren',
    Helenius: 'Helenius',
    Jarvi: 'Järvi',
    Jarvenpaa: 'Järvenpää',
    Hameenlinna: 'Hämeenlinna',
    Siilinjarvi: 'Siilinjärvi',
    Kaarina: 'Kaarina',
    Merilainen: 'Meriläinen',
    Luukkonen: 'Luukkonen',
    Husso: 'Husso',
}

// In-memory cache (starts with defaults)
const nameCache = { ...defaultCorrections }
const llmCorrectionCache = new Map()

/**
 * Correct Finnish name using cache and patterns.
 *
 * @param {string} name - The name to correct
 * @returns {string} Corrected name
 */
export function correctFinnishName(name) {
    if (!name || typeof name !== 'string') {
        return name
    }

    // Check cache first - this includes manual corrections that should always apply
    if (nameCache[name]) {
        return nameCache[name]
    }

    // If name already has Finnish characters, it's likely correct
    if (/[äöåÄÖÅ]/.test(name)) {
        return name
    }

    // Apply pattern-based corrections
    const corrected = applyPatternCorrections(name)

    // If correction was made, cache it
    if (corrected !== name) {
        nameCache[name] = corrected
    }

    return corrected
}

/**
 * Apply pattern-based corrections to a name.
 */
function applyPatternCorrections(name) {
    // Names ending in 'ia' that are correct as-is (should NOT become 'iä')
    const validIaNames = ['Armia', 'Vainio', 'Aaltonen', 'Sebastian']

    // Skip pattern correction for known valid 'ia' endings
    for (const validName of validIaNames) {
        if (name === validName || name.endsWith(` ${validName}`)) {
            return name
        }
    }

    // Pattern: 'ia' -> 'iä' at end of word (Finnish words ending in iä)
    // Skip if name ends in 'nen' (common Finnish surname ending, always correct)
    if (/ia$/.test(name) && !name.endsWith('nen')) {
        const corrected = name.replace(/ia$/, 'iä')
        if (isFinnishPattern(corrected)) {
            return corrected
        }
    }

    // Pattern: 'aa' -> 'ää' before 'nen' or 'ty'
    if (/aa/.test(name)) {
        // Raaty -> Räty
        if (/aa(ty|ny|ly|ry)$/.test(name)) {
            return name.replace(/aa/, 'ää')
        }
        // Parssinen -> Pärssinen
        if (/aanen$/.test(name)) {
            return name.replace(/aa/, 'ää')
        }
    }

    // Pattern: 'aki' -> 'äki' at end
    if (/aki$/.test(name)) {
        const corrected = name.replace(/aki$/, 'äki')
        if (isFinnishPattern(corrected)) {
            return corrected
        }
    }

    // Pattern: 'paa' -> 'pä' (common prefix)
    if (/paa/.test(name)) {
        return name.replace(/paa/g, 'pää')
    }

    // Pattern: 'jarvi' -> 'järvi'
    if (/jarvi/i.test(name)) {
        return name.replace(/jarvi/g, 'järvi').replace(/Jarvi/g, 'Järvi')
    }

    return name
}

/**
 * Check if corrected name follows Finnish patterns.
 */
function isFinnishPattern(name) {
    // Common Finnish ending patterns
    const finnishEndings = [
        'nen',
        'mäki',
        'järvi',
        'lahti',
        'niemi',
        'saari',
        'tä',
        'jä',
        'ty',
        'iä',
    ]
    return finnishEndings.some((ending) => name.toLowerCase().endsWith(ending))
}

/**
 * Correct full name (first + last)
 */
export function correctFullName(fullName) {
    if (!fullName || typeof fullName !== 'string') {
        return fullName
    }

    const parts = fullName.trim().split(/\s+/)
    if (parts.length === 0) return fullName

    // Correct each part
    const corrected = parts.map((part) => correctFinnishName(part))

    return corrected.join(' ')
}

/**
 * Conservative server-side LLM fallback for Finnish names.
 * Uses a small model only when deterministic rules are insufficient.
 *
 * @param {string} fullName
 * @param {string | null | undefined} apiKey
 * @returns {Promise<string>}
 */
export async function correctFullNameWithLLM(fullName, apiKey) {
    if (!fullName || typeof fullName !== 'string') {
        return fullName
    }

    const deterministic = correctFullName(fullName)

    if (!apiKey) {
        return deterministic
    }

    const cacheKey = fullName.trim()
    if (llmCorrectionCache.has(cacheKey)) {
        return llmCorrectionCache.get(cacheKey)
    }

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${apiKey}`,
            },
            body: JSON.stringify({
                model: 'gpt-4o-mini',
                temperature: 0,
                max_tokens: 40,
                messages: [
                    {
                        role: 'user',
                        content: `Correct this Finnish hockey player name only if it is missing obvious Finnish characters like ä, ö, or å.

Rules:
- Be conservative.
- Keep the same person and same spelling otherwise.
- Return only the corrected full name.
- If no correction is needed, return the input unchanged.

Name: "${fullName}"`,
                    },
                ],
            }),
        })

        if (!response.ok) {
            return deterministic
        }

        const data = await response.json()
        const content = data?.choices?.[0]?.message?.content?.trim()
        const corrected = content ? content.replace(/^"|"$/g, '').split('\n')[0].trim() : ''

        const finalName = corrected || deterministic
        llmCorrectionCache.set(cacheKey, finalName)
        return finalName
    } catch (_error) {
        return deterministic
    }
}

/**
 * Process player data array and correct Finnish names
 */
export function correctPlayerNames(players) {
    if (!Array.isArray(players)) {
        return players
    }

    return players.map((player) => {
        if (player.skaterFullName) {
            player.skaterFullName = correctFullName(player.skaterFullName)
        }
        if (player.goalieFullName) {
            player.goalieFullName = correctFullName(player.goalieFullName)
        }
        if (player.lastName) {
            player.lastName = correctFinnishName(player.lastName)
        }
        return player
    })
}

/**
 * Manually add a correction to the cache.
 * Useful for adding known corrections that patterns don't catch.
 */
export function addCorrection(incorrect, correct) {
    nameCache[incorrect] = correct
}

/**
 * Get cache statistics for debugging.
 */
export function getCacheStats() {
    return {
        entries: Object.keys(nameCache).length,
        keys: Object.keys(nameCache),
    }
}
