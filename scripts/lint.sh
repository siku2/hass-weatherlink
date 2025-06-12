#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

ruff check . --fix
ruff format
