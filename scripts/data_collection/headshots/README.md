# Headshot tools

The daily Finnish fetcher calls [sync.py](sync.py) for players without a local WebP. That module writes player-ID `.webp` files under `static/headshots/`. Pillow is required for conversion; background removal is optional. Missing image dependencies do not prevent the results snapshot itself from being collected.

Other tools here handle thumbnails, cropping and prospect image synchronization. The frontend's actual candidate/fallback order is in [playerHeadshots.js](../../../src/lib/utils/playerHeadshots.js) and [PlayerHeadshot](../../../src/lib/components/ui/PlayerHeadshot.svelte). Do not assume every old thumbnail format is the primary UI asset.

Use [Development](../../../docs/DEVELOPMENT.md) for environment setup and [Data pipeline](../../../docs/DATA_PIPELINE.md) for the normal collection path. Avoid publishing fixed headshot counts or download-speed estimates as current status.
