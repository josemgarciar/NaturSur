#!/usr/bin/env bash
# Development startup helper
# Runs migrations, seeds offerings, then starts the dev server

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# If there is a .venv in the project, activate it for the script
if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
	# shellcheck disable=SC1091
	source "$ROOT_DIR/.venv/bin/activate"
	echo "[*] Activated virtualenv at $ROOT_DIR/.venv"
fi

echo "[*] Applying migrations..."
python3 manage.py migrate

echo "[*] Seeding offerings..."
# Run the seeder under manage.py shell so project root is on sys.path
python3 manage.py shell < scripts/seed_offerings.py

HOSTPORT=${1:-"127.0.0.1:8000"}
echo "[*] Starting development server at http://$HOSTPORT/"
exec python3 manage.py runserver "$HOSTPORT"
