#!/usr/bin/env bash
set -euo pipefail
PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
command -v python3 >/dev/null || { printf '%s\n' 'Python 3.10+ is required.' >&2; exit 1; }
command -v git >/dev/null || { printf '%s\n' 'Git is required.' >&2; exit 1; }
exec python3 "$PACKAGE_ROOT/installer/install.py" "$@"