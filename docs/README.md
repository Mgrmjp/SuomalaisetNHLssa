# Documentation

These guides describe the current checkout. Each topic has one primary guide; source files linked from a guide define the actual behavior.

| I want to… | Read |
| --- | --- |
| Run the app or contribute a change | [Development](DEVELOPMENT.md) |
| Configure keys and local overrides | [Configuration](CONFIGURATION.md) |
| Understand routes, stores and build boundaries | [Architecture](ARCHITECTURE.md) |
| Refresh results, roster, schedules or prospects | [Data pipeline](DATA_PIPELINE.md) |
| Understand game and roster records | [Player data](PLAYER_DATA.md) |
| Understand news selection and expiry | [News](DAILY_NEWS.md) |
| Understand standings collection and ordering | [Standings](STANDINGS.md) |
| Trace Finnish name correction | [Name correction](NAME_CORRECTION.md) |
| Publish or investigate a stale deployment | [Deployment](DEPLOYMENT.md) |
| Choose validation commands | [Testing](TESTING.md) |
| Change layouts, components or accessibility behavior | [UI conventions](UI.md) |

## Maintaining these guides

- Update the relevant guide when code, commands, workflows or public section availability change.
- Link to implementation instead of copying entire components or configuration files into documentation.
- Do not record fixed player counts, speculative performance metrics or claims that a provider is always working.
- Put new tests under the locations listed in the testing guide. Do not invent npm commands, endpoints or deployment platforms.
- Keep old implementation history in Git. Removed migration plans and fix-completion reports are not setup instructions.
- Run `npm run docs:check`. It checks local Markdown links, heading anchors, inline source paths and npm script names. It cannot determine whether every prose claim still matches the implementation.

Script-directory READMEs point back to these guides. Player/editorial articles and font licensing files are outside this documentation set.
