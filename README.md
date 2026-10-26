# Devloop Project Starter

A ready-to-use template recognized and monitored by [Devloop](https://github.com/rachid-log/devloop).

## What is Included

- `.watched.json`: Default configuration for the Devloop Observer agent.
- `.gitignore`: Common sensible defaults for Python, TypeScript, Node, and web projects.

## Setup Instructions

1. Edit `.watched.json` to configure your project:
   - `goal`: What the Devloop observer agent should prioritize.
   - `domain`: `BL` (Business Logic), `UX/UI`, `SEO`, or `Security`.
   - `watch_freq`: Scan frequency (e.g. `1h`, `4h`, `1d`).
   - `active`: Set to `true` to enable automated audits.

2. Run devloop:
   ```bash
   devloop status
   devloop observe
   ```
