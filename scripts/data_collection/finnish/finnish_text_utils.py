"""
Finnish text normalization utilities for player and city names.
Handles auto-correction of ASCII approximations to proper Finnish letters (ä, ö, å) using Google Gemini Flash LLM.
"""

import os
from google import genai
from google.genai import types

_gemini_client = None
_correction_cache = {}  # Cache corrections to avoid duplicate API calls


def get_gemini_client():
    """Initialize Gemini client (lazy loading)."""
    global _gemini_client
    if _gemini_client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


def correct_with_gemini(text, context_type="city"):
    """
    Use Gemini Flash LLM to validate/correct Finnish text.

    Args:
        text: Text to validate/correct
        context_type: "city" or "name" for prompt context

    Returns:
        Corrected text from Gemini LLM
    """
    if not text or not isinstance(text, str):
        return text

    # Check cache first
    cache_key = f"{context_type}:{text}"
    if cache_key in _correction_cache:
        return _correction_cache[cache_key]

    client = get_gemini_client()

    prompt = f"""You are a Finnish language expert. Determine if this {context_type} name needs Finnish letter corrections (ä, ö, å).

Input: "{text}"

CRITICAL: Be VERY conservative. ONLY correct obvious double-letter patterns:
- "aa" -> "ää" ONLY when followed by "nen" (Parssinen -> Pärssinen, Raty -> Räty)
- DO NOT correct single "a" in any position
- DO NOT correct "ja" (Matinpalo, Jani are correct)
- DO NOT correct "na" (Nikolas is correct)
- DO NOT correct "us" (Juuse is correct)

Return ONLY the name. If correct, return unchanged. If needs correction, return corrected version.

Examples:
Siilinjarvi -> Siilinjärvi
Hameenlinna -> Hämeenlinna
Turku -> Turku
Oulu -> Oulu
Parssinen -> Pärssinen
Raty -> Räty
Saros -> Saros
Matinpalo -> Matinpalo
Nikolas -> Nikolas
Jani -> Jani
Juuse -> Juuse

Output:"""

    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50,
        )
    )

    # Handle response safely
    if not response or not response.candidates or not response.candidates[0].content:
        return text

    corrected = response.candidates[0].content.parts[0].text.strip()

    # Clean up any extra text LLM might add (take first line or first word)
    if '\n' in corrected:
        corrected = corrected.split('\n')[0].strip()
    if ' ' in corrected and context_type == "city" and ' ' not in text:
        # If original was single word but response has multiple, take first word
        corrected = corrected.split()[0]

    # Remove common LLM artifacts
    corrected = corrected.replace('Corrected spelling:', '').strip()
    corrected = corrected.replace('Output:', '').strip()
    corrected = corrected.replace('**Reasoning**', '').strip()
    corrected = corrected.replace('**', '').strip()

    # Validate: return original if corrected is too different or empty
    if not corrected or len(corrected) > len(text) * 2:
        corrected = text
    # If corrected starts with non-letter, return original
    if corrected and not corrected[0].isalpha():
        corrected = text

    # Cache the result
    _correction_cache[cache_key] = corrected
    return corrected


def correct_finnish_name(name_dict):
    """
    Correct Finnish player name using Gemini Flash LLM.

    Args:
        name_dict: Dict like {'default': 'Parssinen', 'fi': 'Pärssinen'}

    Returns:
        Corrected name string
    """
    if not name_dict or not isinstance(name_dict, dict):
        return ""

    # Use default locale as input (Gemini will handle correction)
    default = name_dict.get('default', '')
    if not default:
        return ""

    return correct_with_gemini(default, "name")


def correct_finnish_city(city_dict):
    """
    Correct Finnish city name using Gemini Flash LLM.

    Args:
        city_dict: Dict like {'default': 'Siilinjarvi', 'fi': 'Siilinjärvi'}

    Returns:
        Corrected city name string
    """
    if not city_dict or not isinstance(city_dict, dict):
        return ""

    # Use default locale as input (Gemini will handle correction)
    default = city_dict.get('default', '')
    if not default:
        return ""

    return correct_with_gemini(default, "city")


def normalize_finnish_player_data(player_data):
    """
    Apply all Finnish text corrections to a player record.

    Args:
        player_data: Dict from NHL API with firstName, lastName, birthCity

    Returns:
        Corrected player data dict (modified in place)
    """
    # Only apply to Finnish players
    if player_data.get("birthCountry") != "FIN":
        return player_data

    # Correct first name
    if 'firstName' in player_data and isinstance(player_data['firstName'], dict):
        original = player_data['firstName'].get('default', '')
        corrected = correct_finnish_name(player_data['firstName'])
        if original != corrected:
            print(f"  Name correction: {original} → {corrected}")
        player_data['firstName']['default'] = corrected

    # Correct last name
    if 'lastName' in player_data and isinstance(player_data['lastName'], dict):
        original = player_data['lastName'].get('default', '')
        corrected = correct_finnish_name(player_data['lastName'])
        if original != corrected:
            print(f"  Name correction: {original} → {corrected}")
        player_data['lastName']['default'] = corrected

    # Recalculate full name
    first = player_data.get('firstName', {}).get('default', '')
    last = player_data.get('lastName', {}).get('default', '')
    player_data['name'] = f"{first} {last}".strip()

    # Correct birth city
    if 'birthCity' in player_data and isinstance(player_data['birthCity'], dict):
        original = player_data['birthCity'].get('default', '')
        corrected = correct_finnish_city(player_data['birthCity'])
        if original != corrected:
            print(f"  City correction: {original} → {corrected}")
        player_data['birthCity']['default'] = corrected

        # Update birthplace string
        country = player_data.get('birthCountry', '')
        player_data['birthplace'] = f"{corrected}, {country}"

    return player_data


def get_cache_stats():
    """Return cache statistics for debugging."""
    return {
        "entries": len(_correction_cache),
        "keys": list(_correction_cache.keys())
    }
