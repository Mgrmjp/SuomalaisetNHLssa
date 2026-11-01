# League and prospect inputs

These collectors provide source-specific inputs for the Finnish prospect cache. They are separate from daily NHL game snapshots.

Use [Data pipeline](../../../docs/DATA_PIPELINE.md#supporting-datasets) for current entry points. The official-league, North American and Mestis inputs are collected by distinct commands; the application-ready cache is built afterward. Optional provider credentials are listed in [Configuration](../../../docs/CONFIGURATION.md).

Provider adapters, exploratory scrapers and demo generators coexist here. Do not treat every adapter as working production coverage or publish demo output as real data. A provider returning HTTP 403/429, empty data or a different season must not silently replace a valid application snapshot.

The public prospects section is currently disabled independently of collection. Check [features.js](../../../src/lib/config/features.js) before changing route availability.
