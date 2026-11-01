# Finnish name correction

[Documentation index](README.md)

Name correction exists in several collection and presentation paths. It is not solely a build-time operation or a planned future feature.

| Path | Implementation and behavior |
| --- | --- |
| Python collection | [finnish_text_utils.py](../scripts/data_collection/finnish/finnish_text_utils.py): manual overrides, persisted correction cache and optional OpenAI correction |
| Season-stat prebuild | [fetch-player-stats.cjs](../scripts/prebuild/fetch-player-stats.cjs): verified-spelling exceptions before optional OpenAI correction, with a deterministic fallback |
| Svelte/server presentation | [finnishNameUtils.js](../src/lib/utils/finnishNameUtils.js): cached lookup/pattern corrections through `correctFullName` |
| Hard-case player slugs | [player load](../src/routes/pelaajat/[slug]/+page.server.js): optional `correctFullNameWithLLM` fallback after deterministic slug matching |

On GitHub Pages the server-load path runs at build time; it does not create a production API server. The deterministic JavaScript helper can also run in browser-rendered components. The optional LLM helper is called with a server-private key, not a public browser setting.

`OPENAI_API_KEY` is optional for these correction paths. Without it, manual/cached/deterministic behavior remains available, with details differing by caller. Python collectors read exported environment variables. The Node prebuild scripts load local env files; see [Configuration](CONFIGURATION.md).

The verified spelling is **Matias Maccelli**, without an umlaut ([NHL profile](https://www.nhl.com/islanders/player/matias-maccelli-8481711/home)). The prebuild preserves `Maccelli` before calling OpenAI; presentation repairs the previously generated `Mäccelli`, including an incorrect LLM response.

Treat corrections conservatively: preserve player IDs and identity, do not turn every ASCII `a` into `ä`, and keep known valid spellings intact. Add specific overrides or representative fixtures rather than globally replacing letters. Do not promise that every source name needs correction.

[News](DAILY_NEWS.md) uses optional OpenAI translation separately; that is not player-name identification.
