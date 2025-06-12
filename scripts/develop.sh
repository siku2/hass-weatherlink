#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Create config dir if not present
if [[ ! -d "${PWD}/config" ]]; then
    mkdir -p "${PWD}/config"
    hass --config "${PWD}/config" --script ensure_config
fi

# Home Assistant will use 'import custom_components' to load custom components
export PYTHONPATH="${PYTHONPATH:-}:${PWD}"

# Start Home Assistant
hass --config "${PWD}/config" --debug
