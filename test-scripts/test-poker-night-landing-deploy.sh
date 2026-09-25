#!/usr/bin/env bash

# Builds a disposable Poker-Night.org landing page, smoke-tests it locally, and
# optionally deploys and verifies the same image on AI-M1 over SSH.
set -euo pipefail

readonly IMAGE_NAME="${POKER_NIGHT_LANDING_IMAGE:-poker-night-org-landing-smoke:latest}"
readonly LOCAL_CONTAINER_NAME="${POKER_NIGHT_LANDING_LOCAL_CONTAINER:-poker-night-org-landing-local-smoke}"
readonly REMOTE_CONTAINER_NAME="${POKER_NIGHT_LANDING_REMOTE_CONTAINER:-poker-night-ux}"
readonly REMOTE_SSH_HOST="${AI_M1_SSH_HOST:-aiserver@AI-M1.local}"
readonly REMOTE_DOCKER_COMMAND="${AI_M1_DOCKER_COMMAND:-/Applications/Docker.app/Contents/Resources/bin/docker}"
readonly REMOTE_DOCKER_CONTEXT="${AI_M1_DOCKER_CONTEXT:-desktop-linux}"
readonly REMOTE_NETWORK="${POKER_NIGHT_LANDING_REMOTE_NETWORK:-proxy}"
readonly REMOTE_PORT="${POKER_NIGHT_LANDING_REMOTE_PORT:-8080}"
readonly REMOTE_WORKDIR="${POKER_NIGHT_LANDING_REMOTE_WORKDIR:-/tmp/poker-night-org-landing-smoke}"
readonly PUBLIC_URL="${POKER_NIGHT_LANDING_PUBLIC_URL:-https://poker-night.org}"

deploy_remote=false
build_dir=''

usage() {
  cat <<'EOF'
Usage: test-poker-night-landing-deploy.sh [--remote]

Builds and verifies a temporary Poker-Night.org landing-page container on localhost.
Pass --remote to copy the generated Docker context to AI-M1, build it remotely,
run it on the host loopback interface, and verify the landing page over SSH.

Environment overrides:
  AI_M1_SSH_HOST                         SSH target (default: aiserver@AI-M1.local)
  AI_M1_DOCKER_COMMAND                   Docker CLI on AI-M1
  AI_M1_DOCKER_CONTEXT                   Docker context on AI-M1 (default: desktop-linux)
  POKER_NIGHT_LANDING_IMAGE              Docker image tag
  POKER_NIGHT_LANDING_REMOTE_NETWORK     AI-M1 Docker network (default: proxy)
  POKER_NIGHT_LANDING_REMOTE_PORT        Remote loopback port (default: 8080)
  POKER_NIGHT_LANDING_REMOTE_CONTAINER   Remote container name
  POKER_NIGHT_LANDING_REMOTE_WORKDIR     Temporary remote build directory
  POKER_NIGHT_LANDING_PUBLIC_URL          Public URL (default: https://poker-night.org)
EOF
}

cleanup() {
  docker rm --force "$LOCAL_CONTAINER_NAME" >/dev/null 2>&1 || true
  [[ -z "$build_dir" ]] || rm -rf "$build_dir"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "$1 is required." >&2
    exit 1
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      deploy_remote=true
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
  shift
done

require_command docker
require_command curl
if [[ "$deploy_remote" == true ]]; then
  require_command ssh
  require_command tar
fi

if ! docker info >/dev/null 2>&1; then
  echo 'Docker is not running or is not accessible.' >&2
  exit 1
fi

trap cleanup EXIT
build_dir=$(mktemp -d)

cat >"$build_dir/Dockerfile" <<'EOF'
FROM nginx:1.27-alpine
COPY default.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
EOF

cat >"$build_dir/default.conf" <<'EOF'
server {
  listen 8080;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;
}
EOF

cat >"$build_dir/index.html" <<'EOF'
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Poker-Night.org</title></head>
  <body><main><h1>Poker-Night.org</h1><p>Landing page smoke test passed.</p></main></body>
</html>
EOF

docker build --tag "$IMAGE_NAME" "$build_dir" >/dev/null
docker rm --force "$LOCAL_CONTAINER_NAME" >/dev/null 2>&1 || true
docker run --detach --rm --name "$LOCAL_CONTAINER_NAME" \
  --publish 127.0.0.1::8080 "$IMAGE_NAME" >/dev/null

local_port=$(docker port "$LOCAL_CONTAINER_NAME" 8080/tcp | sed -E 's/.*:([0-9]+)$/\1/')
local_response=$(curl --fail --silent --show-error --retry 10 --retry-connrefused \
  "http://127.0.0.1:${local_port}/")
if [[ "$local_response" != *'Poker-Night.org'* ]]; then
  echo 'Local landing page did not return the expected content.' >&2
  exit 1
fi
printf 'Local landing page verified at http://127.0.0.1:%s/\n' "$local_port"

if [[ "$deploy_remote" == false ]]; then
  echo 'Remote deployment skipped. Re-run with --remote to deploy to AI-M1.'
  exit 0
fi

tar -C "$build_dir" -cf - Dockerfile default.conf index.html |
  ssh "$REMOTE_SSH_HOST" "set -eu; export PATH='/Applications/Docker.app/Contents/Resources/bin:'\"\$PATH\"; rm -rf '$REMOTE_WORKDIR'; mkdir -p '$REMOTE_WORKDIR/docker-config'; cp -R \"\$HOME/.docker/contexts\" '$REMOTE_WORKDIR/docker-config/contexts'; printf '{\"currentContext\":\"%s\"}\\n' '$REMOTE_DOCKER_CONTEXT' > '$REMOTE_WORKDIR/docker-config/config.json'; tar -xf - -C '$REMOTE_WORKDIR'; DOCKER_CONFIG='$REMOTE_WORKDIR/docker-config' '$REMOTE_DOCKER_COMMAND' build --tag '$IMAGE_NAME' '$REMOTE_WORKDIR'; '$REMOTE_DOCKER_COMMAND' rm --force '$REMOTE_CONTAINER_NAME' >/dev/null 2>&1 || true; '$REMOTE_DOCKER_COMMAND' run --detach --name '$REMOTE_CONTAINER_NAME' --restart unless-stopped --network '$REMOTE_NETWORK' --network-alias '$REMOTE_CONTAINER_NAME' --publish '127.0.0.1:${REMOTE_PORT}:8080' '$IMAGE_NAME' >/dev/null"

remote_response=$(ssh "$REMOTE_SSH_HOST" "curl --fail --silent --show-error --retry 10 --retry-connrefused http://127.0.0.1:${REMOTE_PORT}/")
if [[ "$remote_response" != *'Poker-Night.org'* ]]; then
  echo 'Remote landing page did not return the expected content.' >&2
  exit 1
fi

printf 'Remote landing page deployed and verified on %s at 127.0.0.1:%s.\n' \
  "$REMOTE_SSH_HOST" "$REMOTE_PORT"

public_response=$(curl --fail --silent --show-error --location --retry 10 --retry-all-errors \
  "$PUBLIC_URL")
if [[ "$public_response" != *'Poker-Night.org'* ]]; then
  echo "Public landing page at ${PUBLIC_URL} did not return the expected content." >&2
  exit 1
fi
printf 'Public landing page verified at %s.\n' "$PUBLIC_URL"