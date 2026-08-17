# The Farmer Was Replaced — but by whom?

## What's in here

- **`solutions/`** — polished, shareable "look how far we've come" scripts.
  - `solutions/multidrones/` — the aspirational section.
- **`sync.sh`** — bridges the repo to the game's save folder via symlinks, so edits
  reach the game and the game's save-loads reach us.
- **`__builtins__.py`** — the game's API, mirrored for pyright.

## Usage

1. Install the game (The Farmer Was Replaced).
2. Run `./sync.sh` to teleport code from the save folder into this working repo
3. Paste scripts from /solutions into the according files and run them ingame using import and function calls
4. Watch the farmer do absolutely nothing while the code farms.
