# Legacy realtime monitor

This directory contains a standalone monitor, state manager and systemd artifacts. It is distinct from the active GitHub Actions collector, [realtime_poll.py](../../realtime_poll.py).

The production site is static GitHub Pages and does not use this directory's systemd deployment path. Use [Deployment](../../../../docs/DEPLOYMENT.md) for current production operations and [Data pipeline](../../../../docs/DATA_PIPELINE.md) for collection commands.

These legacy tools are not part of the normal setup or default test suite. Inspect their source and local configuration before experimenting; do not assume old service-install commands describe the current site.
