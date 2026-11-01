# Published data

This directory is served by the static application and copied into production builds. [Data pipeline](../../docs/DATA_PIPELINE.md#ownership-and-outputs) documents ownership and refresh commands; [Player data](../../docs/PLAYER_DATA.md) documents roster/game schemas.

Primary datasets include daily snapshots under `prepopulated/games/`, the master roster under `players/`, season statistics under `player-stats/`, plus the games manifest, standings, upcoming Finnish games, verified news and prospect inputs/caches.

Treat collection timestamps and source state as evidence of freshness. Fixed file/player totals are not configuration. Preserve good snapshots on upstream failure, regenerate the date manifest after dated-file changes, and publish the complete intended data revision.

Research exports, backups and debugging captures are not authoritative homepage inputs. Review repository ignore rules before adding generated artifacts.
