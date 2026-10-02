#!/bin/bash

# Hook the LCARS screensaver into Omarchy by shadowing omarchy-launch-screensaver
# from a directory that sits ahead of Omarchy's own bin on PATH.
# Usage: install.sh [uninstall]

set -e

DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
BIN="$HOME/.local/bin/omarchy-lcars-override"
ENV_FILE="$HOME/.config/environment.d/61-omarchy-lcars-override.conf"
UWSM_FILE="$HOME/.config/uwsm/env.d/61-omarchy-lcars-override"

if [[ $1 == "uninstall" ]]; then
  rm -f "$BIN/omarchy-launch-screensaver" "$ENV_FILE" "$UWSM_FILE"
  rmdir "$BIN" 2>/dev/null || true
  echo "LCARS screensaver removed. Log out and back in to finish."
  exit 0
fi

mkdir -p "$BIN" "$(dirname "$ENV_FILE")" "$(dirname "$UWSM_FILE")"
ln -sf "$DIR/omarchy-launch-screensaver" "$BIN/omarchy-launch-screensaver"
echo 'PATH=%h/.local/bin/omarchy-lcars-override:${PATH}' >"$ENV_FILE"
echo 'export PATH="$HOME/.local/bin/omarchy-lcars-override:$PATH"' >"$UWSM_FILE"

echo "LCARS screensaver installed. Log out and back in so idle picks it up."
echo "Try it now with: $BIN/omarchy-launch-screensaver force"
