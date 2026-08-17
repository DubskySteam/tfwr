# TFWR Dashboard

Live, high-throughput web dashboard for [The Farmer Was Replaced](https://store.steampowered.com/app/2060160/).

The game writes every `print()` / `quick_print()` to its `output.txt` (the in-game
output window truncates, the file does not). This repo tails that file, parses it into
structured telemetry, and serves a live dashboard over Server-Sent Events — no
dependencies, stdlib only.

## Components

- `tailer.py` — high-throughput tailer. Reads only the bytes *appended* since the last
  poll via `os.pread` at a tracked offset, so cost is O(new bytes) regardless of file
  size. Handles truncation/rewrites.
- `parser.py` — streaming parser. Two structured line kinds:
  - `TEL k v k v ...` — resource snapshot
  - `EVT name k v ...` — named event
  Everything else is kept as raw log (error/warning lines are flagged and counted).
- `server.py` — stdlib HTTP server + SSE. Endpoints: `/` (dashboard),
  `/state` (snapshot JSON), `/events` (SSE), `/metrics` (Prometheus text), `/health`.
- `dashboard.html` — the UI: resource cards with sparklines + rates, a selectable line
  chart, live output log, event feed, and save-state panel.

## Sending data from the game

`telemetry.py` (repo root, auto-linked into the save folder by `sync.sh`) provides:

```python
from telemetry import *

report()        # quick_prints current stock of every resource as a TEL line
emit("name", "key", value)   # quick_prints an EVT line
```

Call `report()` periodically from your farm (e.g. once per loop or per phase) and
`emit(...)` on interesting events (unlock bought, treasure found, phase switch).

## Run

```sh
python3 dashboard/server.py                # live game
python3 dashboard/server.py --demo         # synthetic feed (no game needed)
python3 dashboard/server.py --port 9000 --output /path/to/output.txt --save /path/to/save.json
```

Then open http://127.0.0.1:8787

High-rate streams (thousands of lines/sec) are fine: the tailer only reads deltas and
the dashboard coalesces renders.