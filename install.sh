#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BINARY_PATH="$SCRIPT_DIR/dist/imgur_migrate/imgur_migrate"

# Build the binary if it does not exist yet.
if [ ! -f "$BINARY_PATH" ]; then
	echo "No built binary found at $BINARY_PATH"
	if command -v pyinstaller >/dev/null 2>&1; then
		echo "Building binary with pyinstaller..."
		(cd "$SCRIPT_DIR" && pyinstaller imgur_migrate.py)
	else
		echo "Error: pyinstaller is not installed, cannot build binary."
		echo "Install pyinstaller or run ci.sh from the repository root."
		exit 1
	fi
fi

if [ ! -f "$BINARY_PATH" ]; then
	echo "Error: install failed because binary was not created at $BINARY_PATH"
	exit 1
fi

sudo ln -sf "$BINARY_PATH" /usr/local/bin/imgur-migrate
echo "Installed imgur-migrate -> $BINARY_PATH"