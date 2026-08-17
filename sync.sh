#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SAVE="${TFWR_SAVE:-$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/Saves/Save0}"

if [ ! -d "$SAVE" ]; then
  echo "Save folder not found: $SAVE" >&2
  echo "Set TFWR_SAVE to the correct Saves/<name> folder." >&2
  exit 1
fi

for f in "$SAVE"/*.py; do
  name="$(basename "$f")"
  ln -sf "$f" "$REPO/$name"
  echo "linked $REPO/$name -> $f"
done

for f in "$REPO"/*.py; do
  name="$(basename "$f")"
  [ "$name" = "__builtins__.py" ] && continue
  [ -L "$f" ] && continue
  [ -e "$SAVE/$name" ] && continue
  cp "$f" "$SAVE/$name"
  ln -sf "$SAVE/$name" "$f"
  echo "imported $name into save folder"
done