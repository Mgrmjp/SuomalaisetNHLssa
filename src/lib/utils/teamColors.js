/**
 * Team Color System
 * Extracts dominant colors from team SVG logos and provides them for styling
 */

// Cache for extracted team colors
const teamColorCache = new Map()

// Clear cache for debugging
teamColorCache.clear()

// Predefined fallback colors for teams in case extraction fails
const fallbackTeamColors = {
  'ANA': ['#8B0000', '#FDD017'], // Anaheim Ducks - Maroon & Gold
  'ARI': ['#8C2633', '#E31937'], // Arizona Coyotes - Brick Red & Coyote Red
  'BOS': ['#FFB81C', '#000000'], // Boston Bruins - Gold & Black
  'BUF': ['#002D62', '#FFB81C'], // Buffalo Sabres - Navy Blue & Gold
  'CAR': ['#CE1126', '#000000'], // Carolina Hurricanes - Red & Black
  'CBJ': ['#002D62', '#CE1126'], // Columbus Blue Jackets - Navy Blue & Red
  'CGY': ['#CE1126', '#FDD017'], // Calgary Flames - Red & Gold
  'CHI': ['#CF0A2C', '#000000'], // Chicago Blackhawks - Red & Black
  'COL': ['#6F0023', '#002244'], // Colorado Avalanche - Burgundy & Navy
  'DAL': ['#00823E', '#A2AAAD'], // Dallas Stars - Victory Green & Silver
  'DET': ['#CE1126', '#FFFFFF'], // Detroit Red Wings - Red & White
  'EDM': ['#041E42', '#FF4C00'], // Edmonton Oilers - Navy Blue & Orange
  'FLA': ['#C8102E', '#041E42'], // Florida Panthers - Panther Red & Navy
  'LAK': ['#111111', '#A2AAAD'], // Los Angeles Kings - Black & Silver
  'MIN': ['#154734', '#A2AAAD'], // Minnesota Wild - Forest Green & Iron Range Red
  'MTL': ['#AF1E2D', '#192168'], // Montreal Canadiens - Red & Blue
  'NJD': ['#CE1126', '#000000'], // New Jersey Devils - Red & Black
  'NSH': ['#FFB81C', '#041E42'], // Nashville Predators - Gold & Navy
  'NYI': ['#00539B', '#F47938'], // New York Islanders - Blue & Orange
  'NYR': ['#0038A8', '#CE1126'], // New York Rangers - Blue & Red
  'OTT': ['#C52032', '#000000'], // Ottawa Senators - Red & Black
  'PHI': ['#F74902', '#000000'], // Philadelphia Flyers - Orange & Black
  'PIT': ['#FFB81C', '#000000'], // Pittsburgh Penguins - Gold & Black
  'SEA': ['#4D908E', '#99D9EA'], // Seattle Kraken - Deep Sea Blue & Ice Blue
  'SJS': ['#006276', '#ECA352'], // San Jose Sharks - Pacific Teal & Burnt Orange
  'STL': ['#002F6C', '#FCB514'], // St. Louis Blues - Blue & Gold
  'TBL': ['#002868', '#FFFFFF'], // Tampa Bay Lightning - Blue & White
  'TOR': ['#003E7E', '#FFFFFF'], // Toronto Maple Leafs - Blue & White
  'UTA': ['#00275D', '#8B8C89'], // Utah Hockey Club - Navy Blue & Ice Silver
  'VAN': ['#00205B', '#041C2C'], // Vancouver Canucks - Royal Blue & Navy Blue
  'VEG': ['#333F48', '#B9975B'], // Vegas Golden Knights - Steel Gray & Gold
  'WPG': ['#01408D', '#AF1E2D'], // Winnipeg Jets - Royal Blue & Aviator Navy
  'WSH': ['#C8102E', '#041E42']  // Washington Capitals - Red & Navy Blue
}

/**
 * Convert hex color to RGB
 * @param {string} hex - Hex color string
 * @returns {Object|null} RGB values or null if invalid
 */
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null
}

/**
 * Convert RGB to HSL
 * @param {number} r - Red value (0-255)
 * @param {number} g - Green value (0-255)
 * @param {number} b - Blue value (0-255)
 * @returns {Object} HSL values
 */
function rgbToHsl(r, g, b) {
  r /= 255
  g /= 255
  b /= 255

  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  let h, s, l = (max + min) / 2

  if (max === min) {
    h = s = 0 // achromatic
  } else {
    const d = max - min
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break
      case g: h = ((b - r) / d + 2) / 6; break
      case b: h = ((r - g) / d + 4) / 6; break
    }
  }

  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100)
  }
}

/**
 * Calculate team color hue score based on common NHL team colors
 * @param {number} hue - Hue value (0-360)
 * @returns {number} Score for team color prioritization
 */
function getTeamColorHueScore(hue) {
  const normalizedHue = hue % 360

  // Green (Dallas, Minnesota, Colorado)
  if (normalizedHue >= 90 && normalizedHue <= 150) return 100

  // Blue (Toronto, Vancouver, Winnipeg, Tampa Bay)
  if (normalizedHue >= 200 && normalizedHue <= 260) return 95

  // Red (Detroit, Calgary, Montreal, Carolina, Columbus)
  if ((normalizedHue >= 0 && normalizedHue <= 30) || (normalizedHue >= 330 && normalizedHue <= 360)) return 90

  // Orange (Edmonton, Philadelphia, NY Islanders, Florida)
  if (normalizedHue >= 30 && normalizedHue <= 60) return 85

  // Purple (Los Angeles)
  if (normalizedHue >= 270 && normalizedHue <= 330) return 80

  return 50 // Other colors
}

/**
 * Check if a color is vibrant enough to be considered team color
 * @param {string} hexColor - Hex color string
 * @returns {boolean} True if color is vibrant enough
 */
function isColorVibrantEnough(hexColor) {
  const rgb = hexToRgb(hexColor)
  if (!rgb) return false

  const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b)

  // Must have sufficient saturation (>30%)
  if (hsl.s < 30) return false

  // Must not be too light or too dark (15% < lightness < 85%)
  if (hsl.l < 15 || hsl.l > 85) return false

  // Bonus for team-specific hues
  const hueScore = getTeamColorHueScore(hsl.h)
  return hueScore > 70
}

/**
 * Calculate color vibrancy score
 * @param {string} hexColor - Hex color string
 * @param {number} frequency - How often color appears in SVG
 * @returns {number} Vibrancy score
 */
function calculateColorVibrancyScore(hexColor, frequency) {
  const rgb = hexToRgb(hexColor)
  if (!rgb) return 0

  const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b)

  let score = 0

  // Saturation scoring (40% weight) - vibrant colors score higher
  score += hsl.s * 0.4

  // Lightness scoring (30% weight) - avoid pure white/black
  const lightnessScore = (hsl.l > 20 && hsl.l < 80) ? 50 : 0
  score += lightnessScore * 0.3

  // Team color prioritization (20% weight)
  const hueScore = getTeamColorHueScore(hsl.h)
  score += hueScore * 0.2

  // Frequency bonus (10% weight) - minor tie-breaker
  const frequencyBonus = Math.log(frequency + 1) * 2
  score += frequencyBonus * 0.1

  return score
}

/**
 * Extract colors from team SVG file
 * @param {string} teamAbbr - Team abbreviation (e.g., 'TOR', 'MTL')
 * @returns {Promise<Array>} Array of hex colors extracted from the SVG
 */
async function extractTeamColors(teamAbbr) {
  const normalizedTeam = teamAbbr.toLowerCase()
  const svgPath = `/nhl-logos/${normalizedTeam}.svg`

  try {
    // In browser environment, we'll fetch the SVG content
    if (typeof window !== 'undefined') {
      const response = await fetch(svgPath)
      if (!response.ok) {
        console.warn(`Failed to fetch team logo: ${svgPath} - Status: ${response.status}`)
        return fallbackTeamColors[teamAbbr.toUpperCase()] || ['#000000', '#FFFFFF']
      }

      const svgContent = await response.text()
      const extractedColors = extractColorsFromSVG(svgContent)
      console.log(`Extracted colors for ${teamAbbr}:`, extractedColors)
      return extractedColors
    }
  } catch (error) {
    console.warn(`Error extracting colors for ${teamAbbr}:`, error)
    return fallbackTeamColors[teamAbbr.toUpperCase()] || ['#000000', '#FFFFFF']
  }
}

/**
 * Extract colors from SVG content string
 * @param {string} svgContent - SVG content as string
 * @returns {Array} Array of hex colors
 */
function extractColorsFromSVG(svgContent) {
  const colors = new Map()

  // Extract colors from fill attributes with frequency counting
  const fillMatches = svgContent.match(/fill="([^"]+)"/g)
  if (fillMatches) {
    fillMatches.forEach(match => {
      const color = match.match(/fill="([^"]+)"/)[1]
      if (isValidColor(color)) {
        colors.set(color, (colors.get(color) || 0) + 1)
      }
    })
  }

  // Extract colors from style attributes
  const styleMatches = svgContent.match(/style="([^"]+)"/g)
  if (styleMatches) {
    styleMatches.forEach(match => {
      const styleContent = match.match(/style="([^"]+)"/)[1]
      // Look for color properties
      const colorProps = styleContent.match(/(fill|stroke):\s*([^;]+)/g)
      if (colorProps) {
        colorProps.forEach(prop => {
          const color = prop.split(':')[1].trim()
          if (isValidColor(color)) {
            colors.set(color, (colors.get(color) || 0) + 1)
          }
        })
      }
    })
  }

  // Convert to array and sort by frequency (most used colors first)
  const sortedColors = Array.from(colors.entries())
    .sort((a, b) => b[1] - a[1])
    .map(entry => entry[0])

  // Filter out neutral colors but be more selective
  const vibrantColors = sortedColors.filter(color => {
    const hex = color.toUpperCase()
    // Remove pure black, white, and grays - we want vibrant team colors!
    const neutralColors = ['#FFFFFF', '#000000', '#808080', '#A9A9A9', '#C0C0C0', '#D3D3D3']

    // Also filter out very light colors that are almost white
    if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
      const r = parseInt(hex.slice(1, 3), 16)
      const g = parseInt(hex.slice(3, 5), 16)
      const b = parseInt(hex.slice(5, 7), 16)
      const brightness = (r * 299 + g * 587 + b * 114) / 1000
      if (brightness > 240) return false // Too light/white
      if (brightness < 20) return false // Too dark/black
    }

    return !neutralColors.includes(hex)
  })

  // If no vibrant colors found, look for dark colors that could work
  if (vibrantColors.length === 0) {
    const darkColors = sortedColors.filter(color => {
      const hex = color.toUpperCase()
      if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
        const r = parseInt(hex.slice(1, 3), 16)
        const g = parseInt(hex.slice(3, 5), 16)
        const b = parseInt(hex.slice(5, 7), 16)
        const brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness < 128 // Dark colors
      }
      return false
    })

    if (darkColors.length > 0) {
      return darkColors.slice(0, 2)
    }
  }

  // Return the most prominent vibrant colors (up to 4 for better variety)
  const result = vibrantColors.slice(0, 4)

  // If we still don't have enough colors, add some from the original sorted list
  if (result.length < 2) {
    const additionalColors = sortedColors
      .filter(color => !result.includes(color))
      .slice(0, 2 - result.length)
    result.push(...additionalColors)
  }

  // Ensure we always have at least 2 colors
  while (result.length < 2) {
    const fallback = result.length === 0 ? '#000000' : '#FFFFFF'
    if (!result.includes(fallback)) {
      result.push(fallback)
    }
  }

  return result
}

/**
 * Check if a color value is valid
 * @param {string} color - Color value to validate
 * @returns {boolean} True if valid color
 */
function isValidColor(color) {
  // Check for hex colors
  if (/^#[0-9A-Fa-f]{6}$/.test(color)) return true
  if (/^#[0-9A-Fa-f]{3}$/.test(color)) return true

  // Check for RGB colors
  if (/^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$/.test(color)) return true

  // Check for named colors (basic ones we want to keep)
  const namedColors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'cyan', 'magenta']
  return namedColors.includes(color.toLowerCase())
}

/**
 * Get team colors with caching
 * @param {string} teamAbbr - Team abbreviation
 * @returns {Promise<Array>} Array of team colors
 */
export async function getTeamColors(teamAbbr) {
  const upperTeamAbbr = teamAbbr.toUpperCase()

  // For debugging: clear cache to force re-extraction
  if (teamColorCache.has(upperTeamAbbr)) {
    console.log(`Using cached colors for ${upperTeamAbbr}:`, teamColorCache.get(upperTeamAbbr))
    return teamColorCache.get(upperTeamAbbr)
  }

  try {
    console.log(`Extracting fresh colors for ${upperTeamAbbr}...`)
    const colors = await extractTeamColors(upperTeamAbbr)
    teamColorCache.set(upperTeamAbbr, colors)
    console.log(`Cached colors for ${upperTeamAbbr}:`, colors)
    return colors
  } catch (error) {
    console.warn(`Error getting colors for ${upperTeamAbbr}:`, error)
    const fallback = fallbackTeamColors[upperTeamAbbr] || ['#000000', '#FFFFFF']
    teamColorCache.set(upperTeamAbbr, fallback)
    console.log(`Using fallback colors for ${upperTeamAbbr}:`, fallback)
    return fallback
  }
}

/**
 * Get CSS border style string from team colors
 * @param {string} teamAbbr - Team abbreviation
 * @returns {Promise<string>} CSS border style
 */
export async function getTeamBorderStyle(teamAbbr) {
  const colors = await getTeamColors(teamAbbr)

  if (colors.length >= 2) {
    // Create a stunning gradient border using the two most prominent colors
    return `2px solid transparent; background: linear-gradient(white, white) padding-box, linear-gradient(135deg, ${colors[0]}, ${colors[1]}) border-box;`
  } else if (colors.length === 1) {
    return `2px solid ${colors[0]}`
  }

  return '2px solid #000000'
}

/**
 * Generate complementary accent color for better gradient variety
 * @param {string} primaryColor - Primary team color (hex)
 * @param {string} secondaryColor - Secondary team color (hex)
 * @returns {string} Generated accent color (hex)
 */
function generateAccentColor(primaryColor, secondaryColor) {
  try {
    // Convert hex to RGB
    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : null
    }

    // Convert RGB to hex
    const rgbToHex = (r, g, b) => {
      return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
    }

    const primary = hexToRgb(primaryColor)
    const secondary = hexToRgb(secondaryColor)

    if (!primary || !secondary) {
      return primaryColor // Fallback to primary if conversion fails
    }

    // Generate a complementary color by shifting hue
    // Convert to HSL-like representation for easier manipulation
    const avgR = (primary.r + secondary.r) / 2
    const avgG = (primary.g + secondary.g) / 2
    const avgB = (primary.b + secondary.b) / 2

    // Create accent by shifting towards complementary color
    // Using a simplified complementary color algorithm
    const accentR = Math.round(255 - avgR * 0.3)
    const accentG = Math.round(255 - avgG * 0.3)
    const accentB = Math.round(255 - avgB * 0.3)

    // Ensure the accent is sufficiently different from both primary and secondary
    const finalR = accentR > 200 ? Math.max(accentR - 30, primary.r + 20, secondary.r + 20) : accentR
    const finalG = accentG > 200 ? Math.max(accentG - 30, primary.g + 20, secondary.g + 20) : accentG
    const finalB = accentB > 200 ? Math.max(accentB - 30, primary.b + 20, secondary.b + 20) : accentB

    return rgbToHex(
      Math.max(0, Math.min(255, finalR)),
      Math.max(0, Math.min(255, finalG)),
      Math.max(0, Math.min(255, finalB))
    )
  } catch (error) {
    console.warn('Error generating accent color:', error)
    return primaryColor // Fallback to primary color
  }
}

/**
 * Darken a hex color by reducing lightness
 * @param {string} hexColor - Hex color string
 * @param {number} amount - Amount to darken (0-1), default 0.3
 * @returns {string} Darkened hex color
 */
function darkenColor(hexColor, amount = 0.3) {
  const rgb = hexToRgb(hexColor)
  if (!rgb) return hexColor

  // Convert to HSL for easier darkening
  const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b)

  // Reduce lightness but keep hue and saturation
  const darkenedLightness = Math.max(10, hsl.l * (1 - amount))

  // Convert back to RGB
  const h = hsl.h / 360
  const s = hsl.s / 100
  const l = darkenedLightness / 100

  if (s === 0) {
    // Achromatic case - just return the darkened gray
    const gray = Math.round(l * 255)
    return `#${gray.toString(16).padStart(2, '0')}${gray.toString(16).padStart(2, '0')}${gray.toString(16).padStart(2, '0')}`
  }

  const hue2rgb = (p, q, t) => {
    if (t < 0) t += 1
    if (t > 1) t -= 1
    if (t < 1/6) return p + (q - p) * 6 * t
    if (t < 1/2) return q
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6
    return p
  }

  const q = l < 0.5 ? l * (1 + s) : l + s - l * s
  const p = 2 * l - q
  const finalR = Math.round(hue2rgb(p, q, h + 1/3) * 255)
  const finalG = Math.round(hue2rgb(p, q, h) * 255)
  const finalB = Math.round(hue2rgb(p, q, h - 1/3) * 255)

  return `#${finalR.toString(16).padStart(2, '0')}${finalG.toString(16).padStart(2, '0')}${finalB.toString(16).padStart(2, '0')}`
}

/**
 * Randomly select colors from extracted palette for variety
 * @param {Array} colors - Array of extracted colors
 * @param {number} count - Number of colors to select
 * @returns {Array} Array of randomly selected and darkened colors
 */
function getRandomColors(colors, count = 3) {
  // Filter out white and light colors that become white when darkened
  const usableColors = colors.filter(color => {
    const hex = color.toUpperCase()
    // Skip pure white and very light colors
    if (hex === '#FFFFFF' || hex === '#FFF') return false
    if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
      const r = parseInt(hex.slice(1, 3), 16)
      const g = parseInt(hex.slice(3, 5), 16)
      const b = parseInt(hex.slice(5, 7), 16)
      const brightness = (r * 299 + g * 587 + b * 114) / 1000
      if (brightness > 240) return false // Too light/white
    }
    return true
  })

  // If no usable colors, return fallback colors
  if (usableColors.length === 0) {
    return ['#1a1a1a', '#2d2d2d', '#404040'].slice(0, count)
  }

  // Create a weighted array that favors more vibrant colors
  const weightedColors = usableColors.flatMap(color => {
    const weight = isColorVibrantEnough(color) ? 4 : 1
    return Array(weight).fill(color)
  })

  // Shuffle and select unique colors
  const shuffled = weightedColors.sort(() => Math.random() - 0.5)
  const uniqueColors = [...new Set(shuffled)]

  let selectedColors = uniqueColors.slice(0, Math.min(count, uniqueColors.length))

  // If we still don't have enough colors, add more from usableColors
  if (selectedColors.length < count) {
    const remaining = usableColors.filter(color => !selectedColors.includes(color))
    selectedColors = selectedColors.concat(remaining.slice(0, count - selectedColors.length))
  }

  // Darken the selected colors for richer, deeper appearance
  return selectedColors.map(color => darkenColor(color, 0.35))
}

/**
 * Generate CSS variables for team colors with random selection from logo palette
 * @param {string} teamAbbr - Team abbreviation
 * @returns {Promise<Object>} Object with CSS variable values
 */
export async function getTeamColorVariables(teamAbbr) {
  const colors = await getTeamColors(teamAbbr)

  console.log(`🎨 Raw extracted colors for ${teamAbbr}:`, colors)

  // Randomly select 3 colors from the palette (favoring vibrant ones)
  const selectedColors = getRandomColors(colors, 3)

  console.log(`🎲 Randomly selected colors for ${teamAbbr}:`, selectedColors)
  console.log(`🌙 Darkened colors for ${teamAbbr}:`, selectedColors.map(c => `${c} (${Math.round((1 - 0.35) * 100)}% darker)`))

  let primaryColor = selectedColors[0] || '#000000'
  let secondaryColor = selectedColors[1] || '#FFFFFF'
  let accentColor = selectedColors[2] || primaryColor

  // Ensure we have distinct colors
  if (secondaryColor === primaryColor && colors.length > 1) {
    const alternative = colors.find(c => c !== primaryColor)
    if (alternative) secondaryColor = alternative
  }

  if (accentColor === primaryColor || accentColor === secondaryColor) {
    accentColor = generateAccentColor(primaryColor, secondaryColor)
  }

  const result = {
    '--team-primary-color': primaryColor,
    '--team-secondary-color': secondaryColor,
    '--team-accent-color': accentColor
  }

  console.log(`🎯 Final colors for ${teamAbbr}:`, result)
  return result
}

/**
 * Get team colors specifically optimized for gradient animations
 * @param {string} teamAbbr - Team abbreviation
 * @returns {Promise<Array>} Array of 3 colors optimized for gradients
 */
export async function getTeamGradientColors(teamAbbr) {
  const colorVars = await getTeamColorVariables(teamAbbr)

  return [
    colorVars['--team-primary-color'],
    colorVars['--team-secondary-color'],
    colorVars['--team-accent-color']
  ]
}

/**
 * Preload colors for common teams (called during app initialization)
 */
export async function preloadCommonTeamColors() {
  const commonTeams = ['TOR', 'MTL', 'VAN', 'CGY', 'EDM', 'OTT', 'WPG', 'COL', 'CHI', 'DET', 'BOS', 'BUF']

  const promises = commonTeams.map(async team => {
    try {
      await getTeamColors(team)
      console.log(`✓ Preloaded colors for ${team}`)
    } catch (error) {
      console.warn(`✗ Failed to preload colors for ${team}:`, error)
    }
  })

  await Promise.allSettled(promises)
}