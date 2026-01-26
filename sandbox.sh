#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG=${IMAGE_TAG:-brutus-sandbox:local}

usage() {
  cat <<'EOF'
Usage:
  ./sandbox.sh build         Build the sandbox image
  ./sandbox.sh check         Run compile+ruff+tests in a no-network container (default)
  ./sandbox.sh cmd "..."     Run an arbitrary command in the sandbox (no network)

Environment:
  IMAGE_TAG=...              Override docker image tag (default: brutus-sandbox:local)
EOF
}

build() {
  docker build -f Dockerfile.sandbox -t "$IMAGE_TAG" .
}

run() {
  docker run --rm \
    --network=none \
    --cap-drop=ALL \
    --security-opt=no-new-privileges \
    "$IMAGE_TAG" \
    "$@"
}

subcmd=${1:-check}

case "$subcmd" in
  build)
    build
    ;;
  check)
    build
    run "python -m compileall -q src brutus && ruff check . && ruff format . --check && python -m unittest -q && brutus --help >/dev/null"
    ;;
  cmd)
    shift || true
    if [[ $# -eq 0 ]]; then
      usage
      exit 2
    fi
    build
    run "$@"
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage
    exit 2
    ;;
esac
