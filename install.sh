#!/usr/bin/env bash
set -euo pipefail
kit_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${CANNBOT_PYTHON:-python3}" "$kit_root/scripts/install.py" "$@"
